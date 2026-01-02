#!/usr/bin/env python3
"""
Generate a high-density Physical Data Model artefact from a Postgres schema SQL dump.

Outputs:
  app_frontend/src/data/physical_model_by_domain.json

Inputs:
  - database_schema12.sql (or any SQL file)
  - platform_domains.json (domain taxonomy, table assignments)

This generator is deterministic and grounded in the schema.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# Regexes (Postgres-ish)
# -----------------------------

CREATE_TABLE_RE = re.compile(
    r"""
    CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?
    (?P<name>(?:"[^"]+"|\w+)(?:\.(?:"[^"]+"|\w+))?)      # schema.table or table
    \s*\(
      (?P<body>.*?)
    \)
    \s*;
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

ALTER_ADD_CONSTRAINT_RE = re.compile(
    r"""
    ALTER\s+TABLE\s+ONLY\s+(?P<table>(?:"[^"]+"|\w+)(?:\.(?:"[^"]+"|\w+))?)
    \s+ADD\s+CONSTRAINT\s+(?P<constraint>(?:"[^"]+"|\w+))
    \s+(?P<kind>PRIMARY\s+KEY|FOREIGN\s+KEY)
    \s*\((?P<cols>[^)]+)\)
    (?:
      \s+REFERENCES\s+(?P<ref_table>(?:"[^"]+"|\w+)(?:\.(?:"[^"]+"|\w+))?)
      \s*\((?P<ref_cols>[^)]+)\)
    )?
    \s*;
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

# Inline FK inside column definition: col type REFERENCES table(col)
INLINE_FK_RE = re.compile(
    r"""
    REFERENCES\s+(?P<ref_table>(?:"[^"]+"|\w+)(?:\.(?:"[^"]+"|\w+))?)
    \s*\((?P<ref_cols>[^)]+)\)
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Table-level FK constraint in CREATE TABLE body:
TABLE_FK_RE = re.compile(
    r"""
    (?:CONSTRAINT\s+(?P<cname>(?:"[^"]+"|\w+))\s+)?
    FOREIGN\s+KEY\s*\((?P<cols>[^)]+)\)
    \s+REFERENCES\s+(?P<ref_table>(?:"[^"]+"|\w+)(?:\.(?:"[^"]+"|\w+))?)
    \s*\((?P<ref_cols>[^)]+)\)
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

# Table-level PK constraint in CREATE TABLE body:
TABLE_PK_RE = re.compile(
    r"""
    (?:CONSTRAINT\s+(?P<cname>(?:"[^"]+"|\w+))\s+)?
    PRIMARY\s+KEY\s*\((?P<cols>[^)]+)\)
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

# CREATE [UNIQUE] INDEX name ON schema.table USING btree (col1, col2)
CREATE_INDEX_RE = re.compile(
    r"""
    CREATE\s+(?P<unique>UNIQUE\s+)?INDEX\s+(?P<name>(?:"[^"]+"|\w+))
    \s+ON\s+(?P<table>(?:"[^"]+"|\w+)(?:\.(?:"[^"]+"|\w+))?)
    (?:\s+USING\s+(?P<method>\w+))?
    \s*\((?P<cols>[^)]+)\)
    \s*;
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

# Split on commas not inside parentheses (good enough for most DDL dumps)
COMMA_SPLIT_RE = re.compile(r",\s*(?![^()]*\))")


def unquote_ident(s: str) -> str:
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s


def parse_qualified_name(raw: str) -> Tuple[str, str]:
    """
    Returns (schema, table). If schema missing, defaults to 'public'.
    Handles quoted identifiers.
    """
    raw = raw.strip()
    if "." in raw:
        left, right = raw.split(".", 1)
        return unquote_ident(left), unquote_ident(right)
    return "public", unquote_ident(raw)


def split_ident_list(raw: str) -> List[str]:
    return [unquote_ident(x.strip()) for x in raw.split(",") if x.strip()]


@dataclass
class FKRef:
    references_table: str
    references_columns: List[str]


@dataclass
class Column:
    name: str
    type: str
    nullable: Optional[bool]
    default: Optional[str]
    unique: bool
    pk: bool
    fk: Optional[FKRef]
    raw: str


@dataclass
class Index:
    name: str
    unique: bool
    method: str
    columns: List[str]


@dataclass
class ForeignKey:
    name: Optional[str]
    columns: List[str]
    references_table: str
    references_columns: List[str]
    raw: str


@dataclass
class TableModel:
    schema: str
    table: str
    columns: List[Column]
    primary_key: List[str]
    foreign_keys: List[ForeignKey]
    indexes: List[Index]
    create_constraints: List[str]


def parse_column_def(line: str) -> Optional[Column]:
    """
    Very tolerant column parser:
      col_name col_type [constraints...]
    """
    raw = line.strip()
    if not raw:
        return None

    # Skip constraints lines
    if re.match(r"^(CONSTRAINT|PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|CHECK)\b", raw, re.IGNORECASE):
        return None

    # Tokenize by whitespace, but keep type tokens until we hit constraint keywords
    parts = raw.split()
    if len(parts) < 2:
        return None

    col_name = unquote_ident(parts[0])

    constraint_keywords = {"not", "null", "default", "primary", "unique", "references", "check", "constraint"}
    type_tokens: List[str] = []
    i = 1
    while i < len(parts):
        if parts[i].lower() in constraint_keywords:
            break
        type_tokens.append(parts[i])
        i += 1
    col_type = " ".join(type_tokens).strip() or parts[1]

    rest = " ".join(parts[i:]).strip()

    # nullable (None if unknown, but we can usually infer)
    nullable: Optional[bool] = True
    if re.search(r"\bNOT\s+NULL\b", rest, re.IGNORECASE):
        nullable = False

    # default
    default = None
    m = re.search(r"\bDEFAULT\b\s+(.+?)(?=\s+\bNOT\b\s+\bNULL\b|\s+\bNULL\b|\s+\bPRIMARY\b|\s+\bUNIQUE\b|\s+\bREFERENCES\b|$)", rest, re.IGNORECASE)
    if m:
        default = m.group(1).strip().rstrip(",")

    unique = bool(re.search(r"\bUNIQUE\b", rest, re.IGNORECASE))
    pk = bool(re.search(r"\bPRIMARY\s+KEY\b", rest, re.IGNORECASE))

    fk = None
    m = INLINE_FK_RE.search(rest)
    if m:
        ref_schema, ref_table = parse_qualified_name(m.group("ref_table"))
        fk = FKRef(
            references_table=f"{ref_schema}.{ref_table}",
            references_columns=split_ident_list(m.group("ref_cols")),
        )

    return Column(
        name=col_name,
        type=col_type,
        nullable=nullable,
        default=default,
        unique=unique,
        pk=pk,
        fk=fk,
        raw=raw,
    )


def parse_create_table_body(body: str) -> Tuple[List[Column], List[str], List[str], List[ForeignKey]]:
    """
    Returns:
      columns, constraints_raw, pk_cols, fks
    """
    items = [x.strip() for x in COMMA_SPLIT_RE.split(body.strip()) if x.strip()]
    columns: List[Column] = []
    constraints_raw: List[str] = []

    # First pass: columns + raw constraints lines
    for item in items:
        col = parse_column_def(item)
        if col:
            columns.append(col)
        else:
            constraints_raw.append(item)

    # Table-level PK columns
    pk_cols: List[str] = []
    for c in constraints_raw:
        m = TABLE_PK_RE.search(c)
        if m:
            pk_cols = split_ident_list(m.group("cols"))
            break

    # Mark pk cols on columns
    if pk_cols:
        pk_set = set(pk_cols)
        for col in columns:
            if col.name in pk_set:
                col.pk = True

    # Table-level FKs
    fks: List[ForeignKey] = []
    for c in constraints_raw:
        m = TABLE_FK_RE.search(c)
        if not m:
            continue
        cname = m.group("cname")
        cols = split_ident_list(m.group("cols"))
        ref_schema, ref_table = parse_qualified_name(m.group("ref_table"))
        ref_cols = split_ident_list(m.group("ref_cols"))
        fks.append(
            ForeignKey(
                name=unquote_ident(cname) if cname else None,
                columns=cols,
                references_table=f"{ref_schema}.{ref_table}",
                references_columns=ref_cols,
                raw=c.strip(),
            )
        )

        # Mark inline on participating columns too
        fk_ref = FKRef(references_table=f"{ref_schema}.{ref_table}", references_columns=ref_cols)
        for col in columns:
            if col.name in set(cols) and col.fk is None:
                col.fk = fk_ref

    return columns, constraints_raw, pk_cols, fks


def load_platform_domains(path: Path) -> Dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    # Build table->domain mapping
    table_to_domain: Dict[str, str] = {}
    for d in obj.get("domains", []):
        dom = d.get("domain")
        for t in d.get("tables", []):
            table_to_domain[t] = dom
    return {"raw": obj, "table_to_domain": table_to_domain}


def infer_domain(table: str, table_to_domain: Dict[str, str]) -> str:
    """
    Domain assignment:
      1) explicit mapping from platform_domains.json (strongest)
      2) fallback heuristics (prefix / keywords)
      3) Unmapped
    """
    if table in table_to_domain:
        return table_to_domain[table]

    t = table.lower()
    if any(k in t for k in ["ingestion", "source_", "raw", "crm_", "trade_history", "transactions", "accounts"]):
        return "Ingestion"
    if any(k in t for k in ["cluster", "match_", "decision"]):
        return "Matching"
    if any(k in t for k in ["lineage", "dictionary", "precedence"]):
        return "Lineage & dictionary"
    if any(k in t for k in ["audit", "validation", "health", "error", "conflict"]):
        return "Assurance"
    if any(k in t for k in ["evidence"]):
        return "Evidence"
    if any(k in t for k in ["kyc", "risk", "regulatory"]):
        return "KYC & risk"
    if t in {"clients", "client_operational_state", "client_source_coverage"}:
        return "Client canonical"
    return "Unmapped"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sql",
        type=str,
        default="database_schema12.sql",
        help="Path to schema SQL dump (default: database_schema12.sql)",
    )
    parser.add_argument(
        "--domains",
        type=str,
        default="app_frontend/src/data/platform_domains.json",
        help="Path to platform_domains.json (default: app_frontend/src/data/platform_domains.json)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="app_frontend/src/data/physical_model_by_domain.json",
        help="Output JSON path (default: app_frontend/src/data/physical_model_by_domain.json)",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()

    sql_path = (repo_root / args.sql).resolve() if not Path(args.sql).is_absolute() else Path(args.sql)
    domains_path = (repo_root / args.domains).resolve() if not Path(args.domains).is_absolute() else Path(args.domains)
    out_path = (repo_root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)

    if not sql_path.exists():
        raise SystemExit(f"SQL file not found: {sql_path}")
    if not domains_path.exists():
        raise SystemExit(f"platform_domains.json not found: {domains_path}")

    domain_data = load_platform_domains(domains_path)
    table_to_domain: Dict[str, str] = domain_data["table_to_domain"]
    platform_domains_raw = domain_data["raw"]

    sql_text = sql_path.read_text(encoding="utf-8", errors="ignore")

    # Parse CREATE TABLE blocks
    tables: Dict[str, TableModel] = {}

    for m in CREATE_TABLE_RE.finditer(sql_text):
        schema, table = parse_qualified_name(m.group("name"))
        body = m.group("body")
        columns, constraints_raw, pk_cols, fks = parse_create_table_body(body)

        fq = f"{schema}.{table}"
        tables[fq] = TableModel(
            schema=schema,
            table=table,
            columns=columns,
            primary_key=pk_cols if pk_cols else [c.name for c in columns if c.pk],
            foreign_keys=fks,
            indexes=[],
            create_constraints=constraints_raw,
        )

    # Parse ALTER TABLE constraints (PK/FK)
    for m in ALTER_ADD_CONSTRAINT_RE.finditer(sql_text):
        schema, table = parse_qualified_name(m.group("table"))
        fq = f"{schema}.{table}"
        if fq not in tables:
            # Some dumps include alters for tables not in this file; skip safely
            continue

        kind = m.group("kind").strip().upper()
        cols = split_ident_list(m.group("cols"))
        cname = unquote_ident(m.group("constraint"))

        if kind.startswith("PRIMARY"):
            # Add PK columns
            pk_set = set(tables[fq].primary_key or [])
            pk_set |= set(cols)
            tables[fq].primary_key = list(pk_set)
            # Mark pk on columns
            for col in tables[fq].columns:
                if col.name in pk_set:
                    col.pk = True

        elif kind.startswith("FOREIGN"):
            ref_table_raw = m.group("ref_table")
            ref_cols_raw = m.group("ref_cols")
            if not ref_table_raw or not ref_cols_raw:
                continue
            ref_schema, ref_table = parse_qualified_name(ref_table_raw)
            ref_cols = split_ident_list(ref_cols_raw)

            fk = ForeignKey(
                name=cname,
                columns=cols,
                references_table=f"{ref_schema}.{ref_table}",
                references_columns=ref_cols,
                raw=m.group(0).strip(),
            )
            tables[fq].foreign_keys.append(fk)

            fk_ref = FKRef(references_table=f"{ref_schema}.{ref_table}", references_columns=ref_cols)
            for col in tables[fq].columns:
                if col.name in set(cols) and col.fk is None:
                    col.fk = fk_ref

    # Parse indexes
    for m in CREATE_INDEX_RE.finditer(sql_text):
        schema, table = parse_qualified_name(m.group("table"))
        fq = f"{schema}.{table}"
        if fq not in tables:
            continue

        cols_raw = m.group("cols")
        cols = [unquote_ident(x.strip()) for x in cols_raw.split(",") if x.strip()]
        method = (m.group("method") or "btree").lower()
        ix = Index(
            name=unquote_ident(m.group("name")),
            unique=bool(m.group("unique")),
            method=method,
            columns=cols,
        )
        tables[fq].indexes.append(ix)

    # Build domain -> tables (with full details)
    domain_to_tables: Dict[str, List[Dict[str, Any]]] = {}

    for fq, tm in tables.items():
        dom = infer_domain(tm.table, table_to_domain)
        domain_to_tables.setdefault(dom, []).append(
            {
                "schema": tm.schema,
                "table": tm.table,
                "columns": [
                    {
                        "name": c.name,
                        "type": c.type,
                        "nullable": c.nullable,
                        "default": c.default,
                        "unique": c.unique,
                        "pk": c.pk,
                        "fk": (asdict(c.fk) if c.fk else None),
                        "raw": c.raw,
                    }
                    for c in tm.columns
                ],
                "primary_key": tm.primary_key,
                "foreign_keys": [
                    {
                        "name": fk.name,
                        "columns": fk.columns,
                        "references_table": fk.references_table,
                        "references_columns": fk.references_columns,
                        "raw": fk.raw,
                    }
                    for fk in tm.foreign_keys
                ],
                "indexes": [asdict(ix) for ix in tm.indexes],
                "create_constraints": tm.create_constraints,
            }
        )

    # Compose final artefact in the order of platform_domains.json (plus Unmapped at end)
    domains_out: List[Dict[str, Any]] = []
    used_domains = set()

    for d in platform_domains_raw.get("domains", []):
        dom_name = d["domain"]
        used_domains.add(dom_name)
        domains_out.append(
            {
                "domain": dom_name,
                "purpose": d.get("purpose", ""),
                "tables": sorted(domain_to_tables.get(dom_name, []), key=lambda x: x["table"]),
            }
        )

    if "Unmapped" in domain_to_tables:
        domains_out.append(
            {
                "domain": "Unmapped",
                "purpose": "Tables not yet assigned to a platform domain.",
                "tables": sorted(domain_to_tables["Unmapped"], key=lambda x: x["table"]),
            }
        )

    artefact = {
        "artifact_type": "physical_model_by_domain",
        "artifact_version": "1.0",
        "source": {
            "authority": "Postgres schema dump",
            "derived_from": str(sql_path),
        },
        "domains": domains_out,
        "summary": {
            "tables": len(tables),
            "domains": len(domains_out),
            "foreign_keys": sum(len(t["foreign_keys"]) for dom in domains_out for t in dom["tables"]),
            "indexes": sum(len(t["indexes"]) for dom in domains_out for t in dom["tables"]),
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artefact, indent=2), encoding="utf-8")

    print(f"Wrote: {out_path}")
    print(json.dumps(artefact["summary"], indent=2))


if __name__ == "__main__":
    main()
