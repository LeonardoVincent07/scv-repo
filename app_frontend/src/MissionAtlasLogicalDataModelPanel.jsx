import React, { useMemo, useState } from "react";
import ldm from "./data/initial_logical_data_model.json";

export default function MissionAtlasLogicalDataModelPanel() {
  const [query, setQuery] = useState("");
  const [selectedEntityName, setSelectedEntityName] = useState(
    ldm?.entities?.[0]?.entity || ""
  );

  const normalise = (s) => (s || "").toString().trim().toLowerCase();

  const allEntities = useMemo(() => ldm?.entities || [], []);

  const modelStats = useMemo(() => {
    const entities = allEntities.length;
    const fields = allEntities.reduce((acc, e) => acc + ((e.fields || []).length), 0);
    const relationships = allEntities.reduce(
      (acc, e) => acc + ((e.relationships || []).length),
      0
    );
    return { entities, fields, relationships };
  }, [allEntities]);

  const classifyType = (t) => {
    const type = (t || "").toString();
    if (type.startsWith("Optional[")) return { label: "Optional", tone: "bg-gray-50 border-gray-200 text-gray-700" };
    if (type.startsWith("List[")) return { label: "List", tone: "bg-teal-50 border-teal-200 text-gray-800" };
    if (type.startsWith("Dict[")) return { label: "Dict", tone: "bg-amber-50 border-amber-200 text-gray-800" };
    return { label: "Scalar", tone: "bg-white border-gray-200 text-gray-700" };
  };

  const matchesEntity = (entity, q) => {
    if (!q) return true;
    const nq = normalise(q);
    if (normalise(entity.entity).includes(nq)) return true;
    if (normalise(entity.description).includes(nq)) return true;

    return (entity.fields || []).some((f) => {
      return (
        normalise(f.name).includes(nq) ||
        normalise(f.type).includes(nq) ||
        normalise(f.description).includes(nq)
      );
    });
  };

  const filteredEntities = useMemo(() => {
    return allEntities.filter((e) => matchesEntity(e, query));
  }, [allEntities, query]);

  // Keep selection valid as filters change
  const selectedEntity = useMemo(() => {
    const direct =
      filteredEntities.find((e) => e.entity === selectedEntityName) ||
      allEntities.find((e) => e.entity === selectedEntityName) ||
      filteredEntities[0] ||
      allEntities[0] ||
      null;

    if (direct && direct.entity !== selectedEntityName) {
      // Update selection if the prior selection disappeared
      // (safe setState pattern via microtask)
      queueMicrotask(() => setSelectedEntityName(direct.entity));
    }
    return direct;
  }, [allEntities, filteredEntities, selectedEntityName]);

  const selectedStats = useMemo(() => {
    if (!selectedEntity) return { fields: 0, relationships: 0 };
    return {
      fields: (selectedEntity.fields || []).length,
      relationships: (selectedEntity.relationships || []).length,
    };
  }, [selectedEntity]);

  return (
    <div className="space-y-4">
      {/* Authority header + KPIs */}
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h3 className="font-heading text-sm text-gray-900">Logical Data Model</h3>
            <p className="mt-1 text-xs font-body text-gray-600">
              Canonical business semantics derived from Mission Destination (machine-readable artefact).
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800">
                Authority: {ldm?.source?.authority || "—"}
              </span>
              <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-700">
                Version: {ldm?.artifact_version || "—"}
              </span>
              <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-700">
                Artefact: {ldm?.artifact_type || "—"}
              </span>
              {ldm?.source?.derived_from ? (
                <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                  Source: {ldm.source.derived_from}
                </span>
              ) : null}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2">
              <div className="text-[11px] font-body text-gray-600">Entities</div>
              <div className="font-heading text-sm text-gray-900">{modelStats.entities}</div>
            </div>
            <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2">
              <div className="text-[11px] font-body text-gray-600">Fields</div>
              <div className="font-heading text-sm text-gray-900">{modelStats.fields}</div>
            </div>
            <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2">
              <div className="text-[11px] font-body text-gray-600">Relationships</div>
              <div className="font-heading text-sm text-gray-900">{modelStats.relationships}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Two-pane catalogue + search */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left: entity navigator */}
        <div className="rounded-halo border border-gray-200 bg-white p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h4 className="font-heading text-sm text-gray-900">Entity Catalogue</h4>
              <p className="mt-1 text-xs font-body text-gray-600">
                Search by entity, field, type, or description.
              </p>
            </div>
            <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
              {filteredEntities.length} shown
            </span>
          </div>

          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search entities and fields…"
            className="mt-3 w-full px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white"
          />

          <div className="mt-3 space-y-2">
            {filteredEntities.length === 0 ? (
              <div className="text-xs font-body text-gray-600">No matches for that search.</div>
            ) : (
              filteredEntities.map((e) => {
                const active = selectedEntity?.entity === e.entity;
                const fCount = (e.fields || []).length;
                const rCount = (e.relationships || []).length;

                return (
                  <button
                    key={e.entity}
                    type="button"
                    onClick={() => setSelectedEntityName(e.entity)}
                    className={`w-full text-left rounded-md border p-3 transition ${
                      active
                        ? "bg-amber-50 border-amber-300 shadow"
                        : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-heading text-sm text-gray-900">{e.entity}</div>
                        <div className="mt-0.5 text-[11px] font-body text-gray-600 line-clamp-2">
                          {e.description || "—"}
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                          {fCount} field{fCount === 1 ? "" : "s"}
                        </span>
                        <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                          {rCount} rel{rCount === 1 ? "" : "s"}
                        </span>
                      </div>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right: selected entity detail */}
        <div className="lg:col-span-2 rounded-halo border border-gray-200 bg-white p-4">
          {selectedEntity ? (
            <>
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <h4 className="font-heading text-sm text-gray-900">{selectedEntity.entity}</h4>
                  <p className="mt-1 text-xs font-body text-gray-600">
                    {selectedEntity.description || "—"}
                  </p>

                  {(selectedEntity.relationships || []).length ? (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {(selectedEntity.relationships || []).map((r, idx) => (
                        <span
                          key={`${selectedEntity.entity}-rel-${idx}`}
                          className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800"
                        >
                          {r.type} → {r.to}
                          {r.via_field ? ` (${r.via_field})` : ""}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div className="mt-2 text-[11px] font-body text-gray-500">No relationships declared.</div>
                  )}
                </div>

                <div className="flex gap-2">
                  <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2">
                    <div className="text-[11px] font-body text-gray-600">Fields</div>
                    <div className="font-heading text-sm text-gray-900">{selectedStats.fields}</div>
                  </div>
                  <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2">
                    <div className="text-[11px] font-body text-gray-600">Relationships</div>
                    <div className="font-heading text-sm text-gray-900">{selectedStats.relationships}</div>
                  </div>
                </div>
              </div>

              <div className="mt-4 rounded-md border border-gray-200 bg-gray-50 p-3">
                <div className="text-xs font-body text-gray-600 mb-2">Fields</div>

                <table className="w-full text-xs bg-white rounded-md overflow-hidden border border-gray-200">
                  <thead className="bg-gray-50">
                    <tr className="text-left text-gray-600">
                      <th className="py-2 px-2">Field</th>
                      <th className="py-2 px-2">Type</th>
                      <th className="py-2 px-2">Kind</th>
                      <th className="py-2 px-2">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(selectedEntity.fields || []).map((f) => {
                      const kind = classifyType(f.type);
                      return (
                        <tr key={`${selectedEntity.entity}-${f.name}`} className="border-t">
                          <td className="py-2 px-2 font-mono text-gray-900">{f.name}</td>
                          <td className="py-2 px-2 text-gray-800">{f.type}</td>
                          <td className="py-2 px-2">
                            <span className={`text-[11px] font-mono rounded-md px-2 py-1 border ${kind.tone}`}>
                              {kind.label}
                            </span>
                          </td>
                          <td className="py-2 px-2 text-gray-800">{f.description || "—"}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* “Purpose” block (truthful, non-specific) */}
              <div className="mt-4 rounded-md border border-gray-200 bg-white p-4">
                <div className="font-heading text-sm text-gray-900">Why this matters</div>
                <ul className="mt-2 list-disc pl-5 space-y-1">
                  <li className="text-xs font-body text-gray-700">
                    Defines canonical business semantics for the SCV platform (what the system means, not just how it stores data).
                  </li>
                  <li className="text-xs font-body text-gray-700">
                    Used as the reference model for lineage and future controls (drift detection, integrity rules, self-healing).
                  </li>
                  <li className="text-xs font-body text-gray-700">
                    Enables consistent contracts across services by standardising entity and field intent.
                  </li>
                </ul>
              </div>
            </>
          ) : (
            <div className="text-xs font-body text-gray-600">No entity selected.</div>
          )}
        </div>
      </div>
    </div>
  );
}

