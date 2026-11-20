import { PageError } from "./page_error.js";

export class CoordinatorWorker {
  constructor(url) {
    this.url = url;
  }

  run(query) {
    return new Promise((resolve, reject) => {
      const worker = new Worker(this.url, { type: "module" });
      worker.onmessage = ({ data }) => {
        worker.terminate();
        data.error ? reject(new PageError(data.error, data.meta)) : resolve(data);
      };
      worker.onerror = (event) => {
        worker.terminate();
        reject(new Error(event.message || "worker failed"));
      };
      worker.postMessage(query);
    });
  }
}
