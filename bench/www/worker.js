import init, { buildInfo, clockStats, requestedThreads, run, startThreadPool } from "./pkg/bench.js";

async function measure(query, meta) {
  // Spawns N more Web Workers that share this module's WebAssembly.Memory and become the Rayon
  // pool. This worker coordinates: it blocks in run() while the pool works, which the page's main
  // thread may not do (Atomics.wait is not allowed there).
  // requestedThreads parses the whole configuration in Rust, so a bad query fails here, before
  // the pool starts.
  await startThreadPool(requestedThreads(query));
  const clock = JSON.parse(clockStats());
  meta.clockResolutionNs = clock.resolutionNs;
  meta.clockSmallestStepNs = clock.smallestStepNs;
  meta.hardwareConcurrency = navigator.hardwareConcurrency;
  return { csv: run(query), meta };
}

self.onmessage = async ({ data: query }) => {
  const meta = {};
  try {
    await init();
    meta.build = JSON.parse(buildInfo());
    self.postMessage(await measure(query, meta));
  } catch (error) {
    self.postMessage({ error: String(error?.message ?? error), meta });
  }
};
