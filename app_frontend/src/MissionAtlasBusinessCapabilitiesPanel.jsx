import React, { useMemo, useState } from "react";
import businessCapabilities from "./data/business_capabilities.json";

function Chip({ children, variant = "neutral" }) {
  const cls =
    variant === "story"
      ? "border-gray-300 bg-white text-gray-800"
      : variant === "service"
      ? "border-amber-300 bg-amber-50 text-gray-900"
      : variant === "api"
      ? "border-sky-200 bg-sky-50 text-gray-900"
      : variant === "table"
      ? "border-emerald-200 bg-emerald-50 text-gray-900"
      : "border-gray-200 bg-gray-50 text-gray-700";

  return (
    <span
      className={`inline-flex items-center font-mono text-[11px] px-2 py-0.5 rounded border ${cls}`}
    >
      {children}
    </span>
  );
}

function uniq(arr) {
  return Array.from(new Set((arr || []).filter(Boolean)));
}

function deriveArtefacts(cap) {
  const stories = uniq([
    ...(cap.proof?.story_ids || []),
    ...(cap.orchestration || []).flatMap((s) => s.stories || []),
  ]);

  const services = uniq(
    (cap.orchestration || []).flatMap((s) => s.services || [])
  );

  const apis = uniq((cap.outputs || []).flatMap((o) => o.api_routes || []));

  const tables = uniq([
    ...(cap.persistence?.reads || []),
    ...(cap.persistence?.writes || []),
    ...(cap.orchestration || []).flatMap((s) => [
      ...(s.reads_tables || []),
      ...(s.writes_tables || []),
    ]),
    ...(cap.outputs || []).flatMap((o) => o.reads_tables || []),
  ]);

  return { stories, services, apis, tables };
}

