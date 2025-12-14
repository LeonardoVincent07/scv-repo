import React, { useMemo, useState } from "react";

function safeStr(v) {
  if (v === null || v === undefined) return "";
  return String(v);
}

function formatTs(ts) {
  if (!ts) return "—";
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return safeStr(ts);
  return d.toLocaleString();
}

function formatNum(v, digits = 2) {
  if (v === null || v === undefined || v === "") return "—";
  const n = typeof v === "number" ? v : Number(v);
  if (!Number.isFinite(n)) return safeStr(v);
  return n.toFixed(digits);
}

function StatusChip({ label }) {
  const text = (label || "").toLowerCase();

  let classes =
    "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-body border";

  if (text.includes("active") || text.includes("complete") || text.includes("passed") || text.includes("match")) {
    classes += " bg-emerald-50 text-emerald-700 border-emerald-200";
  } else if (text.includes("review") || text.includes("progress") || text.includes("pending")) {
    classes += " bg-amber-50 text-amber-700 border-amber-200";
  } else if (text.includes("fail") || text.includes("reject") || text.includes("error")) {
    classes += " bg-red-50 text-red-700 border-red-200";
  } else {
    classes += " bg-gray-50 text-gray-700 border-gray-200";
  }

  return <span className={classes}>{label || "—"}</span>;
}

function Metric({ label, value, mono = false }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <dt className="text-gray-500">{label}</dt>
      <dd className={`text-right text-gray-900 ${mono ? "font-mono" : ""}`}>
        {value || "—"}
      </dd>
    </div>
  );
}

