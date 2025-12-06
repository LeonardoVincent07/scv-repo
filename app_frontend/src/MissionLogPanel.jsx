// app_frontend/src/MissionLogPanel.jsx
import React from "react";

const ACTIVE_DIMENSIONS = [
  "Halo",
  "Design principles",
  "Guardrails",
  "Testing",
  "Policy as code",
];

const FUTURE_DIMENSIONS = [
  "Dynamics",
  "Technology lineage",
  "Business data lineage",
  "Self-healing",
  "Analytics",
];

// --- Mock data representing ALL epics, features and stories in the repo ---
// Based on missionlog/status/status_snapshot.md and story files.
const missionLogData = [
  {
    epicId: "E00",
    epicName: "Application Bootstrapping",
    overallStatus: "Complete",
    features: [
      {
        featureId: "FT-00-BE",
        name: "Backend Fundamentals",
        overallStatus: "Complete",
        stories: [
          {
            id: "ST-00",
            title: "Provide Basic Backend API Availability",
            overallStatus: "Complete",
            dimensions: {
              Halo: "Complete",
              "Design principles": "Complete",
              Guardrails: "Complete",
              Testing: "Complete",
              "Policy as code": "Complete",
            },
          },
        ],
      },
    ],
  },
  {
    epicId: "E00-UI",
    epicName: "User Interface Bootstrapping",
    overallStatus: "In Progress",
    features: [
      {
        featureId: "FT-00-UI",
        name: "Frontend Fundamentals",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-00-FRONTEND-UI-SHELL",
            title: "Provide Frontend UI Shell Availability",
            overallStatus: "In Progress",
            dimensions: {
              Halo: "Complete",
              "Design principles": "In progress",
              Guardrails: "Planned",
              Testing: "Complete",
              "Policy as code": "Planned",
            },
          },
        ],
      },
    ],
  },
  {
    epicId: "EP-01",
    epicName: "Client Ingestion & Normalisation",
    overallStatus: "In Progress",
    features: [
      {
        featureId: "FT-01",
        name: "Source System Configuration",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-01",
            title: "Register CRM source",
            overallStatus: "In Progress",
          },
          {
            id: "ST-02",
            title: "Register KYC source",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-02",
        name: "Schema Mapping to Canonical Model",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-03",
            title: "Map identity fields",
            overallStatus: "Complete",
            dimensions: {
              Halo: "Complete",
              "Design principles": "Complete",
              Guardrails: "Complete",
              Testing: "Complete",
              "Policy as code": "Complete",
            },
          },
          {
            id: "ST-04",
            title: "Map identifiers",
            overallStatus: "In Progress",
            dimensions: {
              Halo: "In progress",
              "Design principles": "In progress",
              Guardrails: "In progress",
              Testing: "In progress",
              "Policy as code": "Planned",
            },
          },
        ],
      },
      {
        featureId: "FT-03",
        name: "Initial Bulk Ingestion",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-05",
            title: "Bulk load CRM",
            overallStatus: "In Progress",
          },
          {
            id: "ST-06",
            title: "Bulk load KYC",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-04",
        name: "Incremental Ingestion & Change Detection",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-07",
            title: "Detect upstream deltas",
            overallStatus: "In Progress",
          },
          {
            id: "ST-08",
            title: "Apply deltas",
            overallStatus: "In Progress",
          },
        ],
      },
    ],
  },
  {
    epicId: "EP-02",
    epicName: "Client Matching & Golden Record",
    overallStatus: "In Progress",
    features: [
      {
        featureId: "FT-05",
        name: "Exact Match Rules",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-09",
            title: "Match by tax ID",
            overallStatus: "In Progress",
          },
          {
            id: "ST-10",
            title: "Match by registration number",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-06",
        name: "Fuzzy & Probabilistic Matching",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-11",
            title: "Fuzzy name match",
            overallStatus: "In Progress",
          },
          {
            id: "ST-12",
            title: "Attribute confidence",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-07",
        name: "Golden Record Construction",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-13",
            title: "Merge identity",
            overallStatus: "In Progress",
          },
          {
            id: "ST-14",
            title: "Merge addresses",
            overallStatus: "In Progress",
          },
          {
            id: "ST-15",
            title: "Record lineage",
            overallStatus: "In Progress",
          },
        ],
      },
    ],
  },
  {
    epicId: "EP-03",
    epicName: "Client Search",
    overallStatus: "In Progress",
    features: [
      {
        featureId: "FT-08",
        name: "Search Index & Normalisation",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-16",
            title: "Build index",
            overallStatus: "In Progress",
          },
          {
            id: "ST-17",
            title: "Normalise search fields",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-09",
        name: "Fuzzy Search & Ranking",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-18",
            title: "Fuzzy search queries",
            overallStatus: "In Progress",
          },
          {
            id: "ST-19",
            title: "Search ranking",
            overallStatus: "In Progress",
          },
        ],
      },
    ],
  },
  {
    epicId: "EP-04",
    epicName: "Client Profile Assembly",
    overallStatus: "In Progress",
    features: [
      {
        featureId: "FT-10",
        name: "Assemble Canonical Profile",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-20",
            title: "Assemble base profile",
            overallStatus: "In Progress",
            dimensions: {
              Halo: "Planned",
              "Design principles": "In progress",
              Guardrails: "In progress",
              Testing: "In progress",
              "Policy as code": "Planned",
            },
          },
          {
            id: "ST-21",
            title: "Assemble metadata",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-11",
        name: "Lineage Exposure",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-22",
            title: "Expose lineage",
            overallStatus: "In Progress",
          },
          {
            id: "ST-23",
            title: "Drill-down lineage",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-12",
        name: "Conflict Presentation",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-24",
            title: "Flag conflicts",
            overallStatus: "In Progress",
          },
          {
            id: "ST-25",
            title: "Show merge logic",
            overallStatus: "In Progress",
          },
        ],
      },
    ],
  },
  {
    epicId: "EP-05",
    epicName: "Data Quality & Lineage",
    overallStatus: "In Progress",
    features: [
      {
        featureId: "FT-13",
        name: "Lineage Tracking",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-26",
            title: "Store lineage history",
            overallStatus: "In Progress",
          },
          {
            id: "ST-27",
            title: "Timestamp lineage",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-14",
        name: "Data Quality Scoring",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-28",
            title: "Compute freshness",
            overallStatus: "In Progress",
          },
          {
            id: "ST-29",
            title: "Compute completeness",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-15",
        name: "Auditability & Evidence",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-30",
            title: "Audit ingestion",
            overallStatus: "In Progress",
            dimensions: {
              Halo: "Planned",
              "Design principles": "Planned",
              Guardrails: "Planned",
              Testing: "In progress",
              "Policy as code": "Planned",
            },
          },
          {
            id: "ST-31",
            title: "Audit merge",
            overallStatus: "In Progress",
          },
        ],
      },
    ],
  },
  {
    epicId: "EP-06",
    epicName: "Integration & API Exposure",
    overallStatus: "In Progress",
    features: [
      {
        featureId: "FT-16",
        name: "Search API",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-32",
            title: "Search API basic",
            overallStatus: "In Progress",
          },
          {
            id: "ST-33",
            title: "Search API ranking",
            overallStatus: "In Progress",
          },
        ],
      },
      {
        featureId: "FT-17",
        name: "Client Profile API",
        overallStatus: "In Progress",
        stories: [
          {
            id: "ST-34",
            title: "Profile API basic",
            overallStatus: "In Progress",
          },
          {
            id: "ST-35",
            title: "Profile API lineage",
            overallStatus: "In Progress",
          },
        ],
      },
    ],
  },
];

