export class PageStatus {
  constructor(element) {
    this.element = element;
  }

  set(state, detail = "") {
    document.title = state;
    this.element.textContent = detail ? `${state}: ${detail}` : state;
  }
}
