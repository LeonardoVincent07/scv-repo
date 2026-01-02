import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "docs" / "mission_destination" / "initial_database_schema.txt"
OUTPUT_PATH = REPO_ROOT / "app_frontend" / "src" / "data" / "initial_physical_data_model.json"


# ----------------------------
# 1) SQL DDL parsing (optional)
# ----------------------------
CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>[^\s(]+)\s*\((?P<body>.*?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)
LINE_SPLIT_RE = re.compile(r",\s*(?![^()]*\))")  # split on commas not inside parentheses


def _normalise_table_name(raw: str) -> str:
    s = raw.strip().strip('"')
    s = s.replace('".\"', ".").replace('"."', ".").replace('."', ".")
    s = s.replace('"', "")
    return s


def _parse_column_def(line: str):
    parts = line.strip().split()
    if len(parts) < 2:
        return None

    col = parts[0].strip('"')
    constraint_keywords = {
        "not", "null", "default", "primary", "unique", "references", "check", "constraint", "generated", "collate"
    }

    type_tokens = []
    i = 1
    while i < len(parts):
        token = parts[i].lower()
        if token in constraint_keywords:
            break
        type_tokens.append(parts[i])
        i += 1

    col_type = " ".join(type_tokens).strip()
    rest = " ".join(parts[i:]).strip()

    nullable = True
    if re.search(r"\bNOT\s+NULL\b", rest, re.IGNORECASE):
        nullable = False

    default = None
    m = re.search(
        r"\bDEFAULT\b\s+(.+?)(?:\s+\bNOT\b\s+\bNULL\b|\s+\bNULL\b|\s+\bPRIMARY\b|\s+\bUNIQUE\b|\s+\bREFERENCES\b|$)",
        rest,
        re.IGNORECASE,
    )
    if m:
        default = m.group(1).strip()

    is_pk_inline = bool(re.search(r"\bPRIMARY\s+KEY\b", rest, re.IGNORECASE))
    is_unique_inline = bool(re.search(r"\bUNIQUE\b", rest, re.IGNORECASE))

    fk = None
    m = re.search(r"\bREFERENCES\b\s+([^\s(]+)\s*\(([^)]+)\)", rest, re.IGNORECASE)
    if m:
        fk = {
            "references_table": _normalise_table_name(m.group(1)),
            "references_columns": [c.strip().strip('"') for c in m.group(2).split(",")],
        }

    return {
        "name": col,
        "type": col_type or parts[1],
        "nullable": nullable,
        "default": default,
        "pk": is_pk_inline,
        "unique": is_unique_inline,
        "fk": fk,
        "raw": line.strip(),
    }


def _parse_table_body(body: str):
    items = [x.strip() for x in LINE_SPLIT_RE.split(body.strip()) if x.strip()]
    columns = []
    constraints = []

    for item in items:
        if re.match(r"^(CONSTRAINT|PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|CHECK)\b", item, re.IGNORECASE):
            constraints.append(item)
            continue
        col = _parse_column_def(item)
        if col:
            columns.append(col)
        else:
            constraints.append(item)

    pk_cols = set()
    for c in constraints:
        m = re.search(r"PRIMARY\s+KEY\s*\(([^)]+)\)", c, re.IGNORECASE)
        if m:
            pk_cols |= {x.strip().strip('"') for x in m.group(1).split(",")}

    for col in columns:
        if col["name"] in pk_cols:
            col["pk"] = True

    fks = []
    for c in constraints:
        m = re.search(
            r"FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+([^\s(]+)\s*\(([^)]+)\)",
            c,
            re.IGNORECASE,
        )
        if m:
            fks.append(
                {
                    "columns": [x.strip().strip('"') for x in m.group(1).split(",")],
                    "references_table": _normalise_table_name(m.group(2)),
                    "references_columns": [x.strip().strip('"') for x in m.group(3).split(",")],
                    "raw": c.strip(),
                }
            )

    return columns, constraints, fks


def _extract_tables_from_sql(text: str):
    tables = []
    for m in CREATE_TABLE_RE.finditer(text):
        raw_name = m.group("name")
        body = m.group("body")
        table_name = _normalise_table_name(raw_name)
        columns, constraints, fks = _parse_table_body(body)
        tables.append(
            {
                "table": table_name,
                "columns": columns,
                "constraints": constraints,
                "foreign_keys": fks,
            }
        )
    return tables


# --------------------------------
# 2) Markdown schema parsing (yours)
# --------------------------------
MD_TABLE_RE = re.compile(r"^###\s+\d+(?:\.\d+)*\s+`(?P<table>[^`]+)`\s*$", re.MULTILINE)

MD_SECTION_PK_RE = re.compile(r"^\*\*Primary key\*\*\s*$", re.MULTILINE)
MD_SECTION_FK_RE = re.compile(r"^\*\*Foreign keys\*\*\s*$", re.MULTILINE)
MD_SECTION_KEYS_RE = re.compile(r"^\*\*Key columns\*\*\s*$", re.MULTILINE)

MD_BULLET_COL_RE = re.compile(r"^\s*-\s*`(?P<col>[^`]+)`\s*$", re.MULTILINE)
MD_BULLET_FK_RE = re.compile(
    r"^\s*-\s*`(?P<col>[^`]+)`\s*[→-]\s*`(?P<ref_table>[^`.]+)\.(?P<ref_col>[^`]+)`\s*$",
    re.MULTILINE,
)


def _slice_block(text: str, start_idx: int, end_idx: int) -> str:
    return text[start_idx:end_idx].strip()


def _extract_tables_from_markdown(text: str):
    matches = list(MD_TABLE_RE.finditer(text))
    if not matches:
        return []

    tables = []
    for i, m in enumerate(matches):
        table_name = m.group("table").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = _slice_block(text, start, end)

        # PK
        pk_cols = set()
        pk_pos = MD_SECTION_PK_RE.search(block)
        if pk_pos:
            # take bullets after PK heading until blank line or next heading
            pk_block = block[pk_pos.end():]
            for b in MD_BULLET_COL_RE.finditer(pk_block):
                pk_cols.add(b.group("col").strip())

        # FK
        fks = []
        fk_pos = MD_SECTION_FK_RE.search(block)
        if fk_pos:
            fk_block = block[fk_pos.end():]
            for fkm in MD_BULLET_FK_RE.finditer(fk_block):
                col = fkm.group("col").strip()
                ref_table = fkm.group("ref_table").strip()
                ref_col = fkm.group("ref_col").strip()
                fks.append(
                    {
                        "columns": [col],
                        "references_table": ref_table,
                        "references_columns": [ref_col],
                        "raw": f"`{col}` -> `{ref_table}.{ref_col}`",
                    }
                )

        fk_map = {}
        for fk in fks:
            if fk["columns"]:
                fk_map[fk["columns"][0]] = {
                    "references_table": fk["references_table"],
                    "references_columns": fk["references_columns"],
                }

        # Key columns
        key_cols = []
        keys_pos = MD_SECTION_KEYS_RE.search(block)
        if keys_pos:
            keys_block = block[keys_pos.end():]
            for b in MD_BULLET_COL_RE.finditer(keys_block):
                key_cols.append(b.group("col").strip())

        # Build columns (minimal deterministic)
        cols = []
        seen = set()
        for c in key_cols:
            if c in seen:
                continue
            seen.add(c)
            cols.append(
                {
                    "name": c,
                    "type": "unknown",
                    "nullable": None,
                    "default": None,
                    "pk": c in pk_cols,
                    "unique": False,
                    "fk": fk_map.get(c),
                    "raw": c,
                }
            )

        tables.append(
            {
                "table": table_name,
                "columns": cols,
                "constraints": [],
                "foreign_keys": fks,
            }
        )

    return tables


def main():
    if not INPUT_PATH.exists():
        raise SystemExit(f"Input schema file not found: {INPUT_PATH}")

    text = INPUT_PATH.read_text(encoding="utf-8", errors="ignore")

    # Prefer real SQL if present
    tables = _extract_tables_from_sql(text)
    if not tables:
        # Fallback to MissionDestination markdown structure
        tables = _extract_tables_from_markdown(text)

    artefact = {
        "artifact_type": "physical_data_model",
        "artifact_version": "1.0",
        "source": {
            "authority": "MissionDestination",
            "derived_from": "docs/mission_destination/initial_database_schema.txt",
        },
        "tables": sorted(tables, key=lambda t: t["table"]),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(artefact, indent=2), encoding="utf-8")
    print(f"Wrote: {OUTPUT_PATH}")
    print(f"Tables: {len(artefact['tables'])}")


if __name__ == "__main__":
    main()

