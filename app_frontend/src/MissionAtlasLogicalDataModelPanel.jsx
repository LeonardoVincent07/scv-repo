// C:\Dev\scv-repo\app_frontend\src\MissionAtlasLogicalDataModelPanel.jsx
import React, { useMemo, useState } from "react";
import physicalModel from "./data/physical_model_by_domain.json";

export default function MissionAtlasLogicalDataModelPanel() {
  const [selectedDomain, setSelectedDomain] = useState(
    physicalModel?.domains?.[0]?.domain || ""
  );
  const [selectedConceptFq, setSelectedConceptFq] = useState(null); // "public.clients"
  const [conceptQuery, setConceptQuery] = useState("");
  const [attributeQuery, setAttributeQuery] = useState("");

  const normalise = (s) => (s || "").toString().trim().toLowerCase();

  const pascalFromSnake = (s) =>
    (s || "")
      .split("_")
      .filter(Boolean)
      .map((x) => x.charAt(0).toUpperCase() + x.slice(1))
      .join("");

  const singularise = (name) => {
    // crude but effective for table names: clients -> Client, bundles -> Bundle
    const n = name || "";
    if (n.endsWith("sses")) return n; // addresses etc (rare)
    if (n.endsWith("ies")) return n.slice(0, -3) + "y";
    if (n.endsWith("ses")) return n.slice(0, -2); // cases -> case (rare)
    if (n.endsWith("s") && !n.endsWith("ss")) return n.slice(0, -1);
    return n;
  };

  const classifyConcept = (tableName) => {
    const t = (tableName || "").toLowerCase();
    if (t.includes("reference") || t === "country" || t === "asset_class") return "Reference";
    if (t.includes("run") || t.includes("event") || t.includes("log")) return "Operational event";
    if (t.includes("audit") || t.includes("validation") || t.includes("health_check")) return "Assurance signal";
    if (t.includes("evidence") || t.includes("artefact") || t.includes("bundle")) return "Evidence record";
    if (t.includes("lineage") || t.includes("dictionary") || t.includes("precedence")) return "Semantic control";
    if (t.includes("kyc") || t.includes("risk") || t.includes("flag")) return "Regulatory state";
    if (t.includes("cluster") || t.includes("match") || t.includes("decision")) return "Resolution state";
    if (t === "clients" || t.includes("client_")) return "Canonical state";
    if (t.includes("source") || t.includes("ingestion") || t.includes("raw")) return "Ingress state";
    return "Data entity";
  };

  const domains = useMemo(() => physicalModel?.domains || [], []);
  const selectedDomainObj = useMemo(() => {
    return domains.find((d) => d.domain === selectedDomain) || domains[0] || null;
  }, [domains, selectedDomain]);

  // Build fq map for relationships
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
    const inbound = new Map(); // fq -> [{fromFq, fromCols, toCols, fkName}]
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
    // Cross-domain dependencies derived from FKs
    const fqToDomain = new Map();
    for (const d of domains) {
      for (const t of d.tables || []) fqToDomain.set(`${t.schema}.${t.table}`, d.domain);
    }

    return domains.map((d) => {
      const tables = d.tables || [];
      const tableCount = tables.length;
      const colCount = tables.reduce((acc, t) => acc + (t.columns?.length || 0), 0);
      const fkCount = tables.reduce((acc, t) => acc + (t.foreign_keys?.length || 0), 0);

      const outboundRefs = new Map(); // refDomain -> count
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
        outboundRefs: [...outboundRefs.entries()]
          .map(([refDomain, count]) => ({ refDomain, count }))
          .sort((a, b) => b.count - a.count || a.refDomain.localeCompare(b.refDomain)),
      };
    });
  }, [domains]);

  const conceptsInSelectedDomain = useMemo(() => {
    const q = normalise(conceptQuery);
    const tables = selectedDomainObj?.tables || [];

    return tables
      .map((t) => {
        const fq = `${t.schema}.${t.table}`;
        const logicalName = pascalFromSnake(singularise(t.table));
        const conceptType = classifyConcept(t.table);

        // derive a "key surface" summary
        const pk = t.primary_key || [];
        const fks = t.foreign_keys || [];
        const inbound = inboundRefsByTable.get(fq) || [];

        return {
          fq,
          schema: t.schema,
          table: t.table,
          logicalName,
          conceptType,
          purposeHint: selectedDomainObj?.purpose || "",
          columns: t.columns || [],
          primary_key: pk,
          foreign_keys: fks,
          inbound_refs: inbound,
          colCount: t.columns?.length || 0,
          fkCount: fks.length,
          inboundCount: inbound.length,
        };
      })
      .filter((c) => {
        if (!q) return true;
        return (
          normalise(c.logicalName).includes(q) ||
          normalise(c.table).includes(q) ||
          normalise(c.conceptType).includes(q) ||
          normalise(c.fq).includes(q)
        );
      })
      .sort((a, b) => a.logicalName.localeCompare(b.logicalName));
  }, [selectedDomainObj, conceptQuery, inboundRefsByTable]);

  const selectedConcept = useMemo(() => {
    if (!selectedConceptFq) return null;
    return conceptsInSelectedDomain.find((c) => c.fq === selectedConceptFq) || null;
  }, [selectedConceptFq, conceptsInSelectedDomain]);

  // default concept selection
  if (!selectedConceptFq && conceptsInSelectedDomain.length) {
    setSelectedConceptFq(conceptsInSelectedDomain[0].fq);
  }

  const filteredAttributes = useMemo(() => {
    if (!selectedConcept) return [];
    const q = normalise(attributeQuery);

    return (selectedConcept.columns || [])
      .map((c) => ({
        name: c.name,
        type: c.type,
        nullable: c.nullable,
        default: c.default,
        pk: !!c.pk,
        fk: c.fk || null,
      }))
      .filter((a) => {
        if (!q) return true;
        return (
          normalise(a.name).includes(q) ||
          normalise(a.type).includes(q) ||
          (a.default ? normalise(a.default).includes(q) : false) ||
          (a.fk ? normalise(a.fk.references_table).includes(q) : false)
        );
      });
  }, [selectedConcept, attributeQuery]);

  const relationshipNarrative = (concept) => {
    if (!concept) return "";
    const outbound = concept.foreign_keys || [];
    const inbound = concept.inbound_refs || [];

    const parts = [];
    if (outbound.length) parts.push(`References ${outbound.length} upstream entity${outbound.length === 1 ? "" : "ies"}.`);
    if (inbound.length) parts.push(`Referenced by ${inbound.length} downstream entity${inbound.length === 1 ? "" : "ies"}.`);
    if (!outbound.length && !inbound.length) parts.push("No explicit FK relationships captured for this entity.");
    return parts.join(" ");
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h3 className="font-heading text-sm text-gray-900">Logical Data Model</h3>
            <p className="mt-1 text-xs font-body text-gray-600">
              A semantic view derived from the physical schema. Domains contain logical concepts mapped back to real tables and columns.
            </p>
          </div>

          <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
            tables: {physicalModel?.summary?.tables ?? "—"} • domains: {physicalModel?.summary?.domains ?? "—"} • fks:{" "}
            {physicalModel?.summary?.foreign_keys ?? "—"}
          </span>
        </div>
      </div>

      {/* Domain overview */}
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h4 className="font-heading text-sm text-gray-900">Platform domains</h4>
            <p className="mt-1 text-xs font-body text-gray-600">
              Select a domain to inspect its logical concepts and their mappings to physical entities.
            </p>
          </div>

          <select
            value={selectedDomain}
            onChange={(e) => {
              setSelectedDomain(e.target.value);
              setSelectedConceptFq(null);
              setConceptQuery("");
              setAttributeQuery("");
            }}
            className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white"
          >
            {domains.map((d) => (
              <option key={`ldm-dom-${d.domain}`} value={d.domain}>
                {d.domain}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-4 grid grid-cols-1 lg:grid-cols-4 gap-3">
          {domainSummaries.map((s) => {
            const active = s.domain === selectedDomain;
            return (
              <button
                key={`ldm-sum-${s.domain}`}
                type="button"
                onClick={() => {
                  setSelectedDomain(s.domain);
                  setSelectedConceptFq(null);
                  setConceptQuery("");
                  setAttributeQuery("");
                }}
                className={`text-left rounded-md border p-3 transition ${
                  active ? "bg-amber-50 border-amber-300 shadow" : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                }`}
              >
                <div className="font-heading text-sm text-gray-900">{s.domain}</div>
                <div className="mt-1 text-[11px] font-body text-gray-600 line-clamp-2">{s.purpose}</div>

                <div className="mt-3 grid grid-cols-3 gap-2">
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
                </div>

                {s.outboundRefs?.length ? (
                  <div className="mt-3">
                    <div className="text-[11px] font-body text-gray-600 mb-1">Cross-domain dependencies</div>
                    <div className="flex flex-wrap gap-2">
                      {s.outboundRefs.slice(0, 4).map((r) => (
                        <span
                          key={`ldm-od-${s.domain}-${r.refDomain}`}
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

      {/* Concept selector + inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Concept list */}
        <div className="rounded-halo border border-gray-200 bg-white p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h4 className="font-heading text-sm text-gray-900">Logical concepts</h4>
              <p className="mt-1 text-xs font-body text-gray-600">
                Concepts are derived from domain tables (1:1 mapping) and then enriched with semantics, keying and relationships.
              </p>
            </div>
            <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
              {conceptsInSelectedDomain.length}
            </span>
          </div>

          <input
            value={conceptQuery}
            onChange={(e) => setConceptQuery(e.target.value)}
            placeholder="Search concepts…"
            className="mt-3 w-full px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white"
          />

          <div className="mt-3 space-y-2 max-h-[520px] overflow-auto pr-1">
            {conceptsInSelectedDomain.map((c) => {
              const active = c.fq === selectedConceptFq;
              return (
                <button
                  key={`concept-${c.fq}`}
                  type="button"
                  onClick={() => setSelectedConceptFq(c.fq)}
                  className={`w-full text-left rounded-md border p-3 transition ${
                    active ? "bg-amber-50 border-amber-300 shadow" : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-heading text-sm text-gray-900">{c.logicalName}</div>
                      <div className="mt-1 text-[11px] font-mono text-gray-700">{c.fq}</div>
                      <div className="mt-1 text-[11px] font-body text-gray-600">
                        cols: {c.colCount} • outbound: {c.fkCount} • inbound: {c.inboundCount}
                      </div>
                    </div>

                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                      {c.conceptType}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Concept detail */}
        <div className="lg:col-span-2 rounded-halo border border-gray-200 bg-white p-4">
          {!selectedConcept ? (
            <div className="text-sm font-body text-gray-700">Select a concept to inspect.</div>
          ) : (
            <div className="space-y-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <h4 className="font-heading text-sm text-gray-900">{selectedConcept.logicalName}</h4>
                  <div className="mt-1 text-xs font-body text-gray-600">
                    <span className="font-mono">{selectedConcept.fq}</span> • {selectedConcept.conceptType}
                  </div>
                  <div className="mt-2 text-xs font-body text-gray-700">
                    <span className="text-gray-600">Domain intent:</span> {selectedConceptObjOrEmpty(selectedDomainObj)?.purpose || ""}
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-700">
                    PK: {selectedConcept.primary_key?.length ? selectedConcept.primary_key.join(", ") : "—"}
                  </span>
                  <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800">
                    outbound: {selectedConcept.fkCount}
                  </span>
                  <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-amber-50 border-amber-200 text-gray-800">
                    inbound: {selectedConcept.inboundCount}
                  </span>
                </div>
              </div>

              {/* Relationship narrative */}
              <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="text-xs font-body text-gray-600">Relationship surface</div>
                <div className="mt-1 text-xs font-body text-gray-800">{relationshipNarrative(selectedConcept)}</div>
              </div>

              {/* Relationships (Outbound / Inbound) */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                  <div className="font-heading text-sm text-gray-900">Outbound relationships</div>
                  <div className="mt-1 text-xs font-body text-gray-600">
                    Foreign keys expressed as logical references to upstream concepts.
                  </div>
                  <ul className="mt-2 list-disc pl-5 space-y-1">
                    {(selectedConcept.foreign_keys || []).length ? (
                      selectedConcept.foreign_keys.map((fk, idx) => {
                        const ref = tableByFq.get(fk.references_table);
                        const refLogical = ref ? pascalFromSnake(singularise(ref.table)) : fk.references_table;
                        const refDomain = ref?.platformDomain || "External/Unknown";
                        return (
                          <li key={`out-${idx}`} className="text-xs font-body text-gray-800">
                            <span className="font-mono">
                              {selectedConcept.logicalName}.{(fk.columns || []).join(", ")} → {refLogical}.
                              {(fk.references_columns || []).join(", ")}
                            </span>{" "}
                            <span className="text-gray-500">({refDomain})</span>
                          </li>
                        );
                      })
                    ) : (
                      <li className="text-xs font-body text-gray-600">None.</li>
                    )}
                  </ul>
                </div>

                <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                  <div className="font-heading text-sm text-gray-900">Inbound relationships</div>
                  <div className="mt-1 text-xs font-body text-gray-600">
                    Downstream concepts that reference this concept (reverse FK view).
                  </div>
                  <ul className="mt-2 list-disc pl-5 space-y-1">
                    {(selectedConcept.inbound_refs || []).length ? (
                      selectedConcept.inbound_refs.map((r, idx) => {
                        const from = tableByFq.get(r.fromFq);
                        const fromLogical = from ? pascalFromSnake(singularise(from.table)) : r.fromFq;
                        const fromDomain = from?.platformDomain || "External/Unknown";
                        return (
                          <li key={`in-${idx}`} className="text-xs font-body text-gray-800">
                            <span className="font-mono">
                              {fromLogical}.{(r.fromCols || []).join(", ")} → {selectedConcept.logicalName}.
                              {(r.toCols || []).join(", ")}
                            </span>{" "}
                            <span className="text-gray-500">({fromDomain})</span>
                          </li>
                        );
                      })
                    ) : (
                      <li className="text-xs font-body text-gray-600">None.</li>
                    )}
                  </ul>
                </div>
              </div>

              {/* Attributes */}
              <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-heading text-sm text-gray-900">Attributes</div>
                    <div className="mt-1 text-xs font-body text-gray-600">
                      Logical attributes mapped 1:1 to physical columns (type/null/default/keying).
                    </div>
                  </div>

                  <input
                    value={attributeQuery}
                    onChange={(e) => setAttributeQuery(e.target.value)}
                    placeholder="Search attributes…"
                    className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white min-w-[240px]"
                  />
                </div>

                <div className="mt-3 overflow-x-auto">
                  <table className="w-full text-xs bg-white rounded-md overflow-hidden border border-gray-200">
                    <thead className="bg-gray-50">
                      <tr className="text-left text-gray-600">
                        <th className="py-2 px-2">Attribute</th>
                        <th className="py-2 px-2">Type</th>
                        <th className="py-2 px-2">Null</th>
                        <th className="py-2 px-2">Default</th>
                        <th className="py-2 px-2">Keying</th>
                        <th className="py-2 px-2">Mapping</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredAttributes.map((a) => (
                        <tr key={`attr-${selectedConcept.fq}-${a.name}`} className="border-t">
                          <td className="py-2 px-2 font-mono text-gray-900">{a.name}</td>
                          <td className="py-2 px-2 text-gray-800">{a.type}</td>
                          <td className="py-2 px-2 text-gray-800">{a.nullable ? "YES" : "NO"}</td>
                          <td className="py-2 px-2 text-gray-800">{a.default || "—"}</td>
                          <td className="py-2 px-2">
                            <div className="flex flex-wrap gap-2">
                              {a.pk ? (
                                <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-amber-50 border-amber-200 text-gray-800">
                                  PK
                                </span>
                              ) : null}
                              {a.fk ? (
                                <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800">
                                  FK
                                </span>
                              ) : null}
                            </div>
                          </td>
                          <td className="py-2 px-2 text-gray-800">
                            <span className="font-mono text-[11px] text-gray-700">
                              {selectedConcept.fq}.{a.name}
                            </span>
                            {a.fk ? (
                              <div className="mt-1 text-[11px] font-mono text-gray-500">
                                → {a.fk.references_table}({(a.fk.references_columns || []).join(", ")})
                              </div>
                            ) : null}
                          </td>
                        </tr>
                      ))}
                      {!filteredAttributes.length ? (
                        <tr className="border-t">
                          <td className="py-3 px-2 text-xs font-body text-gray-600" colSpan={6}>
                            No attributes match the current filter.
                          </td>
                        </tr>
                      ) : null}
                    </tbody>
                  </table>
                </div>

                {/* Raw constraints (extra technical depth) */}
                <div className="mt-4 rounded-md border border-gray-200 bg-white p-3">
                  <div className="font-heading text-sm text-gray-900">Physical constraints (raw)</div>
                  <div className="mt-1 text-xs font-body text-gray-600">
                    Exposes CREATE TABLE constraint lines that define uniqueness, checks and key semantics.
                  </div>
                  {(tableByFq.get(selectedConcept.fq)?.create_constraints || []).length ? (
                    <div className="mt-2 space-y-2">
                      {(tableByFq.get(selectedConcept.fq)?.create_constraints || []).slice(0, 10).map((x, idx) => (
                        <div
                          key={`ldm-constraint-${idx}`}
                          className="text-[11px] font-mono rounded-md border border-gray-200 bg-gray-50 px-2 py-2 text-gray-700"
                        >
                          {x}
                        </div>
                      ))}
                      {(tableByFq.get(selectedConcept.fq)?.create_constraints || []).length > 10 ? (
                        <div className="text-xs font-body text-gray-600">Showing first 10 constraints.</div>
                      ) : null}
                    </div>
                  ) : (
                    <div className="mt-2 text-xs font-body text-gray-600">—</div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// tiny helper so we don’t explode if selectedDomainObj is null in render
function selectedConceptObjOrEmpty(obj) {
  return obj || { purpose: "" };
}


