import React, { useState } from "react";

const BACKEND_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [clientId, setClientId] = useState("");
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [sources, setSources] = useState([]);
  const [error, setError] = useState("");

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

    try {
      const profileRes = await fetch(
        `${BACKEND_BASE_URL}/clients/${encodeURIComponent(clientId)}/profile`
      );
      if (!profileRes.ok) {
        const detail = await profileRes.json().catch(() => ({}));
        throw new Error(detail.detail || "Failed to fetch profile.");
      }
      const profileJson = await profileRes.json();

      const sourcesRes = await fetch(
        `${BACKEND_BASE_URL}/clients/${encodeURIComponent(clientId)}/sources`
      );
      let sourcesJson = [];
      if (sourcesRes.ok) {
        sourcesJson = await sourcesRes.json();
      }

      setProfile(profileJson);
      setSources(sourcesJson);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top bar */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-heading text-halo-primary">
              Single Client View
            </span>
            <span className="text-sm font-body text-gray-500">
              MissionHalo MVP
            </span>
          </div>
          <span className="text-xs font-body text-gray-400">
            Backend: {BACKEND_BASE_URL}
          </span>
        </div>
      </header>

      {/* Main layout */}
      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Search card */}
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
                className="block text-sm font-body text-gray-600 mb-1"
              >
                Client ID
              </label>
              <input
                id="clientId"
                type="text"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-halo-primary focus:border-halo-primary font-body text-sm"
                placeholder="e.g. 123"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center px-4 py-2 rounded-md font-body text-sm font-medium bg-halo-primary text-white hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Loading…" : "Get profile"}
            </button>
          </form>

          {error && (
            <p className="mt-3 text-sm text-orange-700 bg-orange-50 border border-orange-200 rounded-md px-3 py-2 font-body">
              {error}
            </p>
          )}
        </section>

        {/* Content grid */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile card */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 h-full">
              <h3 className="font-heading text-lg text-gray-800 mb-4 flex items-center justify-between">
                <span>Client profile</span>
                {profile && (
                  <span className="text-xs font-body text-gray-500">
                    Client ID: {profile.client_id}
                  </span>
                )}
              </h3>

              {!profile && !loading && (
                <p className="text-sm font-body text-gray-500">
                  Enter a Client ID and click{" "}
                  <span className="font-medium">Get profile</span> to see the
                  assembled Single Client View.
                </p>
              )}

              {profile && (
                <div className="space-y-4">
                  {/* Core identity */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h4 className="font-heading text-sm text-gray-700 mb-2">
                      Core identity
                    </h4>
                    <dl className="grid grid-cols-2 gap-y-2 text-sm font-body">
                      <div>
                        <dt className="text-gray-500">Name</dt>
                        <dd className="text-gray-900">
                          {profile.name || "—"}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-gray-500">Email</dt>
                        <dd className="text-gray-900">
                          {profile.email || "—"}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-gray-500">Country</dt>
                        <dd className="text-gray-900">
                          {profile.country || "—"}
                        </dd>
                      </div>
                    </dl>
                  </div>

                  {/* Identifiers */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h4 className="font-heading text-sm text-gray-700 mb-2">
                      Identifiers
                    </h4>
                    {profile.identifiers && profile.identifiers.length > 0 ? (
                      <ul className="space-y-1 text-sm font-body">
                        {profile.identifiers.map((id, idx) => (
                          <li
                            key={idx}
                            className="flex justify-between border-b border-gray-200 last:border-b-0 pb-1"
                          >
                            <span className="text-gray-600">
                              {id.system || id["system"]}
                            </span>
                            <span className="text-gray-900 font-mono">
                              {id.value || id["value"]}
                            </span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500 font-body">
                        No identifiers found.
                      </p>
                    )}
                  </div>

                  {/* Addresses */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h4 className="font-heading text-sm text-gray-700 mb-2">
                      Addresses
                    </h4>
                    {profile.addresses && profile.addresses.length > 0 ? (
                      <ul className="space-y-2 text-sm font-body">
                        {profile.addresses.map((addr, idx) => (
                          <li
                            key={idx}
                            className="border-b border-gray-200 pb-2 last:border-b-0"
                          >
                            <div className="text-gray-900">
                              {[
                                addr.line1 || addr["line1"],
                                addr.line2 || addr["line2"],
                                addr.city || addr["city"],
                                addr.postcode || addr["postcode"],
                                addr.country || addr["country"],
                              ]
                                .filter(Boolean)
                                .join(", ")}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              Source: {addr.source || addr["source"] || "—"}
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500 font-body">
                        No addresses available.
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Raw sources / lineage card */}
          <div>
            <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 h-full">
              <h3 className="font-heading text-lg text-gray-800 mb-4">
                Raw sources
              </h3>

              {!profile && !loading && (
                <p className="text-sm font-body text-gray-500">
                  Once a profile is loaded, you&apos;ll see the upstream source
                  records here.
                </p>
              )}

              {sources && sources.length > 0 && (
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
              )}

              {profile && profile.lineage && (
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
      </main>
    </div>
  );
}

export default App;