export default function MissionAtlasBusinessCapabilitiesPanel() {
  const capabilities = useMemo(
    () => businessCapabilities?.capabilities || [],
    []
  );

  const [query, setQuery] = useState("");
  const [selectedCapabilityId, setSelectedCapabilityId] = useState(null);

  const selectedCapability = useMemo(() => {
    if (!selectedCapabilityId) return null;
    return capabilities.find((c) => c.capability_id === selectedCapabilityId) || null;
  }, [capabilities, selectedCapabilityId]);

  const filtered = useMemo(() => {
    const q = (query || "").trim().toLowerCase();
    if (!q) return capabilities;

    return capabilities.filter((c) => {
      const a = deriveArtefacts(c);
      const hay = [
        c.capability_id,
        c.name,
        c.intent,
        c.domain,
        c.description,
        ...a.stories,
        ...a.services,
        ...a.apis,
        ...a.tables,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return hay.includes(q);
    });
  }, [capabilities, query]);

  const renderCatalogue = () => (
    <div className="space-y-4">
      {/* Top row */}
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-body text-gray-600">
            Capabilities provided by this platform, derived from stories, services and data.
          </p>
        </div>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search capabilities, stories, services..."
          className="w-full md:w-[360px] px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white text-gray-700"
        />
      </div>

      {/* Capability list */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filtered.map((cap) => {
          const maturity = cap.proof?.maturity || "unknown";
          const a = deriveArtefacts(cap);

          return (
            <button
              key={cap.capability_id}
              type="button"
              onClick={() => setSelectedCapabilityId(cap.capability_id)}
              className="text-left rounded-halo border border-gray-200 bg-white hover:bg-gray-50 shadow-sm p-4 transition"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-heading text-sm text-gray-900 truncate">
                    {cap.name}
                  </p>
                  <p className="mt-1 text-xs font-body text-gray-600 line-clamp-2">
                    {cap.intent}
                  </p>
                  <p className="mt-2 text-[11px] font-mono text-gray-500">
                    {cap.capability_id} · {cap.domain}
                  </p>
                </div>

                <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800">
                  {maturity}
                </span>
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                <Chip variant="story">{a.stories.length} stories</Chip>
                <Chip variant="service">{a.services.length} services</Chip>
                <Chip variant="api">{a.apis.length} APIs</Chip>
                <Chip variant="table">{a.tables.length} tables</Chip>
              </div>
            </button>
          );
        })}
      </div>

      {!filtered.length ? (
        <div className="rounded-halo border border-gray-200 bg-gray-50 p-5 text-xs font-body text-gray-700">
          No capabilities match your search.
        </div>
      ) : null}
    </div>
  );

  const renderDetail = (cap) => {
    const maturity = cap.proof?.maturity || "unknown";
    const a = deriveArtefacts(cap);

    return (
      <div className="space-y-4">
        {/* Back + search (optional keep search for consistency) */}
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <button
            type="button"
            onClick={() => setSelectedCapabilityId(null)}
            className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white hover:bg-gray-50 text-gray-700 w-fit"
          >
            Back to all capabilities
          </button>

          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search capabilities, stories, services..."
            className="w-full md:w-[360px] px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white text-gray-700"
          />
        </div>

        {/* Detail card (your improved layout) */}
        <div className="rounded-halo border border-gray-200 bg-white shadow-sm">
          {/* Header */}
          <div className="px-5 py-4 border-b border-gray-200 flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <p className="font-heading text-sm text-gray-900">{cap.name}</p>
                <span className="text-[11px] font-mono text-gray-500">
                  {cap.capability_id} · {cap.domain}
                </span>
              </div>
              <p className="mt-1 text-xs font-body text-gray-600">{cap.intent}</p>

              <div className="mt-3 flex flex-wrap gap-2">
                <Chip variant="story">{a.stories.length} stories</Chip>
                <Chip variant="service">{a.services.length} services</Chip>
                <Chip variant="api">{a.apis.length} APIs</Chip>
                <Chip variant="table">{a.tables.length} tables</Chip>
              </div>
            </div>

            <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800">
              {maturity}
            </span>
          </div>

          {/* Body */}
          <div className="p-5">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Left */}
              <div className="lg:col-span-2 space-y-4">
                {cap.description ? (
                  <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                    <p className="text-xs font-body text-gray-700">
                      {cap.description}
                    </p>
                  </div>
                ) : null}

                {cap.inputs?.length ? (
                  <div className="rounded-md border border-gray-200 bg-white p-3">
                    <p className="font-heading text-xs text-gray-800 mb-2">Inputs</p>
                    <div className="space-y-1">
                      {cap.inputs.map((i, idx) => (
                        <div
                          key={`${cap.capability_id}-in-${idx}`}
                          className="text-xs font-body text-gray-700"
                        >
                          <span className="text-gray-900">{i.name}</span>
                          <span className="text-gray-500">
                            {" "}
                            · {i.source}
                            {i.interface ? ` · ${i.interface}` : ""}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                {cap.outputs?.length ? (
                  <div className="rounded-md border border-gray-200 bg-white p-3">
                    <p className="font-heading text-xs text-gray-800 mb-2">Outputs</p>
                    <div className="space-y-2">
                      {cap.outputs.map((o, idx) => (
                        <div
                          key={`${cap.capability_id}-out-${idx}`}
                          className="text-xs font-body text-gray-700"
                        >
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-gray-900">{o.name}</span>
                            <span className="text-gray-500">· {o.channel}</span>
                          </div>

                          {o.api_routes?.length ? (
                            <div className="mt-2 flex flex-wrap gap-2">
                              {o.api_routes.map((r) => (
                                <Chip key={r} variant="api">
                                  {r}
                                </Chip>
                              ))}
                            </div>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                {cap.guarantees?.length ? (
                  <div className="rounded-md border border-gray-200 bg-white p-3">
                    <p className="font-heading text-xs text-gray-800 mb-2">
                      Guarantees
                    </p>
                    <ul className="list-disc pl-5 space-y-1">
                      {cap.guarantees.map((g, idx) => (
                        <li
                          key={`${cap.capability_id}-g-${idx}`}
                          className="text-xs font-body text-gray-700"
                        >
                          {g}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>

              {/* Right */}
              <div className="space-y-4">
                {cap.orchestration?.length ? (
                  <div className="rounded-md border border-gray-200 bg-white p-3">
                    <p className="font-heading text-xs text-gray-800 mb-2">
                      How it works
                    </p>

                    <div className="space-y-2">
                      {cap.orchestration.map((s) => (
                        <div
                          key={`${cap.capability_id}-step-${s.step}`}
                          className="rounded-md border border-gray-200 bg-gray-50 p-2"
                        >
                          <div className="flex items-start gap-2">
                            <div className="font-mono text-[11px] text-gray-500 w-6 text-right">
                              {s.step}.
                            </div>
                            <div className="min-w-0">
                              <div className="text-xs font-body text-gray-900">
                                {s.name}
                              </div>

                              <div className="mt-1 flex flex-wrap gap-2">
                                {(s.stories || []).map((st) => (
                                  <Chip key={st} variant="story">
                                    {st}
                                  </Chip>
                                ))}
                                {(s.services || []).map((svc) => (
                                  <Chip key={svc} variant="service">
                                    {svc}
                                  </Chip>
                                ))}
                              </div>

                              {(s.reads_tables?.length || s.writes_tables?.length) ? (
                                <div className="mt-2 flex flex-wrap gap-2">
                                  {(s.reads_tables || []).map((t) => (
                                    <Chip key={`r-${t}`} variant="table">
                                      {t}
                                    </Chip>
                                  ))}
                                  {(s.writes_tables || []).map((t) => (
                                    <Chip key={`w-${t}`} variant="table">
                                      {t}
                                    </Chip>
                                  ))}
                                </div>
                              ) : null}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                <div className="rounded-md border border-gray-200 bg-white p-3">
                  <p className="font-heading text-xs text-gray-800 mb-2">
                    Artefacts
                  </p>

                  <div className="space-y-3">
                    <div>
                      <p className="text-[11px] font-mono text-gray-500 mb-1">
                        Stories
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {a.stories.length ? a.stories.map((st) => (
                          <Chip key={st} variant="story">{st}</Chip>
                        )) : <span className="text-xs font-body text-gray-500">-</span>}
                      </div>
                    </div>

                    <div>
                      <p className="text-[11px] font-mono text-gray-500 mb-1">
                        Services
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {a.services.length ? a.services.map((svc) => (
                          <Chip key={svc} variant="service">{svc}</Chip>
                        )) : <span className="text-xs font-body text-gray-500">-</span>}
                      </div>
                    </div>

                    <div>
                      <p className="text-[11px] font-mono text-gray-500 mb-1">
                        APIs
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {a.apis.length ? a.apis.map((api) => (
                          <Chip key={api} variant="api">{api}</Chip>
                        )) : <span className="text-xs font-body text-gray-500">-</span>}
                      </div>
                    </div>

                    <div>
                      <p className="text-[11px] font-mono text-gray-500 mb-1">
                        Tables
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {a.tables.length ? a.tables.map((t) => (
                          <Chip key={t} variant="table">{t}</Chip>
                        )) : <span className="text-xs font-body text-gray-500">-</span>}
                      </div>
                    </div>
                  </div>
                </div>

                {cap.proof?.evidence_paths?.length ? (
                  <div className="rounded-md border border-gray-200 bg-white p-3">
                    <p className="font-heading text-xs text-gray-800 mb-2">
                      Evidence hooks
                    </p>
                    <div className="space-y-1">
                      {cap.proof.evidence_paths.map((p) => (
                        <div
                          key={p}
                          className="font-mono text-[11px] text-gray-700 border border-gray-200 bg-gray-50 rounded px-2 py-1"
                        >
                          {p}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (!selectedCapability) return renderCatalogue();
  return renderDetail(selectedCapability);
}




