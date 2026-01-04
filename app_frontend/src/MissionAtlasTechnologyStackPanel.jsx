import React, { useMemo, useState } from "react";
import techStack from "./data/technology_stack.json";

function Badge({ text }) {
  const isLive = (text || "").toLowerCase() === "live";
  return (
    <span
      className={[
        "text-[11px] font-mono rounded-md px-2 py-1 border",
        isLive
          ? "bg-white text-gray-700 border-gray-200"
          : "bg-gray-50 text-gray-600 border-gray-200",
      ].join(" ")}
    >
      {text}
    </span>
  );
}

function Pill({ label }) {
  return (
    <span className="text-[11px] font-mono text-gray-700 bg-gray-50 border border-gray-200 rounded-md px-2 py-1">
      {label}
    </span>
  );
}

function SummaryCard({ title, value, subtitle }) {
  return (
    <div className="rounded-halo border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-heading text-sm text-gray-900">{title}</p>
          <p className="mt-1 text-xs font-body text-gray-700">{value}</p>
          {subtitle ? (
            <p className="mt-2 text-[11px] font-body text-gray-500">{subtitle}</p>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default function MissionAtlasTechnologyStackPanel() {
  const normalise = (s) => (s || "").toString().trim().toLowerCase();

  const components = useMemo(() => techStack?.components || [], []);
  const categories = useMemo(() => {
    const set = new Set((components || []).map((c) => c.category).filter(Boolean));
    return ["All", ...Array.from(set).sort()];
  }, [components]);

  const [categoryFilter, setCategoryFilter] = useState("All");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(components?.[0]?.id || null);

  const filtered = useMemo(() => {
    const q = normalise(query);
    return (components || [])
      .filter((c) => (categoryFilter === "All" ? true : c.category === categoryFilter))
      .filter((c) => {
        if (!q) return true;
        const hay = [
          c.name,
          c.category,
          c.status,
          ...(c.tech || []),
          ...(c.provenance || []).map((p) => p.path),
          ...(c.interfaces || []).map((i) => `${i.type} ${i.name} ${i.port || ""} ${i.path || ""}`),
        ]
          .filter(Boolean)
          .join(" | ");
        return normalise(hay).includes(q);
      });
  }, [components, categoryFilter, query]);

  const selected = useMemo(() => {
    return (components || []).find((c) => c.id === selectedId) || filtered?.[0] || null;
  }, [components, selectedId, filtered]);

  const summary = techStack?.summary || {};
  const meta = techStack?.meta || {};

  return (
    <div>
      {/* Summary strip */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-4">
        <SummaryCard
          title="Runtime"
          value={(summary.runtime || []).join(" · ") || "—"}
          subtitle="Primary runtimes only (no transitive inventories)."
        />
        <SummaryCard
          title="Data"
          value={(summary.data || []).join(" · ") || "—"}
          subtitle="Storage and persistence primitives."
        />
        <SummaryCard
          title="Hosting Target"
          value={(summary.hosting || []).join(" · ") || "—"}
          subtitle="Target state (only ‘Live’ when manifests exist)."
        />
        <SummaryCard
          title="Quality Signals"
          value={(summary.quality_signals || []).slice(0, 3).join(" · ") || "—"}
          subtitle="Automated checks and evidence outputs."
        />
      </div>

      {/* Controls */}
      <div className="rounded-halo border border-gray-200 bg-white p-4 shadow-sm mb-4">
        <div className="flex flex-col md:flex-row gap-3 md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div>
              <label className="block text-xs font-body text-gray-600 mb-1">Category</label>
              <select
                className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                {categories.map((c) => (
                  <option key={`cat-${c}`} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div className="min-w-[260px]">
              <label className="block text-xs font-body text-gray-600 mb-1">Search</label>
              <input
                className="w-full px-3 py-2 rounded-md text-sm font-body border border-gray-200"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search components, tech, interfaces, repo paths…"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Pill label={`Scope: ${meta.intent ? "curated" : "—"}`} />
            <Pill label={`Updated: ${meta.last_updated || "—"}`} />
          </div>
        </div>
      </div>

      {/* Two-pane layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left list */}
        <div className="lg:col-span-5 rounded-halo border border-gray-200 bg-white shadow-sm">
          <div className="border-b border-gray-200 p-4">
            <p className="font-heading text-sm text-gray-900">Components</p>
            <p className="mt-1 text-xs font-body text-gray-600">
              Enterprise-level units only. No lockfile BOMs.
            </p>
          </div>

          <div className="p-2">
            {(filtered || []).map((c) => {
              const active = c.id === selected?.id;
              return (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setSelectedId(c.id)}
                  className={[
                    "w-full text-left rounded-md border p-3 mb-2 transition",
                    active
                      ? "border-gray-300 bg-gray-50"
                      : "border-gray-200 bg-white hover:bg-gray-50",
                  ].join(" ")}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-heading text-sm text-gray-900">{c.name}</p>
                      <p className="mt-1 text-xs font-body text-gray-600">
                        {c.category} · {(c.tech || []).slice(0, 3).join(" · ")}
                        {(c.tech || []).length > 3 ? " · …" : ""}
                      </p>
                    </div>
                    <Badge text={c.status || "—"} />
                  </div>
                </button>
              );
            })}

            {!filtered?.length ? (
              <div className="p-4 text-xs font-body text-gray-600">
                No components match the current filters.
              </div>
            ) : null}
          </div>
        </div>

        {/* Right detail */}
        <div className="lg:col-span-7 rounded-halo border border-gray-200 bg-white shadow-sm">
          <div className="border-b border-gray-200 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-heading text-sm text-gray-900">{selected?.name || "—"}</p>
                <p className="mt-1 text-xs font-body text-gray-600">
                  {selected?.category || "—"}
                </p>
              </div>
              <Badge text={selected?.status || "—"} />
            </div>
          </div>

          <div className="p-4 space-y-4">
            {/* Tech */}
            <div>
              <p className="font-heading text-xs text-gray-900">Primary Technology</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {(selected?.tech || []).length ? (
                  selected.tech.map((t) => <Pill key={`tech-${t}`} label={t} />)
                ) : (
                  <p className="text-xs font-body text-gray-600">—</p>
                )}
              </div>
            </div>

            {/* Interfaces */}
            <div>
              <p className="font-heading text-xs text-gray-900">Interfaces</p>
              <div className="mt-2 space-y-2">
                {(selected?.interfaces || []).length ? (
                  selected.interfaces.map((i, idx) => (
                    <div
                      key={`if-${idx}`}
                      className="rounded-md border border-gray-200 bg-gray-50 p-3"
                    >
                      <p className="text-xs font-body text-gray-800">
                        <span className="font-mono">{i.type}</span>
                        {" · "}
                        {i.name}
                        {i.port ? ` · port ${i.port}` : ""}
                        {i.path ? ` · ${i.path}` : ""}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs font-body text-gray-600">—</p>
                )}
              </div>
            </div>

            {/* Provenance */}
            <div>
              <p className="font-heading text-xs text-gray-900">Provenance</p>
              <div className="mt-2 space-y-2">
                {(selected?.provenance || []).length ? (
                  selected.provenance.map((p, idx) => (
                    <div
                      key={`prov-${idx}`}
                      className="rounded-md border border-gray-200 bg-white p-3"
                    >
                      <p className="text-xs font-body text-gray-800">
                        <span className="font-mono">{p.type}</span>
                        {" · "}
                        <span className="font-mono text-gray-700">{p.path}</span>
                      </p>
                      <p className="mt-1 text-[11px] font-body text-gray-500">
                        Confidence: {p.confidence || "—"}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs font-body text-gray-600">—</p>
                )}
              </div>
            </div>

            {/* Operational */}
            <div>
              <p className="font-heading text-xs text-gray-900">Operational</p>
              <div className="mt-2 space-y-2">
                {(selected?.operational || []).length ? (
                  selected.operational.map((o, idx) => (
                    <div
                      key={`op-${idx}`}
                      className="rounded-md border border-gray-200 bg-gray-50 p-3"
                    >
                      <p className="text-xs font-body text-gray-800">
                        <span className="font-mono">{o.type}</span>
                        {" · "}
                        {o.label ? `${o.label} · ` : ""}
                        <span className="font-mono">{o.value}</span>
                      </p>
                      {o.confidence ? (
                        <p className="mt-1 text-[11px] font-body text-gray-500">
                          Confidence: {o.confidence}
                        </p>
                      ) : null}
                    </div>
                  ))
                ) : (
                  <p className="text-xs font-body text-gray-600">—</p>
                )}
              </div>
            </div>

            {/* Controls */}
            <div>
              <p className="font-heading text-xs text-gray-900">Controls</p>
              <div className="mt-2 space-y-2">
                {(selected?.controls || []).length ? (
                  selected.controls.map((c, idx) => (
                    <div
                      key={`ctl-${idx}`}
                      className="rounded-md border border-gray-200 bg-white p-3"
                    >
                      <p className="text-xs font-body text-gray-800">
                        {c.type} · {c.name} · <span className="font-mono">{c.status}</span>
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs font-body text-gray-600">—</p>
                )}
              </div>
            </div>

            {/* Notes */}
            {selected?.notes ? (
              <div>
                <p className="font-heading text-xs text-gray-900">Notes</p>
                <p className="mt-2 text-xs font-body text-gray-700 whitespace-pre-wrap">
                  {selected.notes}
                </p>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
