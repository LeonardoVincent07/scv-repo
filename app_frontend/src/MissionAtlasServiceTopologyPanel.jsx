import React, { useMemo, useState } from "react";

export default function MissionAtlasServiceTopologyPanel({ domains, services }) {
  // Service Topology UI state
  const [topologyMode, setTopologyMode] = useState("dependencies"); // "dependencies" | "catalogue"
  const [topologyDomainFilter, setTopologyDomainFilter] = useState("All");
  const [topologyQuery, setTopologyQuery] = useState("");

  // Dependency graph navigation state
  const [selectedEdge, setSelectedEdge] = useState(null); // { fromId, fromName, toId, toName, labels }
  const [focusEdgeServices, setFocusEdgeServices] = useState(true);

  // Service selection state (local to Service Topology)
  const [selectedService, setSelectedService] = useState(null);

  const normalise = (s) => (s || "").toString().trim().toLowerCase();

  const topologyDomainsList = useMemo(
    () => ["All", ...(domains || []).map((d) => d.name)],
    [domains]
  );

  const topologyFilteredServices = useMemo(() => {
    const q = normalise(topologyQuery);
    return (services || []).filter((svc) => {
      const domainOk =
        topologyDomainFilter === "All" || svc.domain === topologyDomainFilter;

      const qOk =
        !q ||
        normalise(svc.name).includes(q) ||
        normalise(svc.domain).includes(q) ||
        (svc.exposes || []).some((x) => normalise(x).includes(q)) ||
        (svc.consumes || []).some((x) => normalise(x).includes(q)) ||
        (svc.produces || []).some((x) => normalise(x).includes(q));

      return domainOk && qOk;
    });
  }, [services, topologyDomainFilter, topologyQuery]);

  const topologyDependencyEdges = useMemo(() => {
    const edges = [];
    for (const from of topologyFilteredServices) {
      for (const to of topologyFilteredServices) {
        if (from.id === to.id) continue;

        const fromProduces = new Set((from.produces || []).map((x) => x.trim()));
        const toConsumes = new Set((to.consumes || []).map((x) => x.trim()));
        const shared = [...fromProduces].filter((p) => toConsumes.has(p));

        if (shared.length) {
          edges.push({
            fromId: from.id,
            fromName: from.name,
            toId: to.id,
            toName: to.name,
            labels: shared,
          });
        }
      }
    }

    edges.sort((a, b) => {
      const k1 = `${a.fromName}→${a.toName}`;
      const k2 = `${b.fromName}→${b.toName}`;
      return k1.localeCompare(k2);
    });

    return edges;
  }, [topologyFilteredServices]);

  const topologyServiceById = useMemo(() => {
    const m = new Map();
    for (const s of topologyFilteredServices) m.set(s.id, s);
    return m;
  }, [topologyFilteredServices]);

  const topologyServicesForList = useMemo(() => {
    if (!selectedEdge || !focusEdgeServices) return topologyFilteredServices;
    const ids = new Set([selectedEdge.fromId, selectedEdge.toId]);
    return topologyFilteredServices.filter((s) => ids.has(s.id));
  }, [topologyFilteredServices, selectedEdge, focusEdgeServices]);

  const selectedEdgeFrom = useMemo(() => {
    if (!selectedEdge) return null;
    return (services || []).find((s) => s.id === selectedEdge.fromId) || null;
  }, [services, selectedEdge]);

  const selectedEdgeTo = useMemo(() => {
    if (!selectedEdge) return null;
    return (services || []).find((s) => s.id === selectedEdge.toId) || null;
  }, [services, selectedEdge]);

  const clearSelectedEdge = () => {
    setSelectedEdge(null);
    setFocusEdgeServices(true);
  };

  return (
    <div className="space-y-4">
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h3 className="font-heading text-sm text-gray-900">Microservices Architecture</h3>
            <p className="mt-1 text-xs font-body text-gray-600">
              A live view of domains, services, contracts and inter-service dependencies across the platform.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setTopologyMode("dependencies")}
                className={`px-3 py-2 rounded-md text-sm font-body border ${
                  topologyMode === "dependencies"
                    ? "border-halo-primary bg-teal-50 text-gray-900"
                    : "border-gray-200 bg-white hover:bg-gray-50 text-gray-700"
                }`}
              >
                Dependencies
              </button>
              <button
                type="button"
                onClick={() => setTopologyMode("catalogue")}
                className={`px-3 py-2 rounded-md text-sm font-body border ${
                  topologyMode === "catalogue"
                    ? "border-halo-primary bg-teal-50 text-gray-900"
                    : "border-gray-200 bg-white hover:bg-gray-50 text-gray-700"
                }`}
              >
                Catalogue
              </button>
            </div>

            <select
              value={topologyDomainFilter}
              onChange={(e) => setTopologyDomainFilter(e.target.value)}
              className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white"
            >
              {topologyDomainsList.map((d) => (
                <option key={`dom-${d}`} value={d}>
                  {d}
                </option>
              ))}
            </select>

            <input
              value={topologyQuery}
              onChange={(e) => setTopologyQuery(e.target.value)}
              placeholder="Search services, contracts, tokens…"
              className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white min-w-[240px]"
            />
          </div>
        </div>
      </div>

      {topologyMode === "dependencies" ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-halo border border-gray-200 bg-gray-50 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="font-heading text-sm text-gray-900">Dependency Graph</h4>
                <p className="mt-1 text-xs font-body text-gray-600">
                  Derived from producer/consumer relationships (Produces → Consumes). Click a dependency to inspect it.
                </p>
              </div>

              {selectedEdge ? (
                <button
                  type="button"
                  onClick={clearSelectedEdge}
                  className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white hover:bg-gray-50 text-gray-700"
                >
                  Clear
                </button>
              ) : null}
            </div>

            {topologyDependencyEdges.length === 0 ? (
              <div className="mt-4 text-xs font-body text-gray-700">
                No dependencies found for the current filters.
              </div>
            ) : (
              <div className="mt-4 space-y-2">
                {topologyDependencyEdges.map((e, idx) => {
                  const isSelected =
                    selectedEdge &&
                    selectedEdge.fromId === e.fromId &&
                    selectedEdge.toId === e.toId;

                  return (
                    <button
                      key={`edge-${idx}`}
                      type="button"
                      onClick={() => {
                        setSelectedEdge(e);
                        setFocusEdgeServices(true);

                        // Default to consumer, because that's the dependent party
                        const consumer = (services || []).find((s) => s.id === e.toId) || null;
                        setSelectedService(consumer);
                      }}
                      className={`w-full text-left rounded-md border p-3 transition ${
                        isSelected
                          ? "bg-amber-50 border-amber-300 shadow"
                          : "bg-white border-gray-200 hover:bg-gray-50"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="text-sm font-body text-gray-900">
                          <span className="font-heading">{e.fromName}</span>{" "}
                          <span className="text-gray-500">→</span>{" "}
                          <span className="font-heading">{e.toName}</span>
                        </div>
                        <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
                          {e.labels.length} link{e.labels.length === 1 ? "" : "s"}
                        </span>
                      </div>

                      <div className="mt-2 flex flex-wrap gap-2">
                        {e.labels.map((lbl) => (
                          <span
                            key={`${e.fromId}-${e.toId}-${lbl}`}
                            className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800"
                          >
                            {lbl}
                          </span>
                        ))}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <div className="rounded-halo border border-gray-200 bg-gray-50 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="font-heading text-sm text-gray-900">Selected Service</h4>
                <p className="mt-1 text-xs font-body text-gray-600">
                  Click a service below to view its contracts.
                </p>
              </div>

              {selectedEdge ? (
                <label className="flex items-center gap-2 text-xs font-body text-gray-700 select-none">
                  <input
                    type="checkbox"
                    checked={focusEdgeServices}
                    onChange={(e) => setFocusEdgeServices(e.target.checked)}
                  />
                  Focus edge services
                </label>
              ) : null}
            </div>

            {selectedEdge ? (
              <div className="mt-4 rounded-md border border-gray-200 bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-heading text-sm text-gray-900">Edge Details</div>
                    <div className="mt-1 text-xs font-body text-gray-600">
                      <span className="font-heading">{selectedEdge.fromName}</span>{" "}
                      <span className="text-gray-500">→</span>{" "}
                      <span className="font-heading">{selectedEdge.toName}</span>
                    </div>
                  </div>
                  <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
                    Producer → Consumer
                  </span>
                </div>

                <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                    <div className="text-xs font-body text-gray-600">Producer</div>
                    <div className="font-heading text-sm text-gray-900">
                      {selectedEdgeFrom?.name || selectedEdge.fromName}
                    </div>
                    <div className="text-[11px] font-body text-gray-500">
                      Domain: {selectedEdgeFrom?.domain || "—"}
                    </div>
                  </div>

                  <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                    <div className="text-xs font-body text-gray-600">Consumer</div>
                    <div className="font-heading text-sm text-gray-900">
                      {selectedEdgeTo?.name || selectedEdge.toName}
                    </div>
                    <div className="text-[11px] font-body text-gray-500">
                      Domain: {selectedEdgeTo?.domain || "—"}
                    </div>
                  </div>
                </div>

                <div className="mt-3">
                  <div className="text-xs font-body text-gray-600 mb-1">Link contracts</div>
                  <div className="flex flex-wrap gap-2">
                    {selectedEdge.labels.map((lbl) => (
                      <span
                        key={`edge-lbl-${lbl}`}
                        className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800"
                      >
                        {lbl}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}

            <div className="mt-4 grid grid-cols-1 gap-2">
              {topologyServicesForList.map((svc) => {
                const active = selectedService?.id === svc.id;
                return (
                  <button
                    type="button"
                    key={`svcbtn-${svc.id}`}
                    onClick={() => setSelectedService(active ? null : svc)}
                    className={`text-left rounded-md border p-3 transition ${
                      active
                        ? "bg-amber-50 border-amber-300 shadow"
                        : "bg-white border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-heading text-sm text-gray-900">{svc.name}</div>
                        <div className="text-[11px] font-body text-gray-500">
                          Domain: {svc.domain}
                        </div>
                      </div>
                      <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
                        {svc.exposes?.length ? "API" : "Internal"}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            {selectedService && topologyServiceById.has(selectedService.id) ? (
              <div className="mt-4 rounded-md border border-gray-200 bg-white p-4">
                <div className="font-heading text-sm text-gray-900">{selectedService.name}</div>

                <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <div className="text-xs font-body text-gray-600 mb-1">Consumes</div>
                    {(selectedService.consumes || []).length ? (
                      <ul className="list-disc pl-4 space-y-1">
                        {selectedService.consumes.map((x) => (
                          <li key={`${selectedService.id}-c-${x}`} className="text-xs font-body text-gray-800">
                            {x}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="text-xs font-body text-gray-500">—</div>
                    )}
                  </div>

                  <div>
                    <div className="text-xs font-body text-gray-600 mb-1">Produces</div>
                    {(selectedService.produces || []).length ? (
                      <ul className="list-disc pl-4 space-y-1">
                        {selectedService.produces.map((x) => (
                          <li key={`${selectedService.id}-p-${x}`} className="text-xs font-body text-gray-800">
                            {x}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="text-xs font-body text-gray-500">—</div>
                    )}
                  </div>

                  <div>
                    <div className="text-xs font-body text-gray-600 mb-1">Exposes</div>
                    {(selectedService.exposes || []).length ? (
                      <ul className="list-disc pl-4 space-y-1">
                        {selectedService.exposes.map((x) => (
                          <li key={`${selectedService.id}-e-${x}`} className="text-xs font-body text-gray-800">
                            {x}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="text-xs font-body text-gray-500">—</div>
                    )}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      ) : (
        <div className="rounded-halo border border-gray-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <h4 className="font-heading text-sm text-gray-900">Service Catalogue</h4>
            <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
              {topologyFilteredServices.length} service{topologyFilteredServices.length === 1 ? "" : "s"}
            </span>
          </div>

          <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
            {topologyFilteredServices.map((svc) => (
              <div key={`cat-${svc.id}`} className="rounded-md border border-gray-200 bg-gray-50 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-heading text-sm text-gray-900">{svc.name}</div>
                    <div className="text-[11px] font-body text-gray-500">Domain: {svc.domain}</div>
                  </div>
                  <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-600">
                    {svc.exposes?.length ? "API Surface" : "Internal"}
                  </span>
                </div>

                <div className="mt-3">
                  <div className="text-xs font-body text-gray-600 mb-1">Responsibilities</div>
                  <ul className="list-disc pl-4 space-y-1">
                    {(svc.responsibilities || []).map((r, idx) => (
                      <li key={`${svc.id}-resp-${idx}`} className="text-xs font-body text-gray-800">
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <div className="text-xs font-body text-gray-600 mb-1">Consumes</div>
                    <div className="flex flex-wrap gap-2">
                      {(svc.consumes || []).length ? (
                        svc.consumes.map((x) => (
                          <span key={`${svc.id}-c2-${x}`} className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                            {x}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs font-body text-gray-500">—</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-body text-gray-600 mb-1">Produces</div>
                    <div className="flex flex-wrap gap-2">
                      {(svc.produces || []).length ? (
                        svc.produces.map((x) => (
                          <span key={`${svc.id}-p2-${x}`} className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800">
                            {x}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs font-body text-gray-500">—</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-body text-gray-600 mb-1">Exposes</div>
                    <div className="flex flex-wrap gap-2">
                      {(svc.exposes || []).length ? (
                        svc.exposes.map((x) => (
                          <span key={`${svc.id}-e2-${x}`} className="text-[11px] font-mono rounded-md px-2 py-1 border bg-amber-50 border-amber-200 text-gray-800">
                            {x}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs font-body text-gray-500">—</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
