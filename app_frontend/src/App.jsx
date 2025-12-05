// app_frontend/src/App.jsx
import React, { useState } from "react";
import logo from "./assets/m7_single_client_view.png";

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
      const encodedId = encodeURIComponent(clientId.trim());

      const profileRes = await fetch(
        `${BACKEND_BASE_URL}/clients/${encodedId}/profile`
      );
      if (!profileRes.ok) {
        const detail = await profileRes.json().catch(() => ({}));
        throw new Error(detail.detail || "Failed to fetch profile.");
      }
      const profileJson = await profileRes.json();

      const sourcesRes = await fetch(
        `${BACKEND_BASE_URL}/clients/${encodedId}/sources`
      );
      const sourcesJson = sourcesRes.ok ? await sourcesRes.json() : [];

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
      
      {/* Header with MissionHalo logo */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <img
            src={logo}
            alt="M7 single client view"
            className="h-16 w-auto md:h-20"
          />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">

        {/* Search */}
        <section className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="font-heading text-lg text-gray-800 mb-4">
            Find client profile
          </h2>

          <form
            onSubmit={handleSubmit}
            className="flex flex-col md:flex-row gap-4 items-stretch md:items-end"
          >
            {/* Input */}
            <div className="flex-1">
              <label
                htmlFor="client-id"
                className="block text-sm font-body text-gray-600 mb-1"
              >
                Client ID
              </label>
              <input
                id="client-id"
                type="text"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="e.g. 123"
                className="
                  w-full px-3 py-2 rounded-md border border-gray-300 
                  font-body text-sm
                  focus:outline-none focus:ring-2 
                  focus:ring-[#1A9988] focus:border-[#1A9988]
                "
              />
            </div>

            {/* MissionHalo button */}
            <button
              type="submit"
              disabled={loading}
              className="
                inline-flex items-center justify-center
                px-4 py-2 rounded-md w-32
                bg-[#1A9988] text-white
                font-body text-sm font-medium shadow-sm
                transition-colors transition-transform duration-150
                hover:bg-[#178c7d] hover:-translate-y-0.5
                active:bg-[#147c6f] active:translate-y-0
                disabled:opacity-60 disabled:cursor-not-allowed
              "
            >
              {loading ? "Loading…" : "Get profile"}
            </button>
          </form>

          {error && (
            <p className="mt-4 text-sm text-orange-700 bg-orange-50 border border-orange-200 rounded-md px-3 py-2 font-body">
              {error}
            </p>
          )}
        </section>

        {/* Content */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Client profile */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 h-full">
              <h3 className="font-heading text-lg text-gray-800 mb-4">
                Client profile
              </h3>

              {!profile && !loading && (
                <p className="text-sm font-body text-gray-500">
                  Enter a Client ID and click{" "}
                  <span className="font-semibold">Get profile</span> to see
                  the assembled Single Client View.
                </p>
              )}

              {loading && (
                <p className="text-sm font-body text-gray-500">Loading…</p>
              )}

              {profile && (
                <div className="space-y-4">
                  
                  {/* Basic details */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h4 className="font-heading text-sm text-gray-700 mb-2">
                      Basic details
                    </h4>

                    <dl className="grid grid-cols-2 gap-y-2 text-sm font-body">
                      <div>
                        <dt className="text-gray-500">Client ID</dt>
                        <dd className="text-gray-900">
                          {profile.client_id || "—"}
                        </dd>
                      </div>

                      <div>
                        <dt className="text-gray-500">Name</dt>
                        <dd className="text-gray-900">{profile.name || "—"}</dd>
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

                  {/* Addresses */}
                  {profile.addresses?.length > 0 && (
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
              )}

            </div>
          </div>

          {/* Raw sources + lineage */}
          <div>
            <div className="bg-white rounded-halo shadow-sm border border-gray-200 p-6 h-full">

              <h3 className="font-heading text-lg text-gray-800 mb-4">
                Raw sources
              </h3>

              {!profile && !loading && (
                <p className="text-sm font-body text-gray-500">
                  Once a profile is loaded, you’ll see the upstream records here.
                </p>
              )}

              {sources.length > 0 && (
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
      </main>
    </div>
  );
}

export default App;






