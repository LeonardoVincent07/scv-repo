import React, { useEffect, useState } from "react";

// Status categories for easy reference (currently not used directly but kept for clarity)
const STATUS_MAP = {
  Complete: "Complete",
  "In Progress": "In Progress",
  Planned: "Planned",
};

// Status normalisation function
function normaliseStatus(status) {
  return status ? status.toUpperCase() : "UNKNOWN";
}

// Status Chip (adjusted for consistent look)
function StatusChip({ label, status, extraClass }) {
  let statusClass = "bg-gray-100"; // Default to grey for N/A statuses

  // Define specific color mappings for statuses
  if (status === "Complete" || status === "pass") {
    statusClass = "bg-green-100"; // Green for complete / passed
  } else if (status === "In Progress" || status === "fail") {
    statusClass = "bg-yellow-100"; // Yellow for in progress / failed
  } else if (status === "Planned" || status === "not_run") {
    statusClass = "bg-blue-100"; // Blue for planned / not_run
  } else if (status === "N/A") {
    statusClass = "bg-gray-200"; // Grey color for N/A statuses
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-body ${statusClass} ${
        extraClass || ""
      }`}
    >
      {label}
    </span>
  );
}

// MissionLog Panel with Key, alignment, and Back button
export default function MissionLogPanel({ setActiveView }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await fetch("/missionlog/status_snapshot.json", {
          cache: "no-store",
        });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const json = await res.json();
        if (!cancelled) {
          setData(json);
          setError("");
        }
      } catch (err) {
        console.error("Failed to load MissionLog status snapshot", err);
        if (!cancelled) {
          setError("Could not load latest status snapshot.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const epics = data?.epics || [];

  // Handle Back button
  const handleBack = () => {
    if (typeof setActiveView === "function") {
      setActiveView("scv");
    } else {
      window.location.reload();
    }
  };

  return (
    <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
      {/* Back to Single Client View button */}
      <div className="flex justify-between mb-4">
        <h2
          style={{ fontFamily: "Fjalla One" }}
          className="text-lg text-gray-900 tracking-wide"
        >
          MissionLog Single Client View
        </h2>

        <button
          type="button"
          onClick={handleBack}
          className="inline-flex items-center justify-center px-4 py-2 rounded-md bg-[#1A9988] text-white font-body text-sm font-medium shadow-sm transition-all duration-150 hover:bg-[#178c7d] hover:-translate-y-0.5 hover:shadow-md active:bg-[#147c6f] active:translate-y-0 active:shadow-sm"
        >
          Back to Single Client View
        </button>
      </div>

      {/* Key/Legend for Statuses */}
      <div className="mb-4 p-3 bg-gray-50 rounded-md text-sm font-body text-gray-800">
        <strong>Status Key:</strong>
        <div className="flex flex-wrap gap-3 mt-2">
          <StatusChip label="Complete" status="Complete" />
          <StatusChip label="In Progress" status="In Progress" />
          <StatusChip label="Planned" status="Planned" />
          <StatusChip label="N/A" status="N/A" />
        </div>
      </div>

      {loading && (
        <p className="text-sm font-body text-gray-500">
          Loading latest status snapshot…
        </p>
      )}

      {!loading && error && (
        <p className="text-sm font-body text-red-600 mb-2">{error}</p>
      )}

      {!loading && !error && epics.length === 0 && (
        <p className="text-sm font-body text-gray-500">
          No status data available.
        </p>
      )}

      {/* MissionLog Data */}
      {!loading && !error && epics.length > 0 && (
        <div className="space-y-6">
          {epics.map((epic) => (
            <div
              key={epic.epic_id}
              className="bg-gray-50 rounded-lg border border-gray-200 p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="font-heading text-sm text-gray-900">
                    Epic {epic.epic_id}: {epic.name}
                  </p>
                </div>
                {/* Epic status chip – same size styling as feature-level */}
                <StatusChip
                  label={normaliseStatus(epic.overall_status)}
                  status={epic.overall_status}
                  extraClass="ml-auto px-3 py-1 text-xs"
                />
              </div>

              <div className="space-y-4">
                {epic.features.map((feature) => {
                  const stories = feature.stories || [];
                  const totalStories = stories.length;
                  const completedStories = stories.filter(
                    (s) => normaliseStatus(s.overall_status) === "COMPLETE"
                  ).length;

                  return (
                    <div
                      key={feature.feature_id}
                      className="bg-white rounded-md border border-gray-200 p-3"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-heading text-sm text-gray-900">
                            Feature {feature.feature_id}: {feature.name}
                          </p>
                          <p className="text-xs font-body text-gray-500">
                            {completedStories}/{totalStories} stories complete
                          </p>
                        </div>
                        {/* Feature status chip – same size styling as epic-level */}
                        <StatusChip
                          label={normaliseStatus(feature.overall_status)}
                          status={feature.overall_status}
                          extraClass="ml-auto px-3 py-1 text-xs"
                        />
                      </div>

                      <div className="space-y-1.5">
                        {stories.map((story) => {
                          return (
                            <div
                              key={story.story_id}
                              className="flex items-center justify-between"
                            >
                              <div className="flex-1">
                                <p className="text-sm font-body text-gray-700">
                                  {story.name}
                                </p>
                              </div>

                              {/* Render badges for each story */}
                              <div className="flex space-x-2">
                                {story.testing_status && (
                                  <StatusChip
                                    label="Testing"
                                    status={story.testing_status}
                                  />
                                )}
                                {story.halo_adherence && (
                                  <StatusChip
                                    label="Halo"
                                    status={story.halo_adherence}
                                  />
                                )}
                                {story.guardrail_adherence && (
                                  <StatusChip
                                    label="Guardrails"
                                    status={story.guardrail_adherence}
                                  />
                                )}
                                {story.code_quality_adherence && (
                                  <StatusChip
                                    label="Code Quality"
                                    status={story.code_quality_adherence}
                                  />
                                )}
                                {story.security_adherence && (
                                  <StatusChip
                                    label="Security"
                                    status={story.security_adherence}
                                  />
                                )}
                                {/* Default to "N/A" for the following statuses if they don't exist */}
                                {!story.policy_adherence && (
                                  <StatusChip
                                    label="Policy Adherence"
                                    status="N/A"
                                  />
                                )}
                                {!story.technology_lineage && (
                                  <StatusChip
                                    label="Technology Lineage"
                                    status="N/A"
                                  />
                                )}
                                {!story.business_data_lineage && (
                                  <StatusChip
                                    label="Business Data Lineage"
                                    status="N/A"
                                  />
                                )}
                                {!story.self_healing_adherence && (
                                  <StatusChip
                                    label="Self-healing Adherence"
                                    status="N/A"
                                  />
                                )}
                                {!story.analytics && (
                                  <StatusChip label="Analytics" status="N/A" />
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}




