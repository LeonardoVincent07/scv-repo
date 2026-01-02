import React, { useMemo, useState } from "react";
import physicalModel from "./data/physical_model_by_domain.json";

export default function MissionAtlasPhysicalDataModelPanel() {
  const normalise = (s) => (s || "").toString().trim().toLowerCase();

  const domains = useMemo(() => physicalModel?.domains || [], []);
  const [selectedDomain, setSelectedDomain] = useState(domains?.[0]?.domain || "");
  const [tableQuery, setTableQuery] = useState("");
  const [columnQuery, setColumnQuery] = useState("");
  const [selectedTableFq, setSelectedTableFq] = useState(null);
  const [showRawFkSql, setShowRawFkSql] = useState(false);

  const selectedDomainObj = useMemo(() => {
    return domains.find((d) => d.domain === selectedDomain) || domains[0] || null;
  }, [domains, selectedDomain]);

  const tableByFq = useMemo(() => {
    const m = new Map();
    for (const d of domains) {
      for (const t of d.tables || []) {
        const fq = `${t.schema}.${t.table}`;
        m.set(fq, { ...t, fq, platformDomain: d.domain, platformPurpose: d.purpose });
      }
    }
    return m;
  }, [domains]);

  const inboundRefsByTable = useMemo(() => {
    const inbound = new Map(); // fq -> [{fromFq, fromCols, toCols, fkName, raw}]
    for (const d of domains) {
      for (const t of d.tables || []) {
        const fromFq = `${t.schema}.${t.table}`;
        for (const fk of t.foreign_keys || []) {
          const toFq = fk.references_table;
          if (!inbound.has(toFq)) inbound.set(toFq, []);
          inbound.get(toFq).push({
            fromFq,
            fromCols: fk.columns || [],
            toCols: fk.references_columns || [],
            fkName: fk.name || null,
            raw: fk.raw || null,
          });
        }
      }
    }
    for (const [k, v] of inbound.entries()) {
      v.sort((a, b) => a.fromFq.localeCompare(b.fromFq));
      inbound.set(k, v);
    }
    return inbound;
  }, [domains]);

  const domainSummaries = useMemo(() => {
    const fqToDomain = new Map();
    for (const d of domains) {
      for (const t of d.tables || []) fqToDomain.set(`${t.schema}.${t.table}`, d.domain);
    }

    return domains.map((d) => {
      const tables = d.tables || [];
      const tableCount = tables.length;
      const colCount = tables.reduce((acc, t) => acc + (t.columns?.length || 0), 0);
      const fkCount = tables.reduce((acc, t) => acc + (t.foreign_keys?.length || 0), 0);
      const idxCount = tables.reduce((acc, t) => acc + (t.indexes?.length || 0), 0);

      const outboundRefs = new Map();
      for (const t of tables) {
        for (const fk of t.foreign_keys || []) {
          const refDom = fqToDomain.get(fk.references_table) || "External/Unknown";
          if (refDom === d.domain) continue;
          outboundRefs.set(refDom, (outboundRefs.get(refDom) || 0) + 1);
        }
      }

      return {
        domain: d.domain,
        purpose: d.purpose,
        tableCount,
        colCount,
        fkCount,
        idxCount,
        outboundRefs: [...outboundRefs.entries()]
          .map(([refDomain, count]) => ({ refDomain, count }))
          .sort((a, b) => b.count - a.count || a.refDomain.localeCompare(b.refDomain)),
      };
    });
  }, [domains]);

  const tablesInSelectedDomain = useMemo(() => {
    const q = normalise(tableQuery);
    const tables = selectedDomainObj?.tables || [];
    return tables
      .map((t) => {
        const fq = `${t.schema}.${t.table}`;
        const inbound = inboundRefsByTable.get(fq) || [];
        return {
          ...t,
          fq,
          colCount: t.columns?.length || 0,
          fkCount: t.foreign_keys?.length || 0,
          inboundCount: inbound.length,
          idxCount: t.indexes?.length || 0,
          constraintCount: t.create_constraints?.length || 0,
        };
      })
      .filter((t) => {
        if (!q) return true;
        return (
          normalise(t.fq).includes(q) ||
          normalise(t.table).includes(q) ||
          normalise(t.schema).includes(q)
        );
      })
      .sort((a, b) => a.table.localeCompare(b.table));
  }, [selectedDomainObj, tableQuery, inboundRefsByTable]);

  // Default table selection
  const selectedTable = useMemo(() => {
    if (!tablesInSelectedDomain.length) return null;
    if (!selectedTableFq) return tablesInSelectedDomain[0];
    return tablesInSelectedDomain.find((t) => t.fq === selectedTableFq) || tablesInSelectedDomain[0];
  }, [tablesInSelectedDomain, selectedTableFq]);

  const filteredColumns = useMemo(() => {
    if (!selectedTable) return [];
    const q = normalise(columnQuery);

    return (selectedTable.columns || [])
      .map((c) => ({
        name: c.name,
        type: c.type,
        nullable: c.nullable,
        default: c.default,
        unique: !!c.unique,
        pk: !!c.pk,
        fk: c.fk || null,
        raw: c.raw || null,
      }))
      .filter((c) => {
        if (!q) return true;
        return (
          normalise(c.name).includes(q) ||
          normalise(c.type).includes(q) ||
          (c.default ? normalise(c.default).includes(q) : false) ||
          (c.raw ? normalise(c.raw).includes(q) : false) ||
          (c.fk ? normalise(c.fk.references_table).includes(q) : false)
        );
      });
  }, [selectedTable, columnQuery]);

  const selectedInbound = useMemo(() => {
    if (!selectedTable) return [];
    return inboundRefsByTable.get(selectedTable.fq) || [];
  }, [selectedTable, inboundRefsByTable]);

  const ddlForTable = (t) => {
    if (!t) return "";
    const lines = [];
    lines.push(`CREATE TABLE ${t.schema}.${t.table} (`);
    const colLines = (t.columns || []).map((c) => {
      const parts = [];
      parts.push(`  ${c.name} ${c.type}`);
      if (!c.nullable) parts.push("NOT NULL");
      if (c.default !== null && c.default !== undefined && `${c.default}`.trim() !== "") {
        parts.push(`DEFAULT ${c.default}`);
      }
      return parts.join(" ");
    });

    const constraintLines = (t.create_constraints || []).map((x) => `  ${x.replace(/\s+/g, " ").trim()}`);
    const combined = [...colLines, ...constraintLines];

    for (let i = 0; i < combined.length; i++) {
      const suffix = i === combined.length - 1 ? "" : ",";
      lines.push(`${combined[i]}${suffix}`);
    }
    lines.push(");");

    // Indexes
    if ((t.indexes || []).length) {
      lines.push("");
      for (const ix of t.indexes) {
        const unique = ix.unique ? "UNIQUE " : "";
        const cols = (ix.columns || []).join(", ");
        const method = ix.method || "btree";
        lines.push(`CREATE ${unique}INDEX ${ix.name} ON ${t.schema}.${t.table} USING ${method} (${cols});`);
      }
    }

    // FKs (as ALTERs)
    if ((t.foreign_keys || []).length) {
      lines.push("");
      for (const fk of t.foreign_keys) {
        const cols = (fk.columns || []).join(", ");
        const refCols = (fk.references_columns || []).join(", ");
        lines.push(
          `ALTER TABLE ONLY ${t.schema}.${t.table} ADD CONSTRAINT ${fk.name} FOREIGN KEY (${cols}) REFERENCES ${fk.references_table} (${refCols});`
        );
      }
    }

    return lines.join("\n");
  };

  const tableStatsPill = (label, value) => (
    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
      {label}: {value}
    </span>
  );

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h3 className="font-heading text-sm text-gray-900">Physical Data Model</h3>
            <p className="mt-1 text-xs font-body text-gray-600">
              A schema inspector over the live physical model. Domains group tables; tables expose columns, keys, indexes and constraints.
            </p>
          </div>

          <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
            tables: {physicalModel?.summary?.tables ?? "—"} • domains: {physicalModel?.summary?.domains ?? "—"} • fks:{" "}
            {physicalModel?.summary?.foreign_keys ?? "—"} • idx: {physicalModel?.summary?.indexes ?? "—"}
          </span>
        </div>
      </div>

      {/* Domain overview */}
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h4 className="font-heading text-sm text-gray-900">Platform domains</h4>
            <p className="mt-1 text-xs font-body text-gray-600">
              Select a domain to inspect its tables and relationship surface, including cross-domain dependencies.
            </p>
          </div>

          <select
            value={selectedDomain}
            onChange={(e) => {
              setSelectedDomain(e.target.value);
              setSelectedTableFq(null);
              setTableQuery("");
              setColumnQuery("");
            }}
            className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white"
          >
            {domains.map((d) => (
              <option key={`pdm-dom-${d.domain}`} value={d.domain}>
                {d.domain}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-3 text-xs font-body text-gray-700">
          <span className="text-gray-600">Intent:</span> {selectedDomainObj?.purpose || "—"}
        </div>

        <div className="mt-4 grid grid-cols-1 lg:grid-cols-4 gap-3">
          {domainSummaries.map((s) => {
            const active = s.domain === selectedDomain;
            return (
              <button
                key={`pdm-sum-${s.domain}`}
                type="button"
                onClick={() => {
                  setSelectedDomain(s.domain);
                  setSelectedTableFq(null);
                  setTableQuery("");
                  setColumnQuery("");
                }}
                className={`text-left rounded-md border p-3 transition ${
                  active ? "bg-amber-50 border-amber-300 shadow" : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                }`}
              >
                <div className="font-heading text-sm text-gray-900">{s.domain}</div>
                <div className="mt-1 text-[11px] font-body text-gray-600 line-clamp-2">{s.purpose}</div>

                <div className="mt-3 grid grid-cols-2 gap-2">
                  <div className="rounded-md border border-gray-200 bg-white px-2 py-1">
                    <div className="text-[11px] font-body text-gray-600">Tables</div>
                    <div className="font-heading text-sm text-gray-900">{s.tableCount}</div>
                  </div>
                  <div className="rounded-md border border-gray-200 bg-white px-2 py-1">
                    <div className="text-[11px] font-body text-gray-600">Columns</div>
                    <div className="font-heading text-sm text-gray-900">{s.colCount}</div>
                  </div>
                  <div className="rounded-md border border-gray-200 bg-white px-2 py-1">
                    <div className="text-[11px] font-body text-gray-600">FKs</div>
                    <div className="font-heading text-sm text-gray-900">{s.fkCount}</div>
                  </div>
                  <div className="rounded-md border border-gray-200 bg-white px-2 py-1">
                    <div className="text-[11px] font-body text-gray-600">Indexes</div>
                    <div className="font-heading text-sm text-gray-900">{s.idxCount}</div>
                  </div>
                </div>

                {s.outboundRefs?.length ? (
                  <div className="mt-3">
                    <div className="text-[11px] font-body text-gray-600 mb-1">Cross-domain dependencies</div>
                    <div className="flex flex-wrap gap-2">
                      {s.outboundRefs.slice(0, 4).map((r) => (
                        <span
                          key={`pdm-od-${s.domain}-${r.refDomain}`}
                          className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700"
                        >
                          {r.refDomain}: {r.count}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tables list + Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Tables */}
        <div className="rounded-halo border border-gray-200 bg-white p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h4 className="font-heading text-sm text-gray-900">Tables</h4>
              <p className="mt-1 text-xs font-body text-gray-600">
                Filter tables within the selected domain. Click a table to inspect its schema surface.
              </p>
            </div>
            <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
              {tablesInSelectedDomain.length}
            </span>
          </div>

          <input
            value={tableQuery}
            onChange={(e) => setTableQuery(e.target.value)}
            placeholder="Search tables…"
            className="mt-3 w-full px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white"
          />

          <div className="mt-3 space-y-2 max-h-[560px] overflow-auto pr-1">
            {tablesInSelectedDomain.map((t) => {
              const active = selectedTable?.fq === t.fq;
              return (
                <button
                  key={`tbl-${t.fq}`}
                  type="button"
                  onClick={() => setSelectedTableFq(t.fq)}
                  className={`w-full text-left rounded-md border p-3 transition ${
                    active ? "bg-amber-50 border-amber-300 shadow" : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-mono text-sm text-gray-900">{t.fq}</div>
                      <div className="mt-1 text-[11px] font-body text-gray-600">
                        cols: {t.colCount} • outbound: {t.fkCount} • inbound: {t.inboundCount} • idx: {t.idxCount}
                      </div>
                    </div>
                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                      {t.primary_key?.length ? "PK" : "—"}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Inspector */}
        <div className="lg:col-span-2 rounded-halo border border-gray-200 bg-white p-4">
          {!selectedTable ? (
            <div className="text-sm font-body text-gray-700">Select a table to inspect.</div>
          ) : (
            <div className="space-y-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <h4 className="font-heading text-sm text-gray-900">{selectedTable.fq}</h4>
                  <p className="mt-1 text-xs font-body text-gray-600">
                    Columns, keys, indexes and constraints for the selected physical table.
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  {tableStatsPill("cols", selectedTable.colCount)}
                  {tableStatsPill("outbound", selectedTable.fkCount)}
                  {tableStatsPill("inbound", selectedTable.inboundCount)}
                  {tableStatsPill("idx", selectedTable.idxCount)}
                  {tableStatsPill("constraints", selectedTable.constraintCount)}
                </div>
              </div>

              {/* PK */}
              <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="text-xs font-body text-gray-600">Primary key</div>
                <div className="mt-1 text-xs font-mono text-gray-900">
                  {selectedTable.primary_key?.length ? selectedTable.primary_key.join(", ") : "—"}
                </div>
              </div>

              {/* Relationships */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                  <div className="font-heading text-sm text-gray-900">Outbound foreign keys</div>
                  <ul className="mt-2 list-disc pl-5 space-y-1">
                    {(selectedTable.foreign_keys || []).length ? (
                      selectedTable.foreign_keys.map((fk, idx) => (
                        <li key={`ofk-${idx}`} className="text-xs font-body text-gray-700">
                          <span className="font-mono">
                            ({(fk.columns || []).join(", ")}) → {fk.references_table}(
                            {(fk.references_columns || []).join(", ")})
                          </span>
                        </li>
                      ))
                    ) : (
                      <li className="text-xs font-body text-gray-600">None.</li>
                    )}
                  </ul>

                  {showRawFkSql && (selectedTable.foreign_keys || []).length ? (
                    <div className="mt-3 space-y-2">
                      {(selectedTable.foreign_keys || []).slice(0, 6).map((fk, idx) => (
                        <pre
                          key={`ofk-raw-${idx}`}
                          className="text-[11px] font-mono rounded-md border border-gray-200 bg-white p-3 overflow-auto text-gray-700"
                        >
                          {fk.raw || "(raw not available)"}
                        </pre>
                      ))}
                      {(selectedTable.foreign_keys || []).length > 6 ? (
                        <div className="text-xs font-body text-gray-600">Showing first 6 raw FK statements.</div>
                      ) : null}
                    </div>
                  ) : null}
                </div>

                <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                  <div className="font-heading text-sm text-gray-900">Inbound references</div>
                  <ul className="mt-2 list-disc pl-5 space-y-1">
                    {selectedInbound.length ? (
                      selectedInbound.map((r, idx) => (
                        <li key={`ifk-${idx}`} className="text-xs font-body text-gray-700">
                          <span className="font-mono">
                            {r.fromFq} ({(r.fromCols || []).join(", ")})
                          </span>
                        </li>
                      ))
                    ) : (
                      <li className="text-xs font-body text-gray-600">None.</li>
                    )}
                  </ul>
                </div>
              </div>

              {/* Indexes */}
              <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-heading text-sm text-gray-900">Indexes</div>
                    <div className="mt-1 text-xs font-body text-gray-600">Captured index definitions for lookup and uniqueness.</div>
                  </div>

                  <label className="flex items-center gap-2 text-xs font-body text-gray-700 select-none">
                    <input
                      type="checkbox"
                      checked={showRawFkSql}
                      onChange={(e) => setShowRawFkSql(e.target.checked)}
                    />
                    Show raw FK SQL
                  </label>
                </div>

                <ul className="mt-2 list-disc pl-5 space-y-1">
                  {(selectedTable.indexes || []).length ? (
                    selectedTable.indexes.map((ix, idx) => (
                      <li key={`ix-${idx}`} className="text-xs font-body text-gray-700">
                        <span className="font-mono">
                          {ix.unique ? "UNIQUE " : ""}
                          {ix.name} USING {ix.method} ({(ix.columns || []).join(", ")})
                        </span>
                      </li>
                    ))
                  ) : (
                    <li className="text-xs font-body text-gray-600">None captured.</li>
                  )}
                </ul>
              </div>

              {/* Columns */}
              <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-heading text-sm text-gray-900">Columns</div>
                    <div className="mt-1 text-xs font-body text-gray-600">
                      Physical column definitions with typing, nullability, defaults and key markings.
                    </div>
                  </div>

                  <input
                    value={columnQuery}
                    onChange={(e) => setColumnQuery(e.target.value)}
                    placeholder="Search columns…"
                    className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white min-w-[240px]"
                  />
                </div>

                <div className="mt-3 overflow-x-auto">
                  <table className="w-full text-xs bg-white rounded-md overflow-hidden border border-gray-200">
                    <thead className="bg-gray-50">
                      <tr className="text-left text-gray-600">
                        <th className="py-2 px-2">Column</th>
                        <th className="py-2 px-2">Type</th>
                        <th className="py-2 px-2">Null</th>
                        <th className="py-2 px-2">Default</th>
                        <th className="py-2 px-2">Keying</th>
                        <th className="py-2 px-2">Raw</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredColumns.map((c) => (
                        <tr key={`col-${selectedTable.fq}-${c.name}`} className="border-t">
                          <td className="py-2 px-2 font-mono text-gray-900">{c.name}</td>
                          <td className="py-2 px-2 text-gray-800">{c.type}</td>
                          <td className="py-2 px-2 text-gray-800">{c.nullable ? "YES" : "NO"}</td>
                          <td className="py-2 px-2 text-gray-800">{c.default || "—"}</td>
                          <td className="py-2 px-2">
                            <div className="flex flex-wrap gap-2">
                              {c.pk ? (
                                <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-amber-50 border-amber-200 text-gray-800">
                                  PK
                                </span>
                              ) : null}
                              {c.fk ? (
                                <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800">
                                  FK → {c.fk.references_table}(
                                  {(c.fk.references_columns || []).join(", ")})
                                </span>
                              ) : null}
                              {c.unique ? (
                                <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-800">
                                  UNIQUE
                                </span>
                              ) : null}
                            </div>
                          </td>
                          <td className="py-2 px-2 text-gray-700">
                            <span className="font-mono text-[11px]">{c.raw || "—"}</span>
                          </td>
                          <td className="py-2 px-2 text-gray-700">
                            <span className="font-mono text-[11px]">{c.raw || "—"}</span>
                          </td>
                        </tr>
                      ))}
                      {!filteredColumns.length ? (
                        <tr className="border-t">
                          <td className="py-3 px-2 text-xs font-body text-gray-600" colSpan={7}>
                            No columns match the current filter.
                          </td>
                        </tr>
                      ) : null}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Constraints */}
              <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="font-heading text-sm text-gray-900">Constraints</div>
                <div className="mt-1 text-xs font-body text-gray-600">
                  Raw constraint lines captured from CREATE TABLE for uniqueness, checks and PK semantics.
                </div>

                {(selectedTable.create_constraints || []).length ? (
                  <div className="mt-2 space-y-2">
                    {(selectedTable.create_constraints || []).slice(0, 14).map((x, idx) => (
                      <div
                        key={`con-${idx}`}
                        className="text-[11px] font-mono rounded-md border border-gray-200 bg-white px-2 py-2 text-gray-700"
                      >
                        {x}
                      </div>
                    ))}
                    {(selectedTable.create_constraints || []).length > 14 ? (
                      <div className="text-xs font-body text-gray-600">Showing first 14 constraints.</div>
                    ) : null}
                  </div>
                ) : (
                  <div className="mt-2 text-xs font-body text-gray-600">—</div>
                )}
              </div>

              {/* Generated DDL */}
              <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="font-heading text-sm text-gray-900">Generated DDL (from model)</div>
                <div className="mt-1 text-xs font-body text-gray-600">
                  Derived CREATE TABLE + CREATE INDEX + FK ALTER statements for the selected table.
                </div>
                <pre className="mt-3 text-[11px] font-mono rounded-md border border-gray-200 bg-white p-3 overflow-auto text-gray-700">
                  {ddlForTable(selectedTable)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
