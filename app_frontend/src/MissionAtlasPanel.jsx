import React, { useMemo, useState } from "react";
import BusinessDataLineagePanel from "./BusinessDataLineagePanel";
import MissionAtlasServiceTopologyPanel from "./MissionAtlasServiceTopologyPanel";
import MissionAtlasLogicalDataModelPanel from "./MissionAtlasLogicalDataModelPanel";
import MissionAtlasPhysicalDataModelPanel from "./MissionAtlasPhysicalDataModelPanel";


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
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [selectedService, setSelectedService] = useState(null);
  const [atlasView, setAtlasView] = useState("landing");

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
      title: "Microservices Architecture",
      desc: "Microservices, contracts, and interactions (live from the service model).",
      badge: "Live",
    },
    {
      key: "logicalDataModel",
      title: "Logical Data Model",
      desc: "Business entities, relationships, and rules.",
      badge: "Live",
    },
    {
      key: "physicalDataModel",
      title: "Physical Data Model",
      desc: "Database schema: tables, fields, constraints, and indexes.",
      badge: "Live",
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
              if (t.key !== "technologyArchitecture") resetSelection();
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
    <MissionAtlasPhysicalDataModelPanel />
  );

  const renderEngineeringQuality = () => (
    <ComingSoonPanel
      title="Engineering Quality"
      subtitle="Automated checks enforced in this repository."
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
        return (
          <MissionAtlasServiceTopologyPanel
            domains={domains}
            services={services}
          />
        );
      case "logicalDataModel":
        return <MissionAtlasLogicalDataModelPanel />;
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
          {(() => {
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
          })()}
        </h2>

        <div className="flex items-center gap-2">
          {showBack ? (
            <button
              type="button"
              onClick={() => {
                if (atlasView !== "technologyArchitecture") resetSelection();
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







