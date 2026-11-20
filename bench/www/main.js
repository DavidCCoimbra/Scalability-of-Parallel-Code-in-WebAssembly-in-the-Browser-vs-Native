import { CoordinatorWorker } from "./coordinator_worker.js";
import { PageError } from "./page_error.js";
import { PageStatus } from "./page_status.js";
import { ResultsEndpoint } from "./results_endpoint.js";

const RUN_PARAMETER = "run";
const START_DELAY_PARAMETER = "startDelayMs";
const MAX_START_DELAY_MS = 2 ** 31 - 1;

function splitRunId(search) {
  const parameters = new URLSearchParams(search);
  const runId = parameters.get(RUN_PARAMETER);
  if (!runId) {
    throw new Error(`missing ${RUN_PARAMETER} parameter`);
  }
  const startDelay = parameters.get(START_DELAY_PARAMETER) ?? "0";
  parameters.delete(RUN_PARAMETER);
  parameters.delete(START_DELAY_PARAMETER);
  return { runId, startDelay, query: parameters.toString() };
}

function startDelayMs(value) {
  const delay = Number(value);
  if (!/^\d+$/.test(value) || delay > MAX_START_DELAY_MS) {
    throw new PageError(`invalid ${START_DELAY_PARAMETER} parameter "${value}"`);
  }
  return delay;
}

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function measure(runId, startDelay, query, status) {
  // Shared WebAssembly memory is a SharedArrayBuffer, which browsers only allow on a page served
  // with COOP/COEP headers (harness/server.py); without them the pool cannot start, so fail early
  // with a clear error.
  if (!globalThis.crossOriginIsolated) {
    throw new PageError("page is not cross-origin isolated (COOP/COEP headers missing)");
  }
  const delay = startDelayMs(startDelay);
  status.set("waiting", runId);
  await sleep(delay);
  status.set("running", runId);
  const result = await new CoordinatorWorker(new URL("./worker.js", import.meta.url)).run(query);
  await new ResultsEndpoint().post(runId, result);
  status.set("done", runId);
}

async function main(status) {
  const { runId, startDelay, query } = splitRunId(location.search);
  try {
    await measure(runId, startDelay, query, status);
  } catch (error) {
    status.set("error", error.message);
    await new ResultsEndpoint().postError(runId, error);
  }
}

const status = new PageStatus(document.getElementById("status"));
main(status).catch((error) => {
  console.error(error);
  status.set("error", error.message);
});
