export const technologyBOM = {
  components: [
    {
      name: "frontend",
      type: "microservice",
      runtime: "docker",
      language: "JavaScript",
      framework: "React",
      repoPath: "app_frontend/src",
      interfaces: [
        { type: "REST", endpoint: "/api/clients", method: "GET", description: "Fetch clients data" },
        { type: "REST", endpoint: "/api/clients/{id}", method: "GET", description: "Fetch client details by ID" }
      ],
      dependencies: ["bff"],
      dataStores: ["client_database"],
      assuranceSignals: ["unit-test", "eslint", "security-scan"],
      status: "Live"
    },
    // Add more components as required...
  ],
  interfaces: [
    {
      name: "client-api",
      type: "REST",
      method: "GET",
      path: "/clients/{id}",
      requestModel: "ClientRequest",
      responseModel: "ClientResponse"
    },
    // Add more interfaces...
  ],
  runtimeWiring: [
    {
      service: "frontend",
      port: 8080,
      baseUrl: "http://localhost:8080",
      dependencies: ["bff"]
    },
    {
      service: "bff",
      port: 5000,
      baseUrl: "http://localhost:5000",
      dependencies: ["service-a"]
    },
    // Add more wiring...
  ]
};
