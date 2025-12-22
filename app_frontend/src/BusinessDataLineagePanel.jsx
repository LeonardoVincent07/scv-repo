// app_frontend/src/BusinessDataLineagePanel.jsx
import React, { useEffect, useMemo, useState } from "react";

const BACKEND_BASE_URL = "http://127.0.0.1:8000";

const CRITICAL_DATA_ELEMENTS = [
  {
    group: "Identity",
    items: [
      {
        conceptId: "client.legal_name",
        displayName: "Client Legal Name",
        status: "tracked",
        note: "Authoritative CRM source",
      },
      {
        conceptId: "client.trade_name",
        displayName: "Trading / Known-As Name",
        status: "planned",
      },
      {
        conceptId: "client.external_id",
        displayName: "External Client Identifier",
        status: "planned",
      },
      {
        conceptId: "client.primary_address",
        displayName: "Primary Registered Address",
        status: "planned",
      },
    ],
  },
  {
    group: "Jurisdiction & Regulatory",
    items: [
      {
        conceptId: "client.country",
        displayName: "Country of Incorporation",
        status: "planned",
      },
      {
        conceptId: "client.tax_id",
        displayName: "Tax Identifier",
        status: "planned",
        note: "Sensitive / masked",
      },
      {
        conceptId: "client.lei",
        displayName: "Legal Entity Identifier (LEI)",
        status: "planned",
      },
    ],
  },
  {
    group: "Risk & Classification",
    items: [
      {
        conceptId: "client.segment",
        displayName: "Client Segment",
        status: "planned",
      },
      {
        conceptId: "client.risk_rating",
        displayName: "Risk Rating",
        status: "planned",
        note: "Policy-derived",
      },
    ],
  },
  {
    group: "Lifecycle & Governance",
    items: [
      {
        conceptId: "client.onboarding_date",
        displayName: "Onboarding Date",
        status: "planned",
      },
      {
        conceptId: "client.status",
        displayName: "Client Status",
        status: "planned",
      },
      {
        conceptId: "client.last_reviewed_at",
        displayName: "Last KYC Review Date",
        status: "planned",
      },
      {
        conceptId: "client.source_system",
        displayName: "Source System of Record",
        status: "planned",
      },
    ],
  },
];

