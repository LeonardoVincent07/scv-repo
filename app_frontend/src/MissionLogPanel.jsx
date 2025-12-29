import React, { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Status normalisation function
function normaliseStatus(status) {
  return status ? String(status).toUpperCase() : "UNKNOWN";
}

// Status Chip (fixed width + no wrap)
function StatusChip({ label, status, extraClass = "", onClick }) {
  let statusClass = "bg-gray-200"; // Default grey

  if (status === "Complete" || status === "pass") {
    statusClass = "bg-green-100";
  } else if (status === "In Progress" || status === "fail") {
    statusClass = "bg-yellow-100";
  } else if (status === "Planned" || status === "not_run") {
    statusClass = "bg-blue-100";
  } else if (status === "N/A") {
    statusClass = "bg-gray-200";
  }

  const isClickable = typeof onClick === "function";

  const classes = [
    "inline-flex items-center justify-center",
    "px-2.5 py-0.5 rounded-full",
    "text-xs font-body text-gray-900",
    "w-20",
    "text-center",
    "whitespace-nowrap",
    statusClass,
    isClickable ? "cursor-pointer hover:shadow-sm" : "cursor-default",
    extraClass,
  ].join(" ");

  if (!isClickable) return <span className={classes}>{label}</span>;

  return (
    <button type="button" onClick={onClick} className={classes} title={label}>
      {label}
    </button>
  );
}

// Evidence modal
function EvidenceModal({ open, onClose, title, subtitle, loading, error, data }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        role="button"
        tabIndex={0}
      />

      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-3xl bg-white rounded-halo shadow-lg border border-gray-200">
          <div className="flex items-start justify-between p-4 border-b border-gray-200">
            <div>
              <h3
                style={{ fontFamily: "Fjalla One" }}
                className="text-lg text-gray-900 tracking-wide"
              >
                {title}
              </h3>
              {subtitle && (
                <p className="text-sm font-body text-gray-600 mt-1">{subtitle}</p>
              )}
            </div>

            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center justify-center px-3 py-1.5 rounded-md border border-gray-300 bg-white text-gray-800 text-sm font-body hover:bg-gray-50"
            >
              Close
            </button>
          </div>

          <div className="p-4">
            {loading && (
              <p className="text-sm font-body text-gray-500">Loading evidence…</p>
            )}

            {!loading && error && (
              <p className="text-sm font-body text-red-600">{error}</p>
            )}

            {!loading && !error && (
              <div className="bg-gray-50 border border-gray-200 rounded-md p-3 overflow-auto max-h-[60vh]">
                <pre className="text-xs font-mono text-gray-800 whitespace-pre-wrap">
                  {JSON.stringify(data, null, 2)}
                </pre>
              </div>
            )}

            <p className="text-xs font-body text-gray-400 mt-3">
              Evidence is expected at{" "}
              <code>/missionlog/evidence/&lt;story_id&gt;/&lt;dimension&gt;.json</code>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Confirm execution modal
function ConfirmExecutionModal({ open, onCancel, onConfirm }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onCancel}
        role="button"
        tabIndex={0}
      />

      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl bg-white rounded-halo shadow-lg border border-gray-200">
          <div className="flex items-start justify-between p-4 border-b border-gray-200">
            <div>
              <h3
                style={{ fontFamily: "Fjalla One" }}
                className="text-lg text-gray-900 tracking-wide"
              >
                Confirm Story Execution
              </h3>
            </div>

            <button
              type="button"
              onClick={onCancel}
              className="inline-flex items-center justify-center px-3 py-1.5 rounded-md border border-gray-300 bg-white text-gray-800 text-sm font-body hover:bg-gray-50"
            >
              Close
            </button>
          </div>

          <div className="p-4">
            <p className="text-sm font-body text-gray-800">
              M7 Mission Control will now code and test this story, and ensure that it meets all
              defined principles, guidelines and guardrails before deployment. Please confirm.
            </p>

            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={onCancel}
                className="inline-flex items-center justify-center px-4 py-2 rounded-md border border-gray-300 bg-white text-gray-800 text-sm font-body hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={onConfirm}
                className="inline-flex items-center justify-center px-4 py-2 rounded-md bg-[#1A9988] text-white text-sm font-body font-medium shadow-sm transition-all duration-150 hover:bg-[#178c7d]"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Story definition modal (now loads exported JSON and renders markdown)
function StoryDefinitionModal({ open, onClose, storyId, storyName }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [doc, setDoc] = useState(null);

  useEffect(() => {
    if (!open || !storyId) return;

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError("");
      setDoc(null);

      const url = `/missionlog/story_defs/${encodeURIComponent(storyId)}.json`;

      try {
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) {
          throw new Error(
            `Story definition not found (HTTP ${res.status}). Expected: ${url}`
          );
        }
        const json = await res.json();
        if (!cancelled) setDoc(json);
      } catch (e) {
        if (!cancelled) {
          setError(e?.message || "Could not load story definition.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [open, storyId]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        role="button"
        tabIndex={0}
      />

      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-4xl bg-white rounded-halo shadow-lg border border-gray-200">
          <div className="flex items-start justify-between p-4 border-b border-gray-200">
            <div>
              <h3
                style={{ fontFamily: "Fjalla One" }}
                className="text-lg text-gray-900 tracking-wide"
              >
                {storyId} · Story Definition
              </h3>
              {storyName && (
                <p className="text-sm font-body text-gray-600 mt-1">{storyName}</p>
              )}
            </div>

            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center justify-center px-3 py-1.5 rounded-md border border-gray-300 bg-white text-gray-800 text-sm font-body hover:bg-gray-50"
            >
              Close
            </button>
          </div>

          <div className="p-4">
            {loading && (
              <p className="text-sm font-body text-gray-500">
                Loading story definition…
              </p>
            )}

            {!loading && error && (
              <p className="text-sm font-body text-red-600">{error}</p>
            )}

            {!loading && !error && doc && (
              <div className="grid grid-cols-1 lg:grid-cols-[1fr_18rem] gap-4">
                <div className="bg-gray-50 border border-gray-200 rounded-md p-4 overflow-auto max-h-[65vh]">
                  <article className="prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {doc.body_markdown || ""}
                    </ReactMarkdown>
                  </article>
                </div>

                <div className="bg-white border border-gray-200 rounded-md p-4 overflow-auto max-h-[65vh]">
                  <p className="text-xs font-body text-gray-500 mb-2">Front matter</p>
                  <pre className="text-xs font-mono text-gray-800 whitespace-pre-wrap">
                    {JSON.stringify(doc.front_matter || {}, null, 2)}
                  </pre>

                  <p className="text-xs font-body text-gray-400 mt-3">
                    Source:{" "}
                    <span className="font-mono">
                      {doc.source_path || "(unknown)"}
                    </span>
                  </p>
                  <p className="text-xs font-body text-gray-400 mt-1">
                    Exported:{" "}
                    <span className="font-mono">
                      {doc.exported_at_utc || "(unknown)"}
                    </span>
                  </p>
                </div>
              </div>
            )}

            {!loading && !error && !doc && (
              <p className="text-sm font-body text-gray-500">
                No story definition data available.
              </p>
            )}

            <p className="text-xs font-body text-gray-400 mt-3">
              Definition is generated from story markdown files (re-run the export
              script to refresh).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function MissionLogPanel({ setActiveView }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Evidence modal state
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [evidenceError, setEvidenceError] = useState("");
  const [evidenceData, setEvidenceData] = useState(null);
  const [evidenceMeta, setEvidenceMeta] = useState({
    storyId: "",
    storyName: "",
    dimensionKey: "",
    dimensionLabel: "",
    status: "",
  });

  // Story definition modal state
  const [storyDefOpen, setStoryDefOpen] = useState(false);
  const [storyDefMeta, setStoryDefMeta] = useState({
    storyId: "",
    storyName: "",
  });

  // Demo execution state (local-first MissionControl loop)
  const [demo, setDemo] = useState({
    mode: "idle", // idle | confirming | running | completed | failed
    storyId: "",
    storyName: "",
    runId: "",
    message: "",
  });

  // Filters (multi-select)
  const [selectedEpics, setSelectedEpics] = useState([]);
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [selectedStories, setSelectedStories] = useState([]);

  const reloadSnapshot = async () => {
    try {
      const res = await fetch(`/missionlog/status_snapshot.json?t=${Date.now()}`, {
        cache: "no-store",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setError("");
    } catch (err) {
      console.error("Failed to load MissionLog status snapshot", err);
      setError("Could not load latest status snapshot.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reloadSnapshot();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Poll MissionControl runner and refresh snapshot while a run is active
  useEffect(() => {
    if (demo.mode !== "running" || !demo.runId) return;

    let stopped = false;

    const interval = setInterval(async () => {
      if (stopped) return;

      try {
        const res = await fetch(`http://127.0.0.1:8000/missioncontrol/runs/${demo.runId}`, {
          cache: "no-store",
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const run = await res.json();

        setDemo((d) => ({
          ...d,
          message: run.message || d.message,
          mode:
            run.state === "completed"
              ? "completed"
              : run.state === "failed"
              ? "failed"
              : "running",
        }));

        await reloadSnapshot();

        if (run.state === "completed" || run.state === "failed") {
          clearInterval(interval);
        }
      } catch (err) {
        console.error("MissionControl polling error", err);
      }
    }, 700);

    return () => {
      stopped = true;
      clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demo.mode, demo.runId]);

  const startRun = async (storyId, storyName) => {
    setDemo({
      mode: "running",
      storyId,
      storyName: storyName || "",
      runId: "",
      message: "Starting execution…",
    });

    const res = await fetch("http://127.0.0.1:8000/missioncontrol/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ story_id: storyId }),
    });

    const json = await res.json();

    setDemo((d) => ({
      ...d,
      runId: json.run_id || "",
    }));
  };

  const epics = data?.epics || [];

  // Fixed badge spec (exact order)
  const BADGES = useMemo(
    () => [
      { label: "Testing", key: "testing_status", mvp: true, evidenceDim: "testing" },
      { label: "Halo", key: "halo_adherence", mvp: true, evidenceDim: "halo" },
      { label: "Guardrails", key: "guardrail_adherence", mvp: true, evidenceDim: "guardrails" },
      { label: "Quality", key: "code_quality_adherence", mvp: true, evidenceDim: "code_quality" },
      { label: "Security", key: "security_policy_adherence", mvp: true, evidenceDim: "security" },

      { label: "Policy", key: "policy_adherence", mvp: false, evidenceDim: "policy" },
      { label: "Tech Trace", key: "technology_lineage_adherence", mvp: false, evidenceDim: "tech_lineage" },
      { label: "Lineage", key: "business_data_lineage_adherence", mvp: false, evidenceDim: "business_lineage" },
      { label: "Self-Heal", key: "self_healing_adherence", mvp: false, evidenceDim: "self_healing" },
      { label: "Analytics", key: "analytics_adherence", mvp: false, evidenceDim: "analytics" },
    ],
    []
  );

  const handleBack = () => {
    if (typeof setActiveView === "function") setActiveView("scv");
    else window.location.reload();
  };

  async function openEvidence(story, badge) {
    const raw = story?.[badge.key];
    const statusVal = badge.mvp ? (raw || "not_run") : "N/A";
    if (statusVal !== "pass" && statusVal !== "fail") return;

    const storyId = story.story_id;
    const storyName = story.name;

    setEvidenceMeta({
      storyId,
      storyName,
      dimensionKey: badge.key,
      dimensionLabel: badge.label,
      status: statusVal,
    });

    setEvidenceOpen(true);
    setEvidenceLoading(true);
    setEvidenceError("");
    setEvidenceData(null);

    const url = `/missionlog/evidence/${encodeURIComponent(
      storyId
    )}/${encodeURIComponent(badge.evidenceDim)}.json`;

    try {
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok)
        throw new Error(`Evidence not found (HTTP ${res.status}). Expected: ${url}`);
      const json = await res.json();
      setEvidenceData(json);
    } catch (err) {
      setEvidenceError(
        err?.message || "Could not load evidence for this badge (file missing or invalid JSON)."
      );
    } finally {
      setEvidenceLoading(false);
    }
  }

  const closeEvidence = () => {
    setEvidenceOpen(false);
    setEvidenceLoading(false);
    setEvidenceError("");
    setEvidenceData(null);
  };

  const openStoryDefinition = (story) => {
    setStoryDefMeta({ storyId: story.story_id, storyName: story.name });
    setStoryDefOpen(true);
  };

  const closeStoryDefinition = () => {
    setStoryDefOpen(false);
  };

  // ---------- Filter indexes + expansion rules ----------

  const index = useMemo(() => {
    const epicsById = new Map();
    const featuresById = new Map();
    const storiesById = new Map();
    const featureToEpic = new Map();
    const storyToFeature = new Map();
    const epicToFeatures = new Map();
    const featureToStories = new Map();

    for (const e of epics) {
      epicsById.set(e.epic_id, e);
      epicToFeatures.set(e.epic_id, []);
      for (const f of e.features || []) {
        featuresById.set(f.feature_id, f);
        featureToEpic.set(f.feature_id, e.epic_id);
        epicToFeatures.get(e.epic_id).push(f.feature_id);

        featureToStories.set(f.feature_id, []);
        for (const s of f.stories || []) {
          storiesById.set(s.story_id, s);
          storyToFeature.set(s.story_id, f.feature_id);
          featureToStories.get(f.feature_id).push(s.story_id);
        }
      }
    }

    return {
      epicsById,
      featuresById,
      storiesById,
      featureToEpic,
      storyToFeature,
      epicToFeatures,
      featureToStories,
    };
  }, [epics]);

  const options = useMemo(() => {
    const epicOpts = epics.map((e) => ({
      id: e.epic_id,
      label: `${e.epic_id}: ${e.name}`,
    }));

    const featureOpts = [];
    const storyOpts = [];

    for (const e of epics) {
      for (const f of e.features || []) {
        featureOpts.push({
          id: f.feature_id,
          label: `${f.feature_id}: ${f.name}`,
        });
        for (const s of f.stories || []) {
          storyOpts.push({
            id: s.story_id,
            label: `${s.story_id}: ${s.name}`,
          });
        }
      }
    }

    return { epicOpts, featureOpts, storyOpts };
  }, [epics]);

  const visibleSets = useMemo(() => {
    const anySelected =
      selectedEpics.length > 0 ||
      selectedFeatures.length > 0 ||
      selectedStories.length > 0;

    if (!anySelected) {
      return {
        anySelected: false,
        visibleEpicIds: null,
        visibleFeatureIds: null,
        visibleStoryIds: null,
      };
    }

    const visibleEpicIds = new Set();
    const visibleFeatureIds = new Set();
    const visibleStoryIds = new Set();

    // 1) Expand epics -> all features + all stories
    for (const epicId of selectedEpics) {
      visibleEpicIds.add(epicId);
      const feats = index.epicToFeatures.get(epicId) || [];
      for (const fid of feats) {
        visibleFeatureIds.add(fid);
        const stories = index.featureToStories.get(fid) || [];
        for (const sid of stories) visibleStoryIds.add(sid);
      }
    }

    // 2) Expand features -> parent epic + all stories
    for (const featureId of selectedFeatures) {
      visibleFeatureIds.add(featureId);
      const epicId = index.featureToEpic.get(featureId);
      if (epicId) visibleEpicIds.add(epicId);

      const stories = index.featureToStories.get(featureId) || [];
      for (const sid of stories) visibleStoryIds.add(sid);
    }

    // 3) Expand stories -> parent feature + parent epic (only that story)
    for (const storyId of selectedStories) {
      visibleStoryIds.add(storyId);
      const featureId = index.storyToFeature.get(storyId);
      if (featureId) {
        visibleFeatureIds.add(featureId);
        const epicId = index.featureToEpic.get(featureId);
        if (epicId) visibleEpicIds.add(epicId);
      }
    }

    return {
      anySelected: true,
      visibleEpicIds,
      visibleFeatureIds,
      visibleStoryIds,
    };
  }, [selectedEpics, selectedFeatures, selectedStories, index]);

  const filteredEpics = useMemo(() => {
    if (!visibleSets.anySelected) return epics;

    return epics
      .filter((e) => visibleSets.visibleEpicIds.has(e.epic_id))
      .map((e) => ({
        ...e,
        features: (e.features || [])
          .filter((f) => visibleSets.visibleFeatureIds.has(f.feature_id))
          .map((f) => ({
            ...f,
            stories: (f.stories || []).filter((s) =>
              visibleSets.visibleStoryIds.has(s.story_id)
            ),
          })),
      }));
  }, [epics, visibleSets]);

  const clearFilters = () => {
    setSelectedEpics([]);
    setSelectedFeatures([]);
    setSelectedStories([]);
  };

  const onMultiSelectChange = (setter) => (e) => {
    const vals = Array.from(e.target.selectedOptions).map((o) => o.value);
    setter(vals);
  };

  // ---------- Status column alignment ----------
  const ROW_GRID = "grid grid-cols-[1fr_7rem] items-start gap-3"; // 7rem ~ w-28

  return (
    <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
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

      {demo.mode === "running" && (
        <div className="mb-4 p-3 bg-halo-primary/10 rounded-md border border-halo-primary text-sm font-body text-gray-900">
          <strong>M7 Mission Control:</strong> {demo.message || "Running…"}
        </div>
      )}
      {demo.mode === "completed" && (
        <div className="mb-4 p-3 bg-green-50 rounded-md border border-green-200 text-sm font-body text-gray-900">
          <strong>M7 Mission Control:</strong> Completed.
        </div>
      )}
      {demo.mode === "failed" && (
        <div className="mb-4 p-3 bg-yellow-50 rounded-md border border-yellow-200 text-sm font-body text-gray-900">
          <strong>M7 Mission Control:</strong> Failed. Check backend logs.
        </div>
      )}

      <div className="mb-4 p-3 bg-gray-50 rounded-md text-sm font-body text-gray-800">
        <strong>Status Key:</strong>
        <div className="flex flex-wrap gap-3 mt-2">
          <StatusChip label="Complete" status="pass" />
          <StatusChip label="In Progress" status="fail" />
          <StatusChip label="Planned" status="not_run" />
          <StatusChip label="N/A" status="N/A" />
        </div>
      </div>

      {/* NEW: Filters */}
      <div className="mb-4 p-4 bg-white rounded-md border border-gray-200">
        <div className="flex items-start justify-between gap-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
            <div>
              <label className="block text-xs font-body text-gray-700 mb-1">
                Filter Epics
              </label>
              <select
                multiple
                value={selectedEpics}
                onChange={onMultiSelectChange(setSelectedEpics)}
                className="w-full text-sm font-body border border-gray-300 rounded-md p-2 bg-white"
                size={Math.min(6, Math.max(3, options.epicOpts.length))}
              >
                {options.epicOpts.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-body text-gray-700 mb-1">
                Filter Features
              </label>
              <select
                multiple
                value={selectedFeatures}
                onChange={onMultiSelectChange(setSelectedFeatures)}
                className="w-full text-sm font-body border border-gray-300 rounded-md p-2 bg-white"
                size={Math.min(6, Math.max(3, options.featureOpts.length))}
              >
                {options.featureOpts.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-body text-gray-700 mb-1">
                Filter Stories
              </label>
              <select
                multiple
                value={selectedStories}
                onChange={onMultiSelectChange(setSelectedStories)}
                className="w-full text-sm font-body border border-gray-300 rounded-md p-2 bg-white"
                size={Math.min(6, Math.max(3, options.storyOpts.length))}
              >
                {options.storyOpts.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex-shrink-0">
            <button
              type="button"
              onClick={clearFilters}
              className="inline-flex items-center justify-center px-4 py-2 rounded-md border border-gray-300 bg-white text-gray-800 text-sm font-body hover:bg-gray-50"
            >
              Clear
            </button>
          </div>
        </div>

        <p className="text-xs font-body text-gray-500 mt-3">
          Select any combination. Stories show their parent Feature and Epic.
          Features show their Epic and all Stories. Epics show all Features and
          Stories.
        </p>
      </div>

      {loading && (
        <p className="text-sm font-body text-gray-500">Loading latest status snapshot…</p>
      )}
      {!loading && error && <p className="text-sm font-body text-red-600 mb-2">{error}</p>}
      {!loading && !error && filteredEpics.length === 0 && (
        <p className="text-sm font-body text-gray-500">No status data available.</p>
      )}

      {!loading && !error && filteredEpics.length > 0 && (
        <div className="space-y-6">
          {filteredEpics.map((epic) => (
            <div
              key={epic.epic_id}
              className="bg-gray-50 rounded-lg border border-gray-200 p-4"
            >
              <div className={`${ROW_GRID} mb-3`}>
                <p className="font-heading text-sm text-gray-900">
                  Epic {epic.epic_id}: {epic.name}
                </p>

                <div className="flex justify-end">
                  <StatusChip
                    label={normaliseStatus(epic.overall_status)}
                    status={epic.overall_status}
                    extraClass="w-28"
                  />
                </div>
              </div>

              <div className="space-y-4">
                {(epic.features || []).map((feature) => (
                  <div
                    key={feature.feature_id}
                    className="bg-white rounded-md border border-gray-200 p-4"
                  >
                    {/* CHANGED: bleed header row to outer edges to align status with Epic */}
                    <div className={`${ROW_GRID} -mx-4 px-4`}>
                      <p className="font-heading text-sm text-gray-900">
                        Feature {feature.feature_id}: {feature.name}
                      </p>

                      <div className="flex justify-end">
                        <StatusChip
                          label={normaliseStatus(feature.overall_status)}
                          status={feature.overall_status}
                          extraClass="w-28"
                        />
                      </div>
                    </div>

                    <div className="mt-3 space-y-2">
                      {(feature.stories || []).map((story) => (
                        <div
                          key={story.story_id}
                          className="bg-gray-50 rounded-md border border-gray-200 p-3"
                        >
                          {/* CHANGED: bleed header row to outer edges to align status with Epic/Feature */}
                          <div className={`${ROW_GRID} -mx-3 px-3`}>
                            <button
                              type="button"
                              onClick={() => openStoryDefinition(story)}
                              className="text-sm font-body text-gray-900 truncate min-w-0 text-left rounded-md px-2 py-1 -ml-2 hover:bg-white/70 focus:outline-none focus:ring-2 focus:ring-[#1A9988]"
                              title="View story definition"
                            >
                              <span className="font-semibold">{story.story_id}</span> · {story.name}
                            </button>

                            {/* ONLY CHANGE: button moved left of chip, widened, and ST-05 green */}
                            <div className="flex items-center justify-end gap-2">
                              <button
                                type="button"
                                disabled={story.story_id !== "ST-05" || demo.mode === "running"}
                                onClick={() =>
                                  setDemo({
                                    mode: "confirming",
                                    storyId: story.story_id,
                                    storyName: story.name || "",
                                    runId: "",
                                    message: "",
                                  })
                                }
                                className={[
                                  "inline-flex items-center justify-center",
                                  "px-4 py-2 rounded-md",
                                  "text-xs font-body font-medium",
                                  "whitespace-nowrap",
                                  "min-w-[170px]",
                                  story.story_id === "ST-05"
                                    ? "bg-[#1A9988] text-white hover:bg-[#178c7d]"
                                    : "bg-gray-200 text-gray-500 cursor-not-allowed",
                                  demo.mode === "running"
                                    ? "opacity-60 cursor-not-allowed"
                                    : "",
                                ].join(" ")}
                              >
                                Ready to Implement
                              </button>

                              <StatusChip
                                label={normaliseStatus(story.overall_status)}
                                status={story.overall_status}
                                extraClass="w-28"
                              />
                            </div>
                          </div>

                          <div className="mt-2 overflow-x-auto">
                            <div className="flex flex-nowrap gap-2 justify-start">
                              {BADGES.map((b) => {
                                const raw = story?.[b.key];
                                const statusVal = b.mvp ? (raw || "not_run") : "N/A";
                                const clickable = statusVal === "pass" || statusVal === "fail";

                                return (
                                  <StatusChip
                                    key={`${story.story_id}-${b.key}`}
                                    label={b.label}
                                    status={statusVal}
                                    onClick={clickable ? () => openEvidence(story, b) : undefined}
                                  />
                                );
                              })}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <ConfirmExecutionModal
        open={demo.mode === "confirming"}
        onCancel={() =>
          setDemo({ mode: "idle", storyId: "", storyName: "", runId: "", message: "" })
        }
        onConfirm={() => startRun(demo.storyId, demo.storyName)}
      />

      <EvidenceModal
        open={evidenceOpen}
        onClose={closeEvidence}
        title={`${evidenceMeta.storyId} · ${evidenceMeta.dimensionLabel} Evidence`}
        subtitle={`${evidenceMeta.storyName} · Status: ${evidenceMeta.status}`}
        loading={evidenceLoading}
        error={evidenceError}
        data={evidenceData}
      />

      <StoryDefinitionModal
        open={storyDefOpen}
        onClose={closeStoryDefinition}
        storyId={storyDefMeta.storyId}
        storyName={storyDefMeta.storyName}
      />
    </section>
  );
}