// --- Status → colour mapping ------------------------------------------------

function normaliseStatus(rawStatus) {
  const v = (rawStatus || "").toString().toLowerCase();
  if (v === "complete" || v === "completed" || v === "pass") return "Complete";
  if (v === "in progress" || v === "in_progress") return "In progress";
  if (v === "planned" || v === "not_run") return "Planned";
  if (v === "inactive") return "Inactive";
  return "Planned";
}

function statusChipClasses(rawStatus) {
  const status = normaliseStatus(rawStatus);

  switch (status) {
    case "Complete": // Green
      return "bg-emerald-100 text-emerald-800 border-emerald-200";
    case "In progress": // Yellow
      return "bg-amber-100 text-amber-800 border-amber-200";
    case "Planned": // Blue
      return "bg-sky-100 text-sky-800 border-sky-200";
    case "Inactive": // Grey
    default:
      return "bg-gray-100 text-gray-600 border-gray-300";
  }
}

function StatusChip({ label, status }) {
  const classes = statusChipClasses(status);
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-body border ${classes}`}
    >
      {label}
    </span>
  );
}

function DimensionChip({ name, status, isFuture }) {
  const effectiveStatus = isFuture ? "Inactive" : status || "Planned";
  const classes = statusChipClasses(effectiveStatus);

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-body border whitespace-nowrap ${classes} ${
        isFuture ? "opacity-80" : ""
      }`}
    >
      {name}
    </span>
  );
}