function ConfidenceBar({ value }) {
  const num = typeof value === "number" ? value : Number(value);
  const pct = Number.isFinite(num) ? Math.max(0, Math.min(1, num)) * 100 : null;

  return (
    <div className="min-w-[140px]">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-body text-gray-600">Confidence</span>
        <span className="text-xs font-mono text-gray-700">
          {pct === null ? "—" : `${pct.toFixed(1)}%`}
        </span>
      </div>
      <div className="h-2 w-full rounded-full bg-gray-200 overflow-hidden">
        <div
          className="h-2 rounded-full bg-[#1A9988]"
          style={{ width: pct === null ? "0%" : `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function DetailedClientProfilePanel({
  profile,
  onClose,
  title = "Detailed client profile",
}) {
  const [expandedMatch, setExpandedMatch] = useState({});
  const [expandedAudit, setExpandedAudit] = useState({});
  const [expandedTrade, setExpandedTrade] = useState({});

  const header = useMemo(() => {
    const clientId = safeStr(profile?.client_id || profile?.clientId || "");
    const name = safeStr(profile?.name || profile?.full_name || profile?.fullName || "");
    const segment = safeStr(profile?.segment || "");
    const risk = safeStr(profile?.risk_rating || profile?.riskRating || "");
    const lastUpdated =
      profile?.last_updated_at ||
      profile?.lastUpdatedAt ||
      profile?.operational_state?.as_of ||
      "";

    const status =
      safeStr(profile?.operational_state?.status || profile?.status || profile?.current_status || "");

    return {
      clientId: clientId || "—",
      name: name || "—",
      segment: segment || "—",
      risk: risk || "—",
      lastUpdated: lastUpdated ? formatTs(lastUpdated) : "—",
      status: status || "—",
    };
  }, [profile]);

  const operational = profile?.operational_state || null;
  const reg = profile?.regulatory_enrichment || null;

  const matchDecisions = Array.isArray(profile?.match_decisions)
    ? profile.match_decisions
    : [];

  const evidenceArtefacts = Array.isArray(profile?.evidence_artefacts)
    ? profile.evidence_artefacts
    : [];

  const auditTrail = Array.isArray(profile?.audit_trail) ? profile.audit_trail : [];

  // NEW: Trade history (reads from real backend payload; no mocking)
  const tradeHistory = useMemo(() => {
    const arr = Array.isArray(profile?.trade_history)
      ? profile.trade_history
      : Array.isArray(profile?.trades)
        ? profile.trades
        : [];
    // Sort newest first if trade_date present (keeps UI stable)
    return [...arr].sort((a, b) => {
      const da = new Date(a?.trade_date || a?.tradeDate || 0).getTime();
      const db = new Date(b?.trade_date || b?.tradeDate || 0).getTime();
      return (Number.isFinite(db) ? db : 0) - (Number.isFinite(da) ? da : 0);
    });
  }, [profile]);

  return (
    <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mt-6">
      {/* Header */}
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="font-heading text-lg text-gray-800">{title}</h2>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="text-sm font-body text-gray-900">{header.name}</span>
            <span className="text-xs font-mono text-gray-500">({header.clientId})</span>
            <span className="text-xs font-body text-gray-400">•</span>
            <span className="text-xs font-body text-gray-600">Segment: {header.segment}</span>
            <span className="text-xs font-body text-gray-400">•</span>
            <span className="text-xs font-body text-gray-600">Risk: {header.risk}</span>
          </div>
        </div>

        <div className="flex flex-col items-start md:items-end gap-2">
          <div className="flex items-center gap-2">
            <StatusChip label={header.status} />
            <span className="text-xs font-body text-gray-500">
              Last update: <span className="font-mono">{header.lastUpdated}</span>
            </span>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center justify-center px-3 py-1.5 rounded-md text-sm font-body font-medium bg-gray-100 text-gray-800 border border-gray-200 shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0"
          >
            Close
          </button>
        </div>
      </div>

      {/* Two-column content */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* LEFT COLUMN */}
        <div className="space-y-6">
          {/* 1. Client Information */}
          <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6">
            <h3 className="font-heading text-base text-gray-800 mb-4">Client information</h3>

            <dl className="space-y-2 text-sm font-body text-gray-800">
              <Metric label="Client ID" value={safeStr(profile?.client_id)} mono />
              <Metric label="Full name" value={safeStr(profile?.name)} />
              <Metric label="Primary email" value={safeStr(profile?.email)} />
              <Metric label="Primary phone" value={safeStr(profile?.phone)} />
              <Metric label="Country" value={safeStr(profile?.country)} />
              <Metric label="Primary address" value={safeStr(profile?.primary_address)} />
              <Metric label="Segment" value={safeStr(profile?.segment)} />
              <Metric label="Risk rating" value={safeStr(profile?.risk_rating)} />
            </dl>

            {/* Key metrics */}
            <div className="mt-4 bg-gray-50 rounded-lg border border-gray-200 p-4">
              <h4 className="font-heading text-sm text-gray-700 mb-2">Key metrics</h4>
              <dl className="space-y-2 text-sm font-body text-gray-800">
                <Metric label="Current status" value={safeStr(header.status)} />
                <Metric label="Last updated" value={header.lastUpdated} mono />
                {operational && (
                  <>
                    <Metric label="Processing stage" value={safeStr(operational.processing_stage)} />
                    <Metric label="Message" value={safeStr(operational.message)} />
                  </>
                )}
              </dl>
            </div>
          </div>

          {/* 3. Regulatory Enrichment */}
          <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6">
            <h3 className="font-heading text-base text-gray-800 mb-4">Regulatory enrichment</h3>

            {!reg ? (
              <p className="text-sm font-body text-gray-500">
                No regulatory enrichment available.
              </p>
            ) : (
              <dl className="space-y-2 text-sm font-body text-gray-800">
                <Metric label="FATCA status" value={safeStr(reg.fatca_status)} />
                <Metric label="KYC status" value={safeStr(reg.kyc_overall_status || reg.kyc_status)} />
                <Metric label="Risk assessment" value={safeStr(reg.risk_assessment)} />
                <Metric label="Onboarding status" value={safeStr(reg.onboarding_status)} />
                <Metric label="CRS status" value={safeStr(reg.crs_status)} />
                {reg.derived_risk_notes && (
                  <div className="mt-3 text-sm font-body text-gray-800">
                    <div className="text-gray-500 mb-1">Notes</div>
                    <div className="bg-gray-50 rounded-md border border-gray-200 p-3 text-gray-900">
                      {safeStr(reg.derived_risk_notes)}
                    </div>
                  </div>
                )}
              </dl>
            )}
          </div>

          {/* 4. Evidence Artefacts */}
          <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6">
            <h3 className="font-heading text-base text-gray-800 mb-4">Evidence artefacts</h3>

            {evidenceArtefacts.length === 0 ? (
              <p className="text-sm font-body text-gray-500">
                No evidence artefacts available.
              </p>
            ) : (
              <div className="overflow-auto border border-gray-200 rounded-md">
                <table className="min-w-full text-sm font-body">
                  <thead className="bg-gray-50 text-gray-700">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium">Type</th>
                      <th className="text-left px-4 py-3 font-medium">Created</th>
                      <th className="text-left px-4 py-3 font-medium">Source</th>
                      <th className="text-left px-4 py-3 font-medium">Reference</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {evidenceArtefacts.map((a, idx) => (
                      <tr key={a.artefact_id || a.id || idx}>
                        <td className="px-4 py-3 text-gray-900">
                          {safeStr(a.artefact_type || a.document_type || a.type) || "—"}
                        </td>
                        <td className="px-4 py-3 text-gray-900 font-mono text-xs">
                          {formatTs(a.created_at || a.uploaded_at || a.upload_date)}
                        </td>
                        <td className="px-4 py-3 text-gray-900">
                          {safeStr(a.source_system || a.source) || "—"}
                        </td>
                        <td className="px-4 py-3 text-gray-900 font-mono text-xs">
                          {safeStr(a.storage_ref || a.link || a.reference) || "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-6">
          {/* 2. Match Decisions */}
          <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6">
            <h3 className="font-heading text-base text-gray-800 mb-4">Match decisions</h3>

            {matchDecisions.length === 0 ? (
              <p className="text-sm font-body text-gray-500">
                No match decisions available.
              </p>
            ) : (
              <div className="overflow-auto border border-gray-200 rounded-md">
                <table className="min-w-full text-sm font-body">
                  <thead className="bg-gray-50 text-gray-700">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium">Decided</th>
                      <th className="text-left px-4 py-3 font-medium">Decision</th>
                      <th className="text-left px-4 py-3 font-medium">Source</th>
                      <th className="text-left px-4 py-3 font-medium">IDs</th>
                      <th className="text-left px-4 py-3 font-medium">Confidence</th>
                      <th className="text-left px-4 py-3 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {matchDecisions.map((m, idx) => {
                      const key = m.match_decision_id || m.id || idx;
                      const isOpen = !!expandedMatch[key];

                      return (
                        <React.Fragment key={key}>
                          <tr>
                            <td className="px-4 py-3 font-mono text-xs text-gray-900">
                              {formatTs(m.decided_at)}
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              <StatusChip label={safeStr(m.decision)} />
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              {safeStr(m.source_system || m.system) || "—"}
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              <div className="text-xs font-mono text-gray-700">
                                src: {safeStr(m.source_record_id) || "—"}
                              </div>
                              <div className="text-xs font-mono text-gray-700">
                                match: {safeStr(m.matched_client_id) || "—"}
                              </div>
                            </td>
                            <td className="px-4 py-3">
                              <ConfidenceBar value={m.confidence} />
                            </td>
                            <td className="px-4 py-3">
                              <button
                                type="button"
                                className="inline-flex items-center justify-center px-3 py-1.5 rounded-md text-sm text-gray-900 bg-[rgb(205,226,235)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:shadow-sm"
                                onClick={() =>
                                  setExpandedMatch((prev) => ({
                                    ...prev,
                                    [key]: !prev[key],
                                  }))
                                }
                              >
                                {isOpen ? "Hide" : "View"}
                              </button>
                            </td>
                          </tr>

                          {isOpen && (
                            <tr className="bg-gray-50">
                              <td colSpan={6} className="px-4 py-3">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div className="bg-white border border-gray-200 rounded-md p-3">
                                    <div className="text-xs font-body text-gray-600 mb-2">
                                      Rule hits
                                    </div>
                                    <pre className="whitespace-pre-wrap text-[11px] font-mono text-gray-800">
                                      {JSON.stringify(m.rule_hits || {}, null, 2)}
                                    </pre>
                                  </div>
                                  <div className="bg-white border border-gray-200 rounded-md p-3">
                                    <div className="text-xs font-body text-gray-600 mb-2">
                                      Conflict summary
                                    </div>
                                    <pre className="whitespace-pre-wrap text-[11px] font-mono text-gray-800">
                                      {JSON.stringify(m.conflict_summary || {}, null, 2)}
                                    </pre>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* NEW: Trade History */}
          <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6">
            <h3 className="font-heading text-base text-gray-800 mb-4">Trade history</h3>

            {tradeHistory.length === 0 ? (
              <p className="text-sm font-body text-gray-500">
                No trade history available.
              </p>
            ) : (
              <div className="overflow-auto border border-gray-200 rounded-md">
                <table className="min-w-full text-sm font-body">
                  <thead className="bg-gray-50 text-gray-700">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium">Trade date</th>
                      <th className="text-left px-4 py-3 font-medium">Asset class</th>
                      <th className="text-left px-4 py-3 font-medium">Instrument</th>
                      <th className="text-left px-4 py-3 font-medium">Dir</th>
                      <th className="text-left px-4 py-3 font-medium">Qty</th>
                      <th className="text-left px-4 py-3 font-medium">Price</th>
                      <th className="text-left px-4 py-3 font-medium">PnL</th>
                      <th className="text-left px-4 py-3 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {tradeHistory.map((t, idx) => {
                      const key = t.trade_id || t.id || idx;
                      const isOpen = !!expandedTrade[key];

                      const tradeDate = t.trade_date || t.tradeDate;
                      const assetClass = t.asset_class || t.assetClass;
                      const instrument = t.instrument || t.symbol || t.ccy_pair || t.ccyPair;
                      const direction = t.direction || t.side;
                      const qty = t.quantity ?? t.qty ?? t.notional;
                      const price = t.price ?? t.rate;
                      const pnl = t.pnl ?? t.p_and_l ?? t.pAndL;

                      return (
                        <React.Fragment key={key}>
                          <tr>
                            <td className="px-4 py-3 font-mono text-xs text-gray-900">
                              {formatTs(tradeDate)}
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              {safeStr(assetClass) || "—"}
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              {safeStr(instrument) || "—"}
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              {safeStr(direction) || "—"}
                            </td>
                            <td className="px-4 py-3 font-mono text-xs text-gray-900">
                              {qty === null || qty === undefined ? "—" : safeStr(qty)}
                            </td>
                            <td className="px-4 py-3 font-mono text-xs text-gray-900">
                              {price === null || price === undefined ? "—" : safeStr(price)}
                            </td>
                            <td className="px-4 py-3 font-mono text-xs text-gray-900">
                              {pnl === null || pnl === undefined ? "—" : safeStr(pnl)}
                            </td>
                            <td className="px-4 py-3">
                              <button
                                type="button"
                                className="inline-flex items-center justify-center px-3 py-1.5 rounded-md text-sm text-gray-900 bg-[rgb(205,226,235)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:shadow-sm"
                                onClick={() =>
                                  setExpandedTrade((prev) => ({
                                    ...prev,
                                    [key]: !prev[key],
                                  }))
                                }
                              >
                                {isOpen ? "Hide" : "View"}
                              </button>
                            </td>
                          </tr>

                          {isOpen && (
                            <tr className="bg-gray-50">
                              <td colSpan={8} className="px-4 py-3">
                                <div className="bg-white border border-gray-200 rounded-md p-3">
                                  <div className="text-xs font-body text-gray-600 mb-2">
                                    Full trade record
                                  </div>
                                  <pre className="whitespace-pre-wrap text-[11px] font-mono text-gray-800">
                                    {JSON.stringify(t, null, 2)}
                                  </pre>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* 5. Audit Trail */}
          <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6">
            <h3 className="font-heading text-base text-gray-800 mb-4">Audit trail</h3>

            {auditTrail.length === 0 ? (
              <p className="text-sm font-body text-gray-500">
                No audit events available.
              </p>
            ) : (
              <div className="overflow-auto border border-gray-200 rounded-md">
                <table className="min-w-full text-sm font-body">
                  <thead className="bg-gray-50 text-gray-700">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium">When</th>
                      <th className="text-left px-4 py-3 font-medium">Event type</th>
                      <th className="text-left px-4 py-3 font-medium">Actor</th>
                      <th className="text-left px-4 py-3 font-medium">Details</th>
                      <th className="text-left px-4 py-3 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {auditTrail.map((a, idx) => {
                      const key = a.audit_event_id || a.id || idx;
                      const isOpen = !!expandedAudit[key];

                      const summary =
                        a?.details?.summary ||
                        a?.summary ||
                        a?.details_text ||
                        a?.details?.message ||
                        "";

                      return (
                        <React.Fragment key={key}>
                          <tr>
                            <td className="px-4 py-3 font-mono text-xs text-gray-900">
                              {formatTs(a.occurred_at || a.timestamp || a.created_at)}
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              {safeStr(a.event_type) || "—"}
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              {safeStr(a.actor) || "—"}
                            </td>
                            <td className="px-4 py-3 text-gray-900">
                              {summary ? (
                                <span className="text-sm font-body text-gray-800">
                                  {safeStr(summary)}
                                </span>
                              ) : (
                                <span className="text-sm font-body text-gray-500">—</span>
                              )}
                            </td>
                            <td className="px-4 py-3">
                              <button
                                type="button"
                                className="inline-flex items-center justify-center px-3 py-1.5 rounded-md text-sm text-gray-900 bg-[rgb(205,226,235)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:shadow-sm"
                                onClick={() =>
                                  setExpandedAudit((prev) => ({
                                    ...prev,
                                    [key]: !prev[key],
                                  }))
                                }
                              >
                                {isOpen ? "Hide" : "View"}
                              </button>
                            </td>
                          </tr>

                          {isOpen && (
                            <tr className="bg-gray-50">
                              <td colSpan={5} className="px-4 py-3">
                                <div className="bg-white border border-gray-200 rounded-md p-3">
                                  <div className="text-xs font-body text-gray-600 mb-2">
                                    Full details
                                  </div>
                                  <pre className="whitespace-pre-wrap text-[11px] font-mono text-gray-800">
                                    {JSON.stringify(a.details || a, null, 2)}
                                  </pre>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

        </div>
      </div>
    </section>
  );
}

