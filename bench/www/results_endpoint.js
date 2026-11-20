export class ResultsEndpoint {
  async post(runId, { csv, meta }) {
    await this.send("results", runId, { csv, meta: this.withAgent(meta) });
  }

  async postError(runId, error) {
    await this.send("errors", runId, { error: error.message, meta: this.withAgent(error.meta ?? {}) });
  }

  withAgent(meta) {
    return { ...meta, userAgent: navigator.userAgent };
  }

  async send(endpoint, runId, body) {
    const response = await fetch(`/${endpoint}?run=${encodeURIComponent(runId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`POST /${endpoint} ${response.status}: ${await response.text()}`);
    }
  }
}