function Pill({ children, tone = "neutral" }) {
  const toneClass =
    tone === "ok"
      ? "bg-green-100 text-green-800 border-green-200"
      : tone === "error"
      ? "bg-red-100 text-red-800 border-red-200"
      : tone === "warn"
      ? "bg-yellow-100 text-yellow-900 border-yellow-200"
      : "bg-gray-100 text-gray-800 border-gray-200";

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-body border ${toneClass}`}
    >
      {children}
    </span>
  );
}

function formatUtc(ts) {
  if (!ts) return "—";
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return String(ts);
  // Keep it simple and consistent; browser locale is fine for demo
  return d.toLocaleString();
}

export default function BusinessDataLineagePanel({
  defaultClientId = 1,
  defaultConceptId = "client.legal_name",
  onBack,
}) {
  const [clientId, setClientId] = useState(String(defaultClientId));
  const [conceptId, setConceptId] = useState(String(defaultConceptId));

  // NEW: simple two-step flow:
  // 1) CDE list
  // 2) Detail view
  const [view, setView] = useState("cdeList"); // "cdeList" | "detail"

  const [loading, setLoading] = useState(false);
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState("");

  const endpoint = useMemo(() => {
    const cid = encodeURIComponent(String(clientId).trim());
    const cc = encodeURIComponent(String(conceptId).trim());
    return `${BACKEND_BASE_URL}/atlas/lineage/client/${cid}/concept/${cc}`;
  }, [clientId, conceptId]);

  const fetchLineage = async () => {
    setError("");
    setLoading(true);
    setPayload(null);

    try {
      const res = await fetch(endpoint);
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail?.detail || `HTTP ${res.status}`);
      }
      const json = await res.json();
      setPayload(json);
    } catch (e) {
      setError(e?.message || "Failed to load lineage.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Keep behaviour aligned: only fetch when entering the detail view
    if (view === "detail") {
      fetchLineage();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view]);

  const artifact = payload?.artifact || null;
  const resolvedValue = payload?.resolved_value;
  const resolution = payload?.resolution;

  const statusTone =
    resolution?.status === "ok"
      ? "ok"
      : resolution?.status === "not_found"
      ? "warn"
      : resolution?.status === "error"
      ? "error"
      : "neutral";

  const trackedConcepts = new Set(["client.legal_name"]);

  const goToDetail = (nextConceptId) => {
    setConceptId(String(nextConceptId));
    setView("detail");
  };

  // =========================
  // VIEW 1: CDE LIST
  // =========================
  if (view === "cdeList") {
    return (
      <div className="space-y-4">
        {/* Header row (kept consistent) */}
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="font-fjalla text-base text-gray-900 tracking-wide">
              Business Data Lineage
            </h3>
            <p className="text-xs font-body text-gray-600">
              Critical Data Elements tracked by the platform
            </p>
          </div>

          <div className="flex items-center gap-2">
            {onBack && (
              <button
                type="button"
                onClick={onBack}
                className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white hover:bg-gray-50"
              >
                Back
              </button>
            )}
          </div>
        </div>

        {/* Controls (client stays on the list page too, for realism) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
            <label className="block text-xs font-heading text-gray-700 mb-1">
              Client ID
            </label>
            <input
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              className="w-full px-3 py-2 rounded-md border border-gray-200 bg-white text-sm font-body"
              placeholder="1"
            />
          </div>

          <div className="md:col-span-2 bg-gray-50 border border-gray-200 rounded-md p-3">
            <label className="block text-xs font-heading text-gray-700 mb-1">
              Catalogue scope
            </label>
            <div className="text-sm font-body text-gray-700">
              Showing grouped Critical Data Elements (CDEs). Tracked items are
              clickable.
            </div>
          </div>
        </div>

        {/* CDE catalogue */}
        <div className="bg-white border border-gray-200 rounded-halo p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-heading text-sm text-gray-900">
              Critical Data Elements
            </h4>
            <span className="text-[11px] font-mono text-gray-500">
              tracked: {Array.from(trackedConcepts).length} • planned:{" "}
              {CRITICAL_DATA_ELEMENTS.reduce(
                (acc, g) =>
                  acc + g.items.filter((i) => i.status === "planned").length,
                0
              )}
            </span>
          </div>

          <div className="space-y-6">
            {CRITICAL_DATA_ELEMENTS.map((section) => (
              <div key={section.group}>
                <div className="flex items-center justify-between mb-2">
                  <h5 className="font-heading text-sm text-gray-800">
                    {section.group}
                  </h5>
                </div>

                <div className="space-y-2">
                  {section.items.map((item) => {
                    const isTracked = item.status === "tracked";
                    const isClickable = isTracked && trackedConcepts.has(item.conceptId);

                    return (
                      <div
                        key={item.conceptId}
                        className={`flex items-center justify-between p-3 rounded-md border ${
                          isClickable
                            ? "bg-white border-halo-primary cursor-pointer hover:bg-teal-50"
                            : "bg-gray-50 border-gray-200 opacity-70"
                        }`}
                        onClick={() => {
                          if (isClickable) goToDetail(item.conceptId);
                        }}
                      >
                        <div>
                          <div className="font-body text-sm text-gray-900">
                            {item.displayName}
                          </div>
                          <div className="text-xs font-mono text-gray-500">
                            {item.conceptId}
                          </div>
                          {item.note && (
                            <div className="text-xs text-gray-500 mt-1">
                              {item.note}
                            </div>
                          )}
                        </div>

                        <div className="text-xs font-body">
                          {isClickable ? (
                            <span className="px-2 py-1 rounded-full bg-green-100 text-green-800 border border-green-200">
                              Tracked
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-600 border border-gray-200">
                              Planned
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 text-xs font-body text-gray-600">
            Tip: click a tracked element (e.g. <span className="font-mono">client.legal_name</span>) to drill into live lineage.
          </div>
        </div>
      </div>
    );
  }

  // =========================
  // VIEW 2: DETAIL (existing look & feel preserved)
  // =========================
  return (
    <div className="space-y-4">
      {/* Header row */}
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="font-fjalla text-base text-gray-900 tracking-wide">
            Business Data Lineage
          </h3>
          <p className="text-xs font-body text-gray-600">
            Attribute-level lineage with live value resolution
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* NEW: back to CDE list */}
          <button
            type="button"
            onClick={() => setView("cdeList")}
            className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white hover:bg-gray-50"
          >
            Critical Data Elements
          </button>

          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white hover:bg-gray-50"
            >
              Back
            </button>
          )}

          <button
            type="button"
            onClick={fetchLineage}
            className="px-3 py-2 rounded-md text-sm font-body text-white bg-halo-primary hover:opacity-90"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
          <label className="block text-xs font-heading text-gray-700 mb-1">
            Client ID
          </label>
          <input
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            className="w-full px-3 py-2 rounded-md border border-gray-200 bg-white text-sm font-body"
            placeholder="1"
          />
        </div>

        <div className="md:col-span-2 bg-gray-50 border border-gray-200 rounded-md p-3">
          <label className="block text-xs font-heading text-gray-700 mb-1">
            Concept ID
          </label>
          <input
            value={conceptId}
            onChange={(e) => setConceptId(e.target.value)}
            className="w-full px-3 py-2 rounded-md border border-gray-200 bg-white text-sm font-body"
            placeholder="client.legal_name"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={fetchLineage}
          className="px-4 py-2 rounded-md text-sm font-body text-white bg-halo-primary hover:opacity-90 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Loading…" : "Resolve lineage + value"}
        </button>

        {resolution?.status && (
          <Pill tone={statusTone}>
            Resolution: {String(resolution.status).toUpperCase()}
          </Pill>
        )}

        {error && <Pill tone="error">{error}</Pill>}
      </div>

      {/* Summary card */}
      <div className="bg-white border border-gray-200 rounded-halo p-4">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
          <div className="space-y-1">
            <div className="text-xs font-heading text-gray-500">Subject</div>
            <div className="text-sm font-body text-gray-900">
              {artifact?.subject?.display_name || "—"}
              <span className="text-xs text-gray-500">
                {" "}
                (client_id: {artifact?.subject?.entity_id || clientId || "—"})
              </span>
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-xs font-heading text-gray-500">Concept</div>
            <div className="text-sm font-body text-gray-900">
              {artifact?.concept?.display_name || "—"}
              <span className="text-xs text-gray-500">
                {" "}
                ({artifact?.concept?.concept_id || conceptId || "—"})
              </span>
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-xs font-heading text-gray-500">
              Resolved value
            </div>
            <div className="text-sm font-body text-gray-900">
              {resolvedValue == null ? "—" : String(resolvedValue)}
            </div>
          </div>
        </div>

        {/* NEW: Captured at / Evaluated at */}
        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="text-xs font-body text-gray-600">
            <span className="font-heading text-gray-500">Captured at:</span>{" "}
            {formatUtc(artifact?.captured_at)}
          </div>
          <div className="text-xs font-body text-gray-600">
            <span className="font-heading text-gray-500">Evaluated at:</span>{" "}
            {formatUtc(resolution?.evaluated_at)}
          </div>
        </div>

        {resolution?.details && (
          <div className="mt-3 text-xs font-body text-gray-600">
            {resolution.details}
          </div>
        )}
      </div>

      {/* Lineage detail */}
      <div className="bg-white border border-gray-200 rounded-halo p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-heading text-sm text-gray-900">Lineage path</h4>
          <span className="text-[11px] font-mono text-gray-500">
            artefact: {artifact?.artifact_type || "—"} v
            {artifact?.artifact_version || "—"}
          </span>
        </div>

        {!artifact?.lineage?.length ? (
          <div className="text-sm font-body text-gray-600">
            No lineage stages found in the artefact.
          </div>
        ) : (
          <div className="space-y-2">
            {artifact.lineage.map((step, idx) => (
              <div
                key={`${step.stage || "stage"}-${idx}`}
                className="border border-gray-200 rounded-md p-3 bg-gray-50"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="font-heading text-sm text-gray-900">
                    {String(step.stage || "stage").toUpperCase()}
                  </div>
                  <div className="text-[11px] font-mono text-gray-600">
                    {step.system ? `system=${step.system}` : ""}
                    {step.rule ? ` rule=${step.rule}` : ""}
                    {step.surface ? ` surface=${step.surface}` : ""}
                  </div>
                </div>

                {step.assertion && (
                  <div className="mt-2 text-sm font-body text-gray-700">
                    {step.assertion}
                  </div>
                )}

                {(step.component || step.field_label) && (
                  <div className="mt-2 text-xs font-body text-gray-600">
                    {step.component ? `Component: ${step.component}` : ""}
                    {step.component && step.field_label ? " • " : ""}
                    {step.field_label ? `Field: ${step.field_label}` : ""}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Raw payload (collapsible-ish) */}
      <div className="bg-white border border-gray-200 rounded-halo p-4">
        <h4 className="font-heading text-sm text-gray-900 mb-2">
          Raw response payload
        </h4>
        <pre className="whitespace-pre-wrap text-[11px] font-mono text-gray-800 bg-gray-50 border border-gray-200 rounded-md p-3 max-h-[260px] overflow-auto">
          {payload ? JSON.stringify(payload, null, 2) : "—"}
        </pre>
      </div>
    </div>
  );
}

