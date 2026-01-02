import React, { useMemo, useState } from "react";
import physicalModel from "./data/physical_model_by_domain.json";

export default function MissionAtlasServiceTopologyPanel() {
  const [tab, setTab] = useState("dependencies"); // dependencies | catalogue
  const [selectedService, setSelectedService] = useState(null);
  const [query, setQuery] = useState("");

  const normalise = (s) => (s || "").toString().trim().toLowerCase();

  const domains = useMemo(() => physicalModel?.domains || [], []);

  // Map platform domains → microservices (this is your microservice boundary)
  const services = useMemo(() => {
    return (domains || []).map((d) => {
      const tables = d.tables || [];
      const fks = tables.flatMap((t) => t.foreign_keys || []);
      const indexes = tables.flatMap((t) => t.indexes || []);
      const cols = tables.reduce((acc, t) => acc + (t.columns?.length || 0), 0);

      return {
        serviceId: domainToServiceId(d.domain),
        serviceName: domainToServiceName(d.domain),
        domain: d.domain,
        purpose: d.purpose,
        tables,
        stats: {
          tables: tables.length,
          columns: cols,
          outboundFks: fks.length,
          indexes: indexes.length,
        },
        // contracts are placeholders for now (ready to wire to OpenAPI later)
        contracts: suggestedContractsForDomain(d.domain),
      };
    });
  }, [domains]);

  // Build lookup: table fq -> domain
  const fqToDomain = useMemo(() => {
    const m = new Map();
    for (const d of domains) {
      for (const t of d.tables || []) {
        m.set(`${t.schema}.${t.table}`, d.domain);
      }
    }
    return m;
  }, [domains]);

  // Compute cross-service dependencies using FK references
  const dependencies = useMemo(() => {
    const depMap = new Map(); // domain -> Map(refDomain -> count)

    for (const d of domains) {
      const domain = d.domain;
      if (!depMap.has(domain)) depMap.set(domain, new Map());

      for (const t of d.tables || []) {
        for (const fk of t.foreign_keys || []) {
          const refDomain = fqToDomain.get(fk.references_table) || "External/Unknown";
          if (refDomain === domain) continue;
          const inner = depMap.get(domain);
          inner.set(refDomain, (inner.get(refDomain) || 0) + 1);
        }
      }
    }

    return [...depMap.entries()]
      .map(([domain, refs]) => ({
        domain,
        refs: [...refs.entries()]
          .map(([refDomain, count]) => ({ refDomain, count }))
          .sort((a, b) => b.count - a.count || a.refDomain.localeCompare(b.refDomain)),
      }))
      .sort((a, b) => a.domain.localeCompare(b.domain));
  }, [domains, fqToDomain]);

  const filteredServices = useMemo(() => {
    const q = normalise(query);
    if (!q) return services;
    return services.filter((s) => {
      return (
        normalise(s.serviceName).includes(q) ||
        normalise(s.serviceId).includes(q) ||
        normalise(s.domain).includes(q) ||
        normalise(s.purpose).includes(q) ||
        s.tables.some((t) => normalise(`${t.schema}.${t.table}`).includes(q))
      );
    });
  }, [services, query]);

  const selected = useMemo(() => {
    if (!selectedService) return filteredServices[0] || null;
    return filteredServices.find((s) => s.serviceId === selectedService) || filteredServices[0] || null;
  }, [selectedService, filteredServices]);

  if (!selectedService && filteredServices.length) {
    // set once on first render
    setSelectedService(filteredServices[0].serviceId);
  }

  const selectedDeps = useMemo(() => {
    if (!selected) return [];
    const entry = dependencies.find((d) => d.domain === selected.domain);
    return entry?.refs || [];
  }, [selected, dependencies]);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h3 className="font-heading text-sm text-gray-900">Microservices Architecture</h3>
            <p className="mt-1 text-xs font-body text-gray-600">
              Service boundaries, ownership and dependencies derived from the live schema.
              This is a microservice view (not a table inspector).
            </p>
          </div>

          <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
            tables: {physicalModel?.summary?.tables ?? "—"} • domains: {physicalModel?.summary?.domains ?? "—"} • fks:{" "}
            {physicalModel?.summary?.foreign_keys ?? "—"} • idx: {physicalModel?.summary?.indexes ?? "—"}
          </span>
        </div>
      </div>

      {/* Controls */}
      <div className="rounded-halo border border-gray-200 bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex gap-2">
            <button
              className={`px-3 py-2 rounded-md text-sm font-body border ${
                tab === "dependencies" ? "bg-amber-50 border-amber-300" : "bg-white border-gray-200"
              }`}
              onClick={() => setTab("dependencies")}
              type="button"
            >
              Dependencies
            </button>
            <button
              className={`px-3 py-2 rounded-md text-sm font-body border ${
                tab === "catalogue" ? "bg-amber-50 border-amber-300" : "bg-white border-gray-200"
              }`}
              onClick={() => setTab("catalogue")}
              type="button"
            >
              Catalogue
            </button>
          </div>

          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search services, domains, tables..."
            className="px-3 py-2 rounded-md text-sm font-body border border-gray-200 bg-white min-w-[320px]"
          />
        </div>
      </div>

      {tab === "catalogue" ? (
        <div className="rounded-halo border border-gray-200 bg-white p-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
            {filteredServices.map((s) => {
              const active = selected?.serviceId === s.serviceId;
              return (
                <button
                  key={s.serviceId}
                  type="button"
                  onClick={() => setSelectedService(s.serviceId)}
                  className={`text-left rounded-md border p-3 transition ${
                    active ? "bg-amber-50 border-amber-300 shadow" : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-heading text-sm text-gray-900">{s.serviceName}</div>
                      <div className="mt-1 text-[11px] font-mono text-gray-700">{s.serviceId}</div>
                      <div className="mt-1 text-[11px] font-body text-gray-600">{s.domain}</div>
                    </div>

                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                      tables: {s.stats.tables}
                    </span>
                  </div>

                  <div className="mt-2 text-xs font-body text-gray-700 line-clamp-2">{s.purpose}</div>

                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                      cols: {s.stats.columns}
                    </span>
                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                      outbound fks: {s.stats.outboundFks}
                    </span>
                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700">
                      idx: {s.stats.indexes}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Service list */}
          <div className="rounded-halo border border-gray-200 bg-white p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h4 className="font-heading text-sm text-gray-900">Services</h4>
                <p className="mt-1 text-xs font-body text-gray-600">
                  Select a service to inspect its boundaries, owned data and dependencies.
                </p>
              </div>
              <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-600">
                {filteredServices.length}
              </span>
            </div>

            <div className="mt-3 space-y-2 max-h-[560px] overflow-auto pr-1">
              {filteredServices.map((s) => {
                const active = selected?.serviceId === s.serviceId;
                return (
                  <button
                    key={`svc-${s.serviceId}`}
                    type="button"
                    onClick={() => setSelectedService(s.serviceId)}
                    className={`w-full text-left rounded-md border p-3 transition ${
                      active ? "bg-amber-50 border-amber-300 shadow" : "bg-gray-50 border-gray-200 hover:bg-gray-100"
                    }`}
                  >
                    <div className="font-heading text-sm text-gray-900">{s.serviceName}</div>
                    <div className="mt-1 text-[11px] font-mono text-gray-700">{s.serviceId}</div>
                    <div className="mt-1 text-[11px] font-body text-gray-600">
                      tables: {s.stats.tables} • fks: {s.stats.outboundFks}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Service detail */}
          <div className="lg:col-span-2 rounded-halo border border-gray-200 bg-white p-4">
            {!selected ? (
              <div className="text-sm font-body text-gray-700">Select a service.</div>
            ) : (
              <div className="space-y-4">
                <div className="flex flex-col gap-2 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <h4 className="font-heading text-sm text-gray-900">{selected.serviceName}</h4>
                    <div className="mt-1 text-[11px] font-mono text-gray-700">{selected.serviceId}</div>
                    <div className="mt-2 text-xs font-body text-gray-700">{selected.purpose}</div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-700">
                      tables: {selected.stats.tables}
                    </span>
                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-700">
                      cols: {selected.stats.columns}
                    </span>
                    <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-teal-50 border-teal-200 text-gray-800">
                      outbound fks: {selected.stats.outboundFks}
                    </span>
                  </div>
                </div>

                {/* Owned tables */}
                <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                  <div className="font-heading text-sm text-gray-900">Owned data (service boundary)</div>
                  <div className="mt-1 text-xs font-body text-gray-600">
                    Tables owned by this service. This is the data contract surface for the service.
                  </div>

                  <div className="mt-2 flex flex-wrap gap-2">
                    {(selected.tables || []).map((t) => (
                      <span
                        key={`${t.schema}.${t.table}`}
                        className="text-[11px] font-mono rounded-md px-2 py-1 border bg-white border-gray-200 text-gray-700"
                      >
                        {t.schema}.{t.table}
                      </span>
                    ))}
                    {!selected.tables?.length ? (
                      <div className="text-xs font-body text-gray-600">—</div>
                    ) : null}
                  </div>
                </div>

                {/* Dependencies */}
                <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                  <div className="font-heading text-sm text-gray-900">Service dependencies</div>
                  <div className="mt-1 text-xs font-body text-gray-600">
                    Derived from cross-domain foreign key references (data coupling surface).
                  </div>

                  <ul className="mt-2 list-disc pl-5 space-y-1">
                    {selectedDeps.length ? (
                      selectedDeps.map((d) => (
                        <li key={`${selected.domain}->${d.refDomain}`} className="text-xs font-body text-gray-800">
                          <span className="font-mono">{domainToServiceName(d.refDomain)}</span>{" "}
                          <span className="text-gray-500">({d.refDomain})</span> —{" "}
                          <span className="font-mono">{d.count}</span> FK reference(s)
                        </li>
                      ))
                    ) : (
                      <li className="text-xs font-body text-gray-600">No cross-domain dependencies detected.</li>
                    )}
                  </ul>
                </div>

                {/* Contracts */}
                <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                  <div className="font-heading text-sm text-gray-900">Service contracts</div>
                  <div className="mt-1 text-xs font-body text-gray-600">
                    Suggested REST contracts (placeholder until wired to real OpenAPI from backend).
                  </div>

                  <div className="mt-2 space-y-2">
                    {selected.contracts.map((c) => (
                      <div
                        key={`${selected.serviceId}-${c.name}`}
                        className="rounded-md border border-gray-200 bg-white p-3"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="font-heading text-sm text-gray-900">{c.name}</div>
                          <span className="text-[11px] font-mono rounded-md px-2 py-1 border bg-gray-50 border-gray-200 text-gray-700">
                            {c.version}
                          </span>
                        </div>
                        <div className="mt-1 text-xs font-body text-gray-700">{c.description}</div>

                        <div className="mt-2 flex flex-col gap-1">
                          {c.endpoints.map((e) => (
                            <div key={`${c.name}-${e.method}-${e.path}`} className="text-[11px] font-mono text-gray-700">
                              {e.method} {e.path}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Notes */}
                <div className="rounded-md border border-gray-200 bg-white p-3">
                  <div className="text-xs font-body text-gray-600">Next enrichment (optional)</div>
                  <div className="mt-1 text-xs font-body text-gray-800">
                    Wire this to real service metadata by parsing FastAPI route tables/OpenAPI JSON from backend_v2,
                    then replace “suggested contracts” with the actual published interfaces.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function domainToServiceId(domain) {
  const d = (domain || "").toLowerCase().replace(/\s*&\s*/g, "-").replace(/\s+/g, "-");
  return `svc-${d}`;
}

function domainToServiceName(domain) {
  const d = (domain || "").toString();
  const map = {
    "Client canonical": "Client Canonical Service",
    "Lineage & dictionary": "Lineage and Dictionary Service",
    "KYC & risk": "KYC and Risk Service",
    "Reference data": "Reference Data Service",
  };
  return map[d] || `${d} Service`;
}

function suggestedContractsForDomain(domain) {
  // These are intentionally credible but placeholders.
  // Once you wire OpenAPI, these should become real.
  const d = (domain || "").toLowerCase();

  const contracts = [];

  if (d.includes("ingestion")) {
    contracts.push({
      name: "Ingestion API",
      version: "v1",
      description: "Manage ingestion runs, accept source payloads and expose ingest status.",
      endpoints: [
        { method: "POST", path: "/ingestion/runs" },
        { method: "GET", path: "/ingestion/runs/{run_id}" },
        { method: "POST", path: "/ingestion/source-records" },
        { method: "GET", path: "/ingestion/source-records?run_id={run_id}" },
      ],
    });
  }

  if (d.includes("client canonical")) {
    contracts.push({
      name: "Client Profile API",
      version: "v1",
      description: "Retrieve unified client profiles and operational state.",
      endpoints: [
        { method: "GET", path: "/clients" },
        { method: "GET", path: "/clients/{client_id}" },
        { method: "GET", path: "/clients/{client_id}/operational-state" },
        { method: "GET", path: "/clients/{client_id}/source-coverage" },
      ],
    });
  }

  if (d.includes("matching")) {
    contracts.push({
      name: "Matching API",
      version: "v1",
      description: "Execute and inspect matching, clusters and match decisions.",
      endpoints: [
        { method: "POST", path: "/matching/runs" },
        { method: "GET", path: "/matching/runs/{run_id}" },
        { method: "GET", path: "/matching/clusters" },
        { method: "GET", path: "/matching/decisions?run_id={run_id}" },
      ],
    });
  }

  if (d.includes("lineage")) {
    contracts.push({
      name: "Lineage API",
      version: "v1",
      description: "Attribute dictionary, precedence and resolved lineage paths.",
      endpoints: [
        { method: "GET", path: "/lineage/dictionary" },
        { method: "GET", path: "/lineage/precedence-rules" },
        { method: "GET", path: "/lineage/resolve?client_id={id}&concept={concept}" },
      ],
    });
  }

  if (d.includes("assurance")) {
    contracts.push({
      name: "Assurance API",
      version: "v1",
      description: "Validation results, audits and operational health signals.",
      endpoints: [
        { method: "GET", path: "/assurance/validation-results" },
        { method: "GET", path: "/assurance/audit-events" },
        { method: "GET", path: "/assurance/health-checks" },
        { method: "GET", path: "/assurance/error-logs" },
      ],
    });
  }

  if (d.includes("evidence")) {
    contracts.push({
      name: "Evidence API",
      version: "v1",
      description: "Evidence artefacts and bundles generated from governed execution.",
      endpoints: [
        { method: "GET", path: "/evidence/artefacts" },
        { method: "GET", path: "/evidence/bundles" },
        { method: "GET", path: "/evidence/bundles/{bundle_id}" },
      ],
    });
  }

  if (d.includes("kyc") || d.includes("risk")) {
    contracts.push({
      name: "KYC & Risk API",
      version: "v1",
      description: "KYC flags, KYC records and risk rating surfaces.",
      endpoints: [
        { method: "GET", path: "/kyc/corporate/{client_id}" },
        { method: "GET", path: "/kyc/flags?client_id={id}" },
        { method: "GET", path: "/risk/rating?client_id={id}" },
      ],
    });
  }

  if (d.includes("reference")) {
    contracts.push({
      name: "Reference Data API",
      version: "v1",
      description: "Reference and master data shared across services.",
      endpoints: [
        { method: "GET", path: "/reference/countries" },
        { method: "GET", path: "/reference/asset-classes" },
      ],
    });
  }

  // fallback if nothing matched
  if (!contracts.length) {
    contracts.push({
      name: "Service API",
      version: "v1",
      description: "Service contract placeholder (wire OpenAPI for real endpoints).",
      endpoints: [{ method: "GET", path: "/health" }],
    });
  }

  return contracts;
}

