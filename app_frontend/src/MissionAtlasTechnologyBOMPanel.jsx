import React, { useState, useMemo } from "react";
import { technologyBOM } from "./mission_atlas/technology_bom"; // Import the BOM data

const tabs = [
  { key: "componentInventory", title: "Component Inventory" },
  { key: "interfacesContracts", title: "Interfaces & Contracts" },
  { key: "runtimeWiring", title: "Runtime Wiring" },
];

export default function MissionAtlasTechnologyBOMPanel() {
  const [selectedTab, setSelectedTab] = useState(tabs[0].key); // Default to Component Inventory

  // Helper function to render each tab's content
  const renderTabContent = () => {
    switch (selectedTab) {
      case "componentInventory":
        return renderComponentInventory();
      case "interfacesContracts":
        return renderInterfacesContracts();
      case "runtimeWiring":
        return renderRuntimeWiring();
      default:
        return renderComponentInventory();
    }
  };

  // Render the Component Inventory tab content
  const renderComponentInventory = () => (
    <div className="space-y-3">
      {technologyBOM.components.map((component) => (
        <div key={component.name} className="rounded-md p-3 border bg-gray-50 border-gray-200">
          <h4 className="font-heading text-sm text-gray-900">{component.name}</h4>
          <p className="text-xs font-body text-gray-600">{component.type}</p>
          <p className="text-[11px] font-mono text-gray-500">Runtime: {component.runtime}</p>
          <p className="text-[11px] font-mono text-gray-500">Language: {component.language}</p>
          <p className="text-[11px] font-mono text-gray-500">Framework: {component.framework}</p>
          <p className="text-[11px] font-mono text-gray-500">Repo Path: {component.repoPath}</p>
          <p className="text-[11px] font-mono text-gray-500">Interfaces: {component.interfaces.map((i) => i.endpoint).join(", ")}</p>
          <p className="text-[11px] font-mono text-gray-500">Dependencies: {component.dependencies.join(", ")}</p>
          <p className="text-[11px] font-mono text-gray-500">Data Stores: {component.dataStores.join(", ")}</p>
          <p className="text-[11px] font-mono text-gray-500">Assurance Signals: {component.assuranceSignals.join(", ")}</p>
          <p className="text-[11px] font-mono text-gray-500">Status: {component.status}</p>
        </div>
      ))}
    </div>
  );

  // Render the Interfaces & Contracts tab content
  const renderInterfacesContracts = () => (
    <div className="space-y-3">
      {technologyBOM.interfaces.map((iface) => (
        <div key={iface.name} className="rounded-md p-3 border bg-gray-50 border-gray-200">
          <h4 className="font-heading text-sm text-gray-900">{iface.name}</h4>
          <p className="text-xs font-body text-gray-600">Type: {iface.type}</p>
          <p className="text-xs font-body text-gray-600">Method: {iface.method}</p>
          <p className="text-xs font-body text-gray-600">Path: {iface.path}</p>
          <p className="text-xs font-body text-gray-600">Request Model: {iface.requestModel}</p>
          <p className="text-xs font-body text-gray-600">Response Model: {iface.responseModel}</p>
        </div>
      ))}
    </div>
  );

  // Render the Runtime Wiring tab content
  const renderRuntimeWiring = () => (
    <div className="space-y-3">
      {technologyBOM.runtimeWiring.map((wiring) => (
        <div key={wiring.service} className="rounded-md p-3 border bg-gray-50 border-gray-200">
          <h4 className="font-heading text-sm text-gray-900">{wiring.service}</h4>
          <p className="text-xs font-body text-gray-600">Port: {wiring.port}</p>
          <p className="text-xs font-body text-gray-600">Base URL: {wiring.baseUrl}</p>
          <p className="text-xs font-body text-gray-600">Dependencies: {wiring.dependencies.join(", ")}</p>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Tabs navigation */}
      <div className="flex gap-4">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setSelectedTab(tab.key)}
            className={`text-sm font-heading px-3 py-2 rounded-md border border-gray-200 ${
              selectedTab === tab.key
                ? "bg-teal-50 text-gray-900 border-teal-300"
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            {tab.title}
          </button>
        ))}
      </div>

      {/* Render content based on selected tab */}
      {renderTabContent()}

      {/* Add the Service Dependency Diagram */}
      <div className="space-y-4">
        <h4 className="font-heading text-lg text-gray-900">Service Dependency Diagram</h4>
        <div className="rounded-md p-4 border bg-gray-50 border-gray-200">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="100%"
            height="400"
            viewBox="0 0 400 400"
            fill="none"
          >
            <circle cx="100" cy="100" r="30" fill="#4fd1c5" />
            <circle cx="300" cy="100" r="30" fill="#4fd1c5" />
            <circle cx="200" cy="300" r="30" fill="#4fd1c5" />
            <line x1="100" y1="100" x2="300" y2="100" stroke="#b0e0e6" strokeWidth="2" />
            <line x1="300" y1="100" x2="200" y2="300" stroke="#b0e0e6" strokeWidth="2" />
            <line x1="200" y1="300" x2="100" y2="100" stroke="#b0e0e6" strokeWidth="2" />
            <text x="95" y="100" fill="white" fontFamily="Fjalla One" fontSize="16" textAnchor="middle">
              Frontend
            </text>
            <text x="295" y="100" fill="white" fontFamily="Fjalla One" fontSize="16" textAnchor="middle">
              BFF
            </text>
            <text x="195" y="300" fill="white" fontFamily="Fjalla One" fontSize="16" textAnchor="middle">
              Service-A
            </text>
          </svg>
        </div>
      </div>
    </div>
  );
}


