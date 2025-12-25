import React, { useEffect, useMemo, useState } from "react";
import MissionLogPanel from "./MissionLogPanel";
import MissionAtlasPanel from "./MissionAtlasPanel";
import DetailedClientProfilePanel from "./DetailedClientProfilePanel";
import logo from "./assets/m7_single_client_view.png";

const BACKEND_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [clientId, setClientId] = useState("");
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [sources, setSources] = useState([]);
  const [error, setError] = useState("");

  // NEW: toggle detailed panel (no routing, no landing regression)
  const [showDetailedProfile, setShowDetailedProfile] = useState(false);

  // Client index (landing screen list)
  const [clientIndex, setClientIndex] = useState([]); // [{client_id,name,risk_rating,status,segment}]
  const [clients, setClients] = useState([]); // datalist IDs
  const [clientsLoading, setClientsLoading] = useState(false);
  const [clientIndexError, setClientIndexError] = useState("");

  // Landing screen search & filters
  const [clientSearch, setClientSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");

  // 'scv' | 'missionLog' | 'missionAtlas'
  const [activeView, setActiveView] = useState("scv");

  // NEW: Pre-Matched Records (ST-05 demo ingestion)
  const [preMatchedRecords, setPreMatchedRecords] = useState([]);
  const [preMatchedLoading, setPreMatchedLoading] = useState(false);
  const [preMatchedError, setPreMatchedError] = useState("");

  const fetchPreMatched = async () => {
    setPreMatchedLoading(true);
    setPreMatchedError("");

    try {
      const res = await fetch(
        `${BACKEND_BASE_URL}/ingestion/crm/contacts?source_system=DEMO_CRM`
      );
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(
          detail.detail || `Failed to fetch pre-matched records (${res.status}).`
        );
      }

      const data = await res.json();
      const records = Array.isArray(data?.records) ? data.records : [];
      setPreMatchedRecords(records);
    } catch (err) {
      setPreMatchedRecords([]);
      setPreMatchedError(err?.message || "Failed to fetch pre-matched records.");
    } finally {
      setPreMatchedLoading(false);
    }
  };

  // Fetch client index (best-effort; UI degrades gracefully if endpoint not available)
  useEffect(() => {
    let cancelled = false;

    const normaliseRow = (x) => {
      if (typeof x === "string") {
        return {
          client_id: x,
          name: "",
          risk_rating: "",
          status: "",
          segment: "",
        };
      }

      const client_id = x?.client_id ?? x?.clientId ?? x?.id ?? "";
      const name =
        x?.name ??
        x?.full_name ??
        x?.fullName ??
        x?.client_name ??
        x?.clientName ??
        "";
      const risk_rating = x?.risk_rating ?? x?.riskRating ?? x?.risk ?? "";
      const status =
        x?.status ?? x?.current_status ?? x?.currentStatus ?? x?.state ?? "";
      const segment = x?.segment ?? x?.client_segment ?? x?.clientSegment ?? "";

      return {
        client_id: String(client_id || "").trim(),
        name: String(name || "").trim(),
        risk_rating: String(risk_rating || "").trim(),
        status: String(status || "").trim(),
        segment: String(segment || "").trim(),
      };
    };

    const fetchClientIndex = async () => {
      setClientsLoading(true);
      setClientIndexError("");

      try {
        const res = await fetch(`${BACKEND_BASE_URL}/clients/`);
        if (!res.ok) {
          throw new Error(`Client list not available (${res.status}).`);
        }

        const data = await res.json();
        if (cancelled) return;

        const raw = Array.isArray(data) ? data : data?.clients || [];
        const rows = raw
          .map(normaliseRow)
          .filter((r) => r.client_id && r.client_id.length > 0);

        const ids = rows.map((r) => r.client_id);

        setClientIndex(rows);
        setClients(ids);
      } catch (err) {
        console.warn(err);
        if (!cancelled) {
          setClientIndex([]);
          setClients([]);
          setClientIndexError(err?.message || "Client list not available.");
        }
      } finally {
        if (!cancelled) setClientsLoading(false);
      }
    };

    fetchClientIndex();

    // NEW: fetch pre-matched records on landing load
    fetchPreMatched();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredClientIndex = useMemo(() => {
    const q = clientSearch.trim().toLowerCase();

    return clientIndex.filter((c) => {
      const matchesSearch =
        !q ||
        c.client_id.toLowerCase().includes(q) ||
        (c.name || "").toLowerCase().includes(q) ||
        (c.segment || "").toLowerCase().includes(q) ||
        (c.status || "").toLowerCase().includes(q) ||
        (c.risk_rating || "").toLowerCase().includes(q);

      const matchesRisk =
        riskFilter === "All" ||
        (c.risk_rating || "").toLowerCase() === riskFilter.toLowerCase();

      const matchesStatus =
        statusFilter === "All" ||
        (c.status || "").toLowerCase() === statusFilter.toLowerCase();

      return matchesSearch && matchesRisk && matchesStatus;
    });
  }, [clientIndex, clientSearch, riskFilter, statusFilter]);

  const distinctRiskRatings = useMemo(() => {
    const set = new Set(
      clientIndex
        .map((c) => (c.risk_rating || "").trim())
        .filter((v) => v.length > 0)
    );
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [clientIndex]);

  const distinctStatuses = useMemo(() => {
    const set = new Set(
      clientIndex
        .map((c) => (c.status || "").trim())
        .filter((v) => v.length > 0)
    );
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [clientIndex]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!clientId.trim()) {
      setError("Please enter a Client ID.");
      return;
    }

    setError("");
    setLoading(true);
    setProfile(null);
    setSources([]);
    setShowDetailedProfile(false); // NEW: reset panel on new fetch

    try {
      const encodedId = encodeURIComponent(clientId.trim());

      const profileRes = await fetch(
        `${BACKEND_BASE_URL}/clients/${encodedId}/profile`
      );
      if (!profileRes.ok) {
        const detail = await profileRes.json().catch(() => ({}));
        throw new Error(detail.detail || "Failed to fetch profile.");
      }
      const profileJson = await profileRes.json();

      // Keep existing logging
      console.log("Profile Response:", profileJson);

      setProfile(profileJson);

      const sourcesRes = await fetch(
        `${BACKEND_BASE_URL}/clients/${encodedId}/sources`
      );
      const sourcesJson = sourcesRes.ok ? await sourcesRes.json() : [];

      setSources(sourcesJson);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const isMissionLog = activeView === "missionLog";
  const isMissionAtlas = activeView === "missionAtlas";

  const viewDetailsDisabled = !profile;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header with MissionHalo logo */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <img
            src={logo}
            alt="M7 single client view"
            className="h-16 w-auto md:h-20"
          />
        </div>

        {/* Mission buttons bar */}
        <div className="bg-gray-100 border-t border-gray-200">
          <div className="max-w-6xl mx-auto px-4 py-3 flex justify-end gap-4">
            <button
              type="button"
              style={{ fontFamily: "Fjalla One" }}
              className="inline-flex items-center justify-center px-8 py-2.5 rounded-md text-base text-gray-900 bg-[rgb(176,192,159)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:shadow-sm"
              onClick={() =>
                window.open(
                  `${window.location.origin}/MissionSmith-M7-SingleClientView.html`,
                  "_blank",
                  "noopener,noreferrer"
                )
              }
            >
              MissionSmith
            </button>

            <button
              type="button"
              style={{ fontFamily: "Fjalla One" }}
              className="inline-flex items-center justify-center px-8 py-2.5 rounded-md text-base text-gray-900 bg-[rgb(205,226,235)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:shadow-sm"
              onClick={() => setActiveView("missionAtlas")}
            >
              MissionAtlas
            </button>

            <button
              type="button"
              style={{ fontFamily: "Fjalla One" }}
              className="inline-flex items-center justify-center px-8 py-2.5 rounded-md text-base text-gray-900 bg-[rgb(241,205,86)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:shadow-sm"
              onClick={() => setActiveView("missionLog")}
            >
              MissionLog
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        {isMissionLog ? (
          <MissionLogPanel setActiveView={setActiveView} />
        ) : isMissionAtlas ? (
          <MissionAtlasPanel />
        ) : (
          <>
            {/* Find client profile (always shown in SCV view) */}
            <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="font-heading text-lg text-gray-800 mb-4">
                Find client profile
              </h2>

              <form
                onSubmit={handleSubmit}
                className="flex flex-col md:flex-row gap-4 items-stretch md:items-end"
              >
                <div className="flex-1">
                  <label
                    htmlFor="clientId"
                    className="block text-sm font-body text-gray-700 mb-1"
                  >
                    Client ID
                  </label>
                  <input
                    id="clientId"
                    type="text"
                    value={clientId}
                    onChange={(e) => setClientId(e.target.value)}
                    className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-body text-gray-900 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1A9988]"
                    placeholder="e.g. client-001"
                    list="clientIdOptions"
                  />
                  <datalist id="clientIdOptions">
                    {clients.map((id) => (
                      <option key={id} value={id} />
                    ))}
                  </datalist>

                  {clientsLoading && (
                    <p className="mt-2 text-xs font-body text-gray-500">
                      Loading client IDs…
                    </p>
                  )}
                </div>

                <div className="flex flex-row gap-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className={`
                      inline-flex items-center justify-center
                      px-4 py-2 rounded-md
                      bg-[#1A9988] text-white
                      font-body text-sm font-medium
                      shadow-sm
                      transition-colors transition-transform duration-150
                      hover:bg-[#178c7d] hover:-translate-y-0.5 hover:shadow-md
                      active:bg-[#147c6f] active:translate-y-0
                      ${loading ? "opacity-60 cursor-not-allowed" : ""}
                    `}
                  >
                    {loading ? "Loading..." : "Get profile"}
                  </button>

                  {/* NOW WIRED: Detailed Profile button */}
                  <button
                    type="button"
                    disabled={viewDetailsDisabled}
                    className={`
                      inline-flex items-center justify-center
                      px-4 py-2 rounded-md
                      font-body text-sm font-medium
                      shadow-sm
                      transition-colors transition-transform duration-150
                      ${
                        viewDetailsDisabled
                          ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                          : "bg-[rgb(176,192,159)] text-gray-900 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0"
                      }
                    `}
                    onClick={() => {
                      if (!profile) return;
                      setShowDetailedProfile(true);
                      // small UX: nudge scroll to panel on click
                      setTimeout(() => {
                        const el = document.getElementById("scv-detailed-profile");
                        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
                      }, 50);
                    }}
                    title={
                      viewDetailsDisabled ? "Load a profile first" : "View detailed profile"
                    }
                  >
                    View detailed profile
                  </button>
                </div>
              </form>

              {error && (
                <p className="mt-3 text-sm font-body text-red-600">{error}</p>
              )}
            </section>

            {/* Initial landing screen (only when no profile): Client Overview + Pre-Matched */}
            {!profile && (
              <>
                {/* Client overview */}
                <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
                  <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
                    <div>
                      <h2 className="font-heading text-lg text-gray-800">
                        Client overview
                      </h2>
                      <p className="mt-1 text-sm font-body text-gray-600">
                        Search and filter clients, then navigate to the detailed profile.
                      </p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                      <div className="flex-1 sm:w-64">
                        <label className="block text-sm font-body text-gray-700 mb-1">
                          Search
                        </label>
                        <input
                          type="text"
                          value={clientSearch}
                          onChange={(e) => setClientSearch(e.target.value)}
                          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-body text-gray-900 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1A9988]"
                          placeholder="Name, ID, segment…"
                        />
                      </div>

                      <div className="sm:w-44">
                        <label className="block text-sm font-body text-gray-700 mb-1">
                          Risk rating
                        </label>
                        <select
                          value={riskFilter}
                          onChange={(e) => setRiskFilter(e.target.value)}
                          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-body text-gray-900 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1A9988]"
                        >
                          <option value="All">All</option>
                          {distinctRiskRatings.map((r) => (
                            <option key={r} value={r}>
                              {r}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="sm:w-44">
                        <label className="block text-sm font-body text-gray-700 mb-1">
                          Status
                        </label>
                        <select
                          value={statusFilter}
                          onChange={(e) => setStatusFilter(e.target.value)}
                          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-body text-gray-900 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1A9988]"
                        >
                          <option value="All">All</option>
                          {distinctStatuses.map((s) => (
                            <option key={s} value={s}>
                              {s}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className="mt-5">
                    {clientsLoading ? (
                      <p className="text-sm font-body text-gray-500">
                        Loading client list…
                      </p>
                    ) : clientIndexError ? (
                      <p className="text-sm font-body text-gray-500">
                        {clientIndexError}
                      </p>
                    ) : filteredClientIndex.length === 0 ? (
                      <p className="text-sm font-body text-gray-500">
                        No clients match your search/filters.
                      </p>
                    ) : (
                      <div className="overflow-auto border border-gray-200 rounded-md">
                        <table className="min-w-full text-sm font-body">
                          <thead className="bg-gray-50 text-gray-700">
                            <tr>
                              <th className="text-left px-4 py-3 font-medium">
                                Client ID
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Name
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Risk
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Status
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Segment
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Action
                              </th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-200">
                            {filteredClientIndex.map((c) => (
                              <tr key={c.client_id} className="bg-white">
                                <td className="px-4 py-3 font-mono text-gray-900">
                                  {c.client_id}
                                </td>
                                <td className="px-4 py-3 text-gray-900">
                                  {c.name || "—"}
                                </td>
                                <td className="px-4 py-3 text-gray-900">
                                  {c.risk_rating || "—"}
                                </td>
                                <td className="px-4 py-3 text-gray-900">
                                  {c.status || "—"}
                                </td>
                                <td className="px-4 py-3 text-gray-900">
                                  {c.segment || "—"}
                                </td>
                                <td className="px-4 py-3">
                                  <button
                                    type="button"
                                    className="inline-flex items-center justify-center px-3 py-1.5 rounded-md text-sm text-gray-900 bg-[rgb(205,226,235)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:shadow-sm"
                                    onClick={() => setClientId(c.client_id)}
                                    title="Populate Client ID"
                                  >
                                    Select
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </section>

                {/* Pre-Matched Records */}
                <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="font-heading text-lg text-gray-800">
                      Pre-Matched Records
                    </h2>

                    <button
                      type="button"
                      style={{ fontFamily: "Fjalla One" }}
                      className="inline-flex items-center justify-center px-5 py-2 rounded-md text-sm text-gray-900 bg-[rgb(205,226,235)] shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:shadow-sm"
                      onClick={fetchPreMatched}
                      disabled={preMatchedLoading}
                      title="Refresh pre-matched records"
                    >
                      {preMatchedLoading ? "Refreshing…" : "Refresh"}
                    </button>
                  </div>

                  {preMatchedError && (
                    <p className="text-sm font-body text-red-600">{preMatchedError}</p>
                  )}

                  {!preMatchedError && preMatchedRecords.length === 0 ? (
                    <p className="text-sm font-body text-gray-500">
                      No pre-matched records.
                    </p>
                  ) : (
                    preMatchedRecords.length > 0 && (
                      <div className="overflow-auto border border-gray-200 rounded-md">
                        <table className="min-w-full text-sm font-body">
                          <thead className="bg-gray-50 text-gray-700">
                            <tr>
                              <th className="text-left px-4 py-3 font-medium">
                                Source
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Record ID
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Name
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Email
                              </th>
                              <th className="text-left px-4 py-3 font-medium">
                                Created
                              </th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-200">
                            {preMatchedRecords.map((r) => {
                              const name = `${r.first_name || ""} ${r.last_name || ""}`.trim();
                              const created =
                                r.created_at
                                  ? String(r.created_at).replace("T", " ").slice(0, 19)
                                  : "—";

                              return (
                                <tr key={r.id} className="bg-white">
                                  <td className="px-4 py-3 text-gray-900">
                                    {r.source_system || "—"}
                                  </td>
                                  <td className="px-4 py-3 font-mono text-gray-900">
                                    {r.source_record_id || "—"}
                                  </td>
                                  <td className="px-4 py-3 text-gray-900">
                                    {name || "—"}
                                  </td>
                                  <td className="px-4 py-3 text-gray-900">
                                    {r.email || "—"}
                                  </td>
                                  <td className="px-4 py-3 text-gray-900">
                                    {created}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )
                  )}
                </section>
              </>
            )}

            {/* SCV layout grid (only when profile loaded) */}
            {profile && (
              <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
                {/* Left column: core profile */}
                <div className="space-y-4">
                  <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6">
                    <h3 className="font-heading text-lg text-gray-800 mb-4">
                      Client profile
                    </h3>

                    <dl className="space-y-2 text-sm font-body text-gray-800">
                      <div className="flex justify-between gap-4">
                        <dt className="text-gray-500">Client ID</dt>
                        <dd className="font-mono text-gray-900">
                          {profile.client_id || "—"}
                        </dd>
                      </div>

                      <div className="flex justify-between gap-4">
                        <dt className="text-gray-500">Full name</dt>
                        <dd className="text-right">{profile?.name || "—"}</dd>
                      </div>

                      <div className="flex justify-between gap-4">
                        <dt className="text-gray-500">Primary email</dt>
                        <dd className="text-right">{profile?.email || "—"}</dd>
                      </div>

                      <div className="flex justify-between gap-4">
                        <dt className="text-gray-500">Primary phone</dt>
                        <dd className="text-right">{profile?.phone || "—"}</dd>
                      </div>
                    </dl>
                  </div>

                  {/* Addresses */}
                  {profile?.addresses?.length > 0 && (
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <h4 className="font-heading text-sm text-gray-700 mb-2">
                        Addresses
                      </h4>

                      <ul className="space-y-2 text-sm font-body">
                        {profile.addresses.map((addr, idx) => (
                          <li
                            key={idx}
                            className="border-b border-gray-200 pb-2 last:border-none"
                          >
                            <div className="text-gray-900">
                              {[
                                addr.line1,
                                addr.line2,
                                addr.city,
                                addr.postcode,
                                addr.country,
                              ]
                                .filter(Boolean)
                                .join(", ")}
                            </div>

                            <div className="text-xs text-gray-500 mt-1">
                              Source: {addr.source || "—"}
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Right column: raw sources + lineage */}
                <div>
                  <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 h-full">
                    <h3 className="font-heading text-lg text-gray-800 mb-4">
                      Raw sources
                    </h3>

                    {sources.length > 0 ? (
                      <div className="space-y-3 text-xs font-mono bg-gray-50 rounded-lg p-3 border border-gray-200 max-h-[400px] overflow-auto">
                        {sources.map((src) => (
                          <div
                            key={src.id}
                            className="bg-white border border-gray-200 rounded-md p-2"
                          >
                            <div className="flex justify-between items-center mb-1">
                              <span className="font-body text-xs text-gray-600">
                                {src.system}
                              </span>
                              <span className="font-body text-[10px] text-gray-400">
                                client_id: {src.client_id}
                              </span>
                            </div>

                            <pre className="whitespace-pre-wrap text-[11px] text-gray-800">
                              {JSON.stringify(src.payload, null, 2)}
                            </pre>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm font-body text-gray-500">
                        No raw sources available.
                      </p>
                    )}

                    {profile?.lineage && (
                      <>
                        <h4 className="font-heading text-sm text-gray-700 mt-4 mb-2">
                          Lineage
                        </h4>
                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200 text-xs font-body max-h-[200px] overflow-auto">
                          <pre className="whitespace-pre-wrap text-[11px] text-gray-800">
                            {JSON.stringify(profile.lineage, null, 2)}
                          </pre>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </section>
            )}

            {/* Detailed Profile panel (below existing SCV grid, no regression) */}
            {profile && showDetailedProfile && (
              <div id="scv-detailed-profile">
                <DetailedClientProfilePanel
                  profile={profile}
                  onClose={() => setShowDetailedProfile(false)}
                />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;

























