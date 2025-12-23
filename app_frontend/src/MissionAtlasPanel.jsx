// app_frontend/src/MissionAtlasPanel.jsx
import React, { useMemo, useState } from "react";
import BusinessDataLineagePanel from "./BusinessDataLineagePanel";

const domains = [
  {
    id: "domain-ingestion",
    name: "Ingestion",
    description: "Bring CRM and KYC client records into the SCV platform.",
    keyEntities: ["SourceRecord", "IngestionBatch"],
  },
  {
    id: "domain-matching",
    name: "Matching",
    description: "Resolve records into a single client identity.",
    keyEntities: ["MatchCandidate", "MatchGroup", "MatchScore"],
  },
  {
    id: "domain-profile",
    name: "Client Profile",
    description: "Assemble and expose the golden client profile.",
    keyEntities: ["ClientProfile", "ClientAttribute", "Address"],
  },
  {
    id: "domain-search",
    name: "Search",
    description: "Help users quickly find the right client profile.",
    keyEntities: ["SearchQuery", "SearchResult"],
  },
  {
    id: "domain-lineage",
    name: "Lineage & Audit",
    description: "Track where data came from and how it was transformed.",
    keyEntities: ["LineageEvent", "AuditEvent"],
  },
  {
    id: "domain-ux",
    name: "Single Client View UI",
    description: "Visualise client profile, sources and lineage.",
    keyEntities: ["ClientView", "SourcePanel", "LineagePanel"],
  },
];

const services = [
  {
    id: "svc-ingestion",
    name: "Ingestion Service",
    domain: "Ingestion",
    responsibilities: [
      "Load CRM and KYC records.",
      "Normalise incoming payloads to canonical structures.",
      "Emit ingestion audit events.",
    ],
    consumes: ["CRM feed", "KYC feed"],
    produces: ["SourceRecord", "IngestionBatch", "AuditEvent"],
    exposes: [],
  },
  {
    id: "svc-matching",
    name: "Matching Service",
    domain: "Matching",
    responsibilities: [
      "Apply exact and fuzzy match rules.",
      "Group records into candidate client identities.",
    ],
    consumes: ["SourceRecord"],
    produces: ["MatchCandidate", "MatchGroup", "MatchScore"],
    exposes: [],
  },
  {
    id: "svc-profile-core",
    name: "Client Profile Service",
    domain: "Client Profile",
    responsibilities: [
      "Build ClientProfile from MatchGroup + source records.",
      "Merge core attributes and addresses.",
      "Attach lineage references.",
    ],
    consumes: ["MatchGroup", "SourceRecord"],
    produces: ["ClientProfile", "ClientAttribute", "Address", "LineageEvent"],
    exposes: ["Client Profile API"],
  },
  {
    id: "svc-search",
    name: "Client Search Service",
    domain: "Search",
    responsibilities: [
      "Index ClientProfile documents.",
      "Serve search queries with ranking.",
    ],
    consumes: ["ClientProfile"],
    produces: ["SearchResult"],
    exposes: ["Client Search API"],
  },
  {
    id: "svc-lineage",
    name: "Lineage Service",
    domain: "Lineage & Audit",
    responsibilities: [
      "Capture provenance and transformation metadata.",
      "Expose lineage graph for a given client.",
    ],
    consumes: ["LineageEvent", "AuditEvent"],
    produces: ["Lineage graph view"],
    exposes: ["Lineage API"],
  },
  {
    id: "svc-ui",
    name: "SCV Frontend",
    domain: "Single Client View UI",
    responsibilities: [
      "Call search and profile APIs.",
      "Render Single Client View: profile, sources, lineage.",
    ],
    consumes: ["Client Profile API", "Client Search API", "Lineage API"],
    produces: ["ClientView"],
    exposes: ["SCV screen"],
  },
];