export default function MissionLogPanel() {
  return (
    <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2
          style={{ fontFamily: "Fjalla One" }}
          className="text-lg text-gray-900 tracking-wide"
        >
          MissionLog Single Client View
        </h2>
      </div>

      <div className="space-y-6">
        {missionLogData.map((epic) => (
          <div
            key={epic.epicId}
            className="bg-gray-50 rounded-lg border border-gray-200 p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="font-heading text-sm text-gray-900">
                  Epic {epic.epicId}: {epic.epicName}
                </p>
              </div>
              <StatusChip
                label={normaliseStatus(epic.overallStatus)}
                status={epic.overallStatus}
              />
            </div>

            <div className="space-y-4">
              {epic.features.map((feature) => {
                const totalStories = feature.stories.length;
                const completedStories = feature.stories.filter(
                  (s) =>
                    normaliseStatus(s.overallStatus) === "Complete"
                ).length;

                return (
                  <div
                    key={feature.featureId}
                    className="bg-white rounded-md border border-gray-200 p-3"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="font-heading text-sm text-gray-900">
                          Feature {feature.featureId}: {feature.name}
                        </p>
                        <p className="text-xs font-body text-gray-500">
                          {completedStories}/{totalStories} stories complete
                        </p>
                      </div>
                      <StatusChip
                        label={normaliseStatus(feature.overallStatus)}
                        status={feature.overallStatus}
                      />
                    </div>

                    <div className="space-y-1.5">
                      {feature.stories.map((story) => (
                        <div
                          key={story.id}
                          className="flex items-center gap-3 border border-gray-200 bg-gray-50 rounded-md px-3 py-2"
                        >
                          {/* Story ID + title */}
                          <div className="min-w-[260px] pr-2">
                            <p className="font-body text-sm text-gray-900">
                              <span className="font-semibold mr-1">
                                {story.id}
                              </span>
                              {story.title}
                            </p>
                          </div>

                          {/* All dimension badges on one line */}
                          <div className="flex-1 flex items-center gap-1 overflow-x-auto whitespace-nowrap">
                            {ACTIVE_DIMENSIONS.map((dim) => (
                              <DimensionChip
                                key={dim}
                                name={dim}
                                status={story.dimensions?.[dim]}
                                isFuture={false}
                              />
                            ))}
                            {FUTURE_DIMENSIONS.map((dim) => (
                              <DimensionChip
                                key={dim}
                                name={dim}
                                isFuture={true}
                              />
                            ))}
                          </div>

                          {/* Overall story status on the right */}
                          <div className="ml-2">
                            <StatusChip
                              label={normaliseStatus(story.overallStatus)}
                              status={story.overallStatus}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

