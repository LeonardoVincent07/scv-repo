// app_frontend/src/MissionAtlasPanel.jsx
import React, { useState } from "react";
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

export default function MissionAtlasPanel() {
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [selectedService, setSelectedService] = useState(null);

  // NEW: view toggle inside MissionAtlas
  // "overview" | "businessDataLineage"
  const [atlasView, setAtlasView] = useState("overview");

  // Reset when clicking outside domain or service
  const resetSelection = () => {
    setSelectedDomain(null);
    setSelectedService(null);
  };

  // Determine which services to show
  const visibleServices = selectedDomain
    ? services.filter((s) => s.domain === selectedDomain.name)
    : services;

  // Determine which flows to show
  const visibleFlows = selectedService
    ? flows.filter((flow) =>
        flow.steps.some((step) =>
          step.toLowerCase().includes(selectedService.name.toLowerCase())
        )
      )
    : selectedDomain
    ? flows.filter((flow) =>
        flow.steps.some((step) =>
          step.toLowerCase().includes(selectedDomain.name.toLowerCase())
        )
      )
    : flows;

  const isOverview = atlasView === "overview";
  const isBusinessLineage = atlasView === "businessDataLineage";

  return (
    <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-4">
        <h2
          style={{ fontFamily: "Fjalla One" }}
          className="text-lg text-gray-900 tracking-wide"
        >
          MissionAtlas Single Client View
        </h2>

        <div className="flex items-center gap-2">
          {/* View toggle buttons */}
          <button
            type="button"
            onClick={() => setAtlasView("overview")}
            className={`px-3 py-2 rounded-md text-sm font-body border ${
              isOverview
                ? "border-halo-primary bg-teal-50 text-gray-900"
                : "border-gray-200 bg-white hover:bg-gray-50 text-gray-700"
            }`}
          >
            Overview
          </button>

          <button
            type="button"
            onClick={() => setAtlasView("businessDataLineage")}
            className={`px-3 py-2 rounded-md text-sm font-body border ${
              isBusinessLineage
                ? "border-halo-primary bg-teal-50 text-gray-900"
                : "border-gray-200 bg-white hover:bg-gray-50 text-gray-700"
            }`}
          >
            Business Data Lineage
          </button>

          {/* Existing reset (only relevant on overview) */}
          {isOverview && (selectedDomain || selectedService) && (
            <button
              onClick={resetSelection}
              className="text-sm text-halo-primary underline hover:opacity-90"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* New: Business Data Lineage screen */}
      {isBusinessLineage ? (
        <BusinessDataLineagePanel
          defaultClientId={1}
          defaultConceptId="client.legal_name"
          onBack={() => setAtlasView("overview")}
        />
      ) : (
        /* Existing overview content */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* DOMAINS */}
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
                  <p className="text-xs font-body text-gray-600 mb-2">
                    {d.description}
                  </p>
                  <p className="text-[11px] font-mono text-gray-500">
                    Entities: {d.keyEntities.join(", ")}
                  </p>
                </div>
              );
            })}
          </div>

          {/* SERVICES */}
          <div className="space-y-3">
            <h3 className="font-heading text-sm text-gray-800 mb-1">
              Services
            </h3>
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
                  <p className="font-heading text-sm text-gray-900 mb-1">
                    {s.name}
                  </p>
                  <p className="text-[11px] font-body text-gray-500 mb-1">
                    Domain: {s.domain}
                  </p>
                  <ul className="list-disc pl-4 mb-1 space-y-0.5">
                    {s.responsibilities.map((r, idx) => (
                      <li
                        key={`${s.id}-r-${idx}`}
                        className="text-xs font-body text-gray-700"
                      >
                        {r}
                      </li>
                    ))}
                  </ul>
                  <p className="text-[11px] font-mono text-gray-500">
                    Produces: {s.produces.join(", ")}
                  </p>
                </div>
              );
            })}
          </div>

          {/* FLOWS */}
          <div className="space-y-3">
            <h3 className="font-heading text-sm text-gray-800 mb-1">Flows</h3>
            {visibleFlows.map((flow) => (
              <div
                key={flow.id}
                className="rounded-md p-3 border bg-gray-50 border-gray-200"
              >
                <p className="font-heading text-sm text-gray-900 mb-2">
                  {flow.name}
                </p>
                <p className="text-[11px] font-mono text-gray-700 whitespace-pre-wrap leading-5">
                  {flow.steps.join("  →  ")}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