const flows = [
  {
    id: "flow-01",
    name: "Client onboarding (CRM route)",
    steps: [
      "CRM feed",
      "Ingestion Service",
      "SourceRecord",
      "Matching Service",
      "MatchGroup",
      "Client Profile Service",
      "ClientProfile",
      "Client Search Service",
      "SCV Frontend",
    ],
  },
  {
    id: "flow-02",
    name: "Client onboarding (KYC route)",
    steps: [
      "KYC feed",
      "Ingestion Service",
      "SourceRecord",
      "Matching Service",
      "MatchGroup",
      "Client Profile Service",
      "ClientProfile",
      "SCV Frontend",
    ],
  },
  {
    id: "flow-03",
    name: "Search & view client",
    steps: [
      "SCV Frontend",
      "Client Search API",
      "Client Search Service",
      "SearchResult",
      "Client Profile API",
      "Client Profile Service",
      "ClientProfile",
      "SCV Frontend",
    ],
  },
  {
    id: "flow-04",
    name: "Lineage drill-down",
    steps: [
      "SCV Frontend",
      "Lineage API",
      "Lineage Service",
      "Lineage graph view",
      "SCV Frontend",
    ],
  },
];

function ComingSoonPanel({ title, subtitle, bullets }) {
  return (
    <div className="rounded-halo border border-gray-200 bg-gray-50 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-heading text-sm text-gray-900">{title}</h3>
          {subtitle ? (
            <p className="mt-1 text-xs font-body text-gray-600">{subtitle}</p>
          ) : null}
        </div>
        <span className="text-[11px] font-mono text-gray-500 bg-white border border-gray-200 rounded-md px-2 py-1">
          Planned
        </span>
      </div>

      {bullets?.length ? (
        <ul className="mt-4 list-disc pl-5 space-y-1">
          {bullets.map((b, idx) => (
            <li key={`cs-${idx}`} className="text-xs font-body text-gray-700">
              {b}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export default function MissionAtlasPanel() {
  // Shared selection state (used by Technology Architecture + Service Topology)
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [selectedService, setSelectedService] = useState(null);

  // Landing-first navigation
  const [atlasView, setAtlasView] = useState("landing");

  // ----------------------------
  // Service Topology UI state (TOP-LEVEL HOOKS)
  // ----------------------------
  const [topologyMode, setTopologyMode] = useState("dependencies"); // "dependencies" | "catalogue"
  const [topologyDomainFilter, setTopologyDomainFilter] = useState("All");
  const [topologyQuery, setTopologyQuery] = useState("");

  // NEW: Dependency graph navigation state
  const [selectedEdge, setSelectedEdge] = useState(null); // { fromId, fromName, toId, toName, labels }
  const [focusEdgeServices, setFocusEdgeServices] = useState(true); // when edge selected, focus list to edge endpoints

  const resetSelection = () => {
    setSelectedDomain(null);
    setSelectedService(null);
  };

  const visibleServices = useMemo(() => {
    return selectedDomain
      ? services.filter((s) => s.domain === selectedDomain.name)
      : services;
  }, [selectedDomain]);

  const visibleFlows = useMemo(() => {
    if (selectedService) {
      return flows.filter((flow) =>
        flow.steps.some((step) =>
          step.toLowerCase().includes(selectedService.name.toLowerCase())
        )
      );
    }
    if (selectedDomain) {
      return flows.filter((flow) =>
        flow.steps.some((step) =>
          step.toLowerCase().includes(selectedDomain.name.toLowerCase())
        )
      );
    }
    return flows;
  }, [selectedDomain, selectedService]);

  // ----------------------------
  // Service Topology derived data (TOP-LEVEL HOOKS)
  // ----------------------------
  const normalise = (s) => (s || "").toString().trim().toLowerCase();

  const topologyDomainsList = useMemo(
    () => ["All", ...domains.map((d) => d.name)],
    []
  );

  const topologyFilteredServices = useMemo(() => {
    const q = normalise(topologyQuery);
    return services.filter((svc) => {
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
  }, [topologyDomainFilter, topologyQuery]);

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
    return services.find((s) => s.id === selectedEdge.fromId) || null;
  }, [selectedEdge]);

  const selectedEdgeTo = useMemo(() => {
    if (!selectedEdge) return null;
    return services.find((s) => s.id === selectedEdge.toId) || null;
  }, [selectedEdge]);

  // ----------------------------
  // Landing tiles
  // ----------------------------
  const tiles = [
    {
      key: "businessCapabilities",
      title: "Business Capabilities",
      desc: "What this system does today, derived from the current codebase.",
      badge: "Live",
    },
    {
      key: "businessDataLineage",
      title: "Business Data Lineage",
      desc: "Where data comes from, how it transforms, and where it is used.",
      badge: "Live",
    },
    {
      key: "technologyArchitecture",
      title: "Technology Architecture",
      desc: "Domains, services, and flows across the SCV platform.",
      badge: "Live",
    },
    {
      key: "serviceTopology",
      title: "Service Topology",
      desc: "Microservices, contracts, and interactions (live from the service model).",
      badge: "Live",
    },
    {
      key: "logicalDataModel",
      title: "Logical Data Model",
      desc: "Business entities, relationships, and rules.",
      badge: "Planned",
    },
    {
      key: "physicalDataModel",
      title: "Physical Data Model",
      desc: "Database schema: tables, fields, constraints, and indexes.",
      badge: "Planned",
    },
    {
      key: "engineeringQuality",
      title: "Engineering Quality",
      desc: "Automated quality checks enforced in this repository.",
      badge: "Planned",
    },
    {
      key: "securityPosture",
      title: "Security Posture",
      desc: "Active security checks and assurance signals.",
      badge: "Planned",
    },
    {
      key: "selfHealing",
      title: "Self-Healing",
      desc: "Data integrity and agentic support, built on live system truth.",
      badge: "Planned",
    },
  ];

  const viewTitle = (() => {
    switch (atlasView) {
      case "landing":
        return "MissionAtlas — Live System Map";
      case "businessCapabilities":
        return "Business Capabilities";
      case "businessDataLineage":
        return "Business Data Lineage";
      case "technologyArchitecture":
        return "Technology Architecture";
      case "serviceTopology":
        return "Service Topology";
      case "logicalDataModel":
        return "Logical Data Model";
      case "physicalDataModel":
        return "Physical Data Model";
      case "engineeringQuality":
        return "Engineering Quality";
      case "securityPosture":
        return "Security Posture";
      case "selfHealing":
        return "Self-Healing";
      default:
        return "MissionAtlas — Live System Map";
    }
  })();

  const showBack = atlasView !== "landing";

  const renderLanding = () => (
    <div>
      <div className="mb-4">
        <h3 className="font-heading text-sm text-gray-800">Live Areas</h3>
        <p className="mt-1 text-xs font-body text-gray-600">
          MissionAtlas reflects the system as it exists right now — derived from code, data,
          and execution.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {tiles.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => {
              if (t.key !== "technologyArchitecture" && t.key !== "serviceTopology") {
                resetSelection();
              }
              setAtlasView(t.key);
            }}
            className="text-left rounded-halo border border-gray-200 bg-white hover:bg-gray-50 shadow-sm p-4 transition"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-heading text-sm text-gray-900">{t.title}</p>
                <p className="mt-1 text-xs font-body text-gray-600">{t.desc}</p>
              </div>
              <span
                className={`text-[11px] font-mono rounded-md px-2 py-1 border ${
                  t.badge === "Live"
                    ? "bg-teal-50 border-teal-200 text-gray-800"
                    : "bg-gray-50 border-gray-200 text-gray-600"
                }`}
              >
                {t.badge}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );

  const renderBusinessCapabilities = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="space-y-3">
        <h3 className="font-heading text-sm text-gray-800 mb-1">Capabilities</h3>
        {domains.map((d) => (
          <div key={d.id} className="rounded-md p-3 border bg-gray-50 border-gray-200">
            <p className="font-heading text-sm text-gray-900">{d.name}</p>
            <p className="text-xs font-body text-gray-600 mb-2">{d.description}</p>
            <p className="text-[11px] font-mono text-gray-500">
              Key entities: {d.keyEntities.join(", ")}
            </p>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        <h3 className="font-heading text-sm text-gray-800 mb-1">Key Flows</h3>
        {flows.map((flow) => (
          <div key={flow.id} className="rounded-md p-3 border bg-gray-50 border-gray-200">
            <p className="font-heading text-sm text-gray-900 mb-2">{flow.name}</p>
            <p className="text-[11px] font-mono text-gray-700 whitespace-pre-wrap leading-5">
              {flow.steps.join("  →  ")}
            </p>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTechnologyArchitecture = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="space-y-3">
        <h3 className="font-heading text-sm text-gray-800 mb-1">Domains</h3>
        {domains.map((d) => {
          const active = selectedDomain?.id === d.id;
          return (
            <div
              key={d.id}
              onClick={() => {
                setSelectedService(null);
                setSelectedDomain(active ? null : d);
              }}
              className={`cursor-pointer rounded-md p-3 border ${
                active
                  ? "bg-teal-50 border-teal-300 shadow"
                  : "bg-gray-50 border-gray-200 hover:bg-gray-100"
              }`}
            >
              <p className="font-heading text-sm text-gray-900">{d.name}</p>
              <p className="text-xs font-body text-gray-600 mb-2">{d.description}</p>
              <p className="text-[11px] font-mono text-gray-500">
                Entities: {d.keyEntities.join(", ")}
              </p>
            </div>
          );
        })}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-heading text-sm text-gray-800 mb-1">Services</h3>
          {(selectedDomain || selectedService) && (
            <button
              type="button"
              onClick={resetSelection}
              className="text-xs text-halo-primary underline hover:opacity-90"
            >
              Reset
            </button>
          )}
        </div>

        {visibleServices.map((s) => {
          const active = selectedService?.id === s.id;
          const faded = selectedDomain && s.domain !== selectedDomain.name;

          return (
            <div
              key={s.id}
              onClick={() => setSelectedService(active ? null : s)}
              className={`cursor-pointer rounded-md p-3 border transition ${
                active
                  ? "bg-amber-50 border-amber-300 shadow"
                  : faded
                  ? "opacity-50 bg-gray-50 border-gray-200"
                  : "bg-gray-50 border-gray-200 hover:bg-gray-100"
              }`}
            >
              <p className="font-heading text-sm text-gray-900 mb-1">{s.name}</p>
              <p className="text-[11px] font-body text-gray-500 mb-1">Domain: {s.domain}</p>
              <ul className="list-disc pl-4 mb-1 space-y-0.5">
                {s.responsibilities.map((r, idx) => (
                  <li key={`${s.id}-r-${idx}`} className="text-xs font-body text-gray-700">
                    {r}
                  </li>
                ))}
              </ul>
              <p className="text-[11px] font-mono text-gray-500">Produces: {s.produces.join(", ")}</p>
            </div>
          );
        })}
      </div>

      <div className="space-y-3">
        <h3 className="font-heading text-sm text-gray-800 mb-1">Flows</h3>
        {visibleFlows.map((flow) => (
          <div key={flow.id} className="rounded-md p-3 border bg-gray-50 border-gray-200">
            <p className="font-heading text-sm text-gray-900 mb-2">{flow.name}</p>
            <p className="text-[11px] font-mono text-gray-700 whitespace-pre-wrap leading-5">
              {flow.steps.join("  →  ")}
            </p>
          </div>
        ))}
      </div>
    </div>
  );

  const clearSelectedEdge = () => {
    setSelectedEdge(null);
    setFocusEdgeServices(true);
  };

  // PURE render: NO hooks here
  const renderServiceTopology = () => (
    <div className="space-y-4">
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h3 className="font-heading text-sm text-gray-900">Service Topology</h3>
            <p className="mt-1 text-xs font-body text-gray-600">
              A live view of services, contracts, and dependencies derived from the current service model.
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
                        const consumer = services.find((s) => s.id === e.toId) || null;
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

  const renderLogicalDataModel = () => (
    <ComingSoonPanel
      title="Logical Data Model"
      subtitle="Business entities, relationships, and rules."
      bullets={[
        "Entity catalogue (Client, SourceRecord, MatchGroup, EvidenceArtefact, etc.)",
        "Relationships and cardinality",
        "Declarative invariants used by Self-Healing",
      ]}
    />
  );

  const renderPhysicalDataModel = () => (
    <ComingSoonPanel
      title="Physical Data Model"
      subtitle="Database schema: tables, fields, constraints, and indexes."
      bullets={[
        "Live schema snapshot (tables + columns)",
        "Constraints and foreign keys",
        "Diff vs previous snapshot (change detection)",
      ]}
    />
  );

  const renderEngineeringQuality = () => (
    <ComingSoonPanel
      title="Engineering Quality"
      subtitle="Automated quality checks enforced in this repository."
      bullets={[
        "Linting and formatting rules",
        "Test suites and coverage",
        "Guardrail checks and evidence outputs",
      ]}
    />
  );

  const renderSecurityPosture = () => (
    <ComingSoonPanel
      title="Security Posture"
      subtitle="Active security checks and assurance signals."
      bullets={[
        "Dependency scanning",
        "SAST checks and policy gates",
        "Security evidence artefacts",
      ]}
    />
  );

  const renderSelfHealing = () => (
    <ComingSoonPanel
      title="Self-Healing"
      subtitle="Data integrity and agentic support, built on live system truth."
      bullets={[
        "Data Integrity: detect → recommend → repair → evidence",
        "Agentic Support: explain → diagnose → guided remediation",
        "Audit trail and rollback semantics",
      ]}
    />
  );

  const renderContent = () => {
    switch (atlasView) {
      case "landing":
        return renderLanding();
      case "businessCapabilities":
        return renderBusinessCapabilities();
      case "businessDataLineage":
        // IMPORTANT: unchanged wiring for Business Data Lineage
        return (
          <BusinessDataLineagePanel
            defaultClientId={1}
            defaultConceptId="client.legal_name"
            onBack={() => setAtlasView("landing")}
          />
        );
      case "technologyArchitecture":
        return renderTechnologyArchitecture();
      case "serviceTopology":
        return renderServiceTopology();
      case "logicalDataModel":
        return renderLogicalDataModel();
      case "physicalDataModel":
        return renderPhysicalDataModel();
      case "engineeringQuality":
        return renderEngineeringQuality();
      case "securityPosture":
        return renderSecurityPosture();
      case "selfHealing":
        return renderSelfHealing();
      default:
        return renderLanding();
    }
  };

  return (
    <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-4">
        <h2 style={{ fontFamily: "Fjalla One" }} className="text-lg text-gray-900 tracking-wide">
          {viewTitle}
        </h2>

        <div className="flex items-center gap-2">
          {showBack ? (
            <button
              type="button"
              onClick={() => {
                if (atlasView !== "technologyArchitecture" && atlasView !== "serviceTopology") {
                  resetSelection();
                }
                // leaving topology view should clear edge context
                if (atlasView === "serviceTopology") {
                  clearSelectedEdge();
                }
                setAtlasView("landing");
              }}
              className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white hover:bg-gray-50 text-gray-700"
            >
              Back
            </button>
          ) : null}
        </div>
      </div>

      {renderContent()}
    </section>
  );
}







