export class PageError extends Error {
  constructor(message, meta = {}) {
    super(message);
    this.meta = meta;
  }
}
