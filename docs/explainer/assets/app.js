/* Documentation: shared behaviour. Plain script (no modules) so pages work from file://. */
(function () {
  "use strict";

  var D = window.PPC || {};
  var G = window.GLOSSARY || [];
  var STATIC = /[?&]static\b/.test(location.search);
  var REDUCED = STATIC || (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
  var REPO = "../../"; // docs/explainer -> repository root

  // Every page, in reading order. sections: [id, title] for search and the page outline.
  var PAGES = [
    {"id": "index", "file": "index.html", "title": "Introduction", "group": "Getting started", "sections": [["questions", "What the study asks", 2], ["found", "What it found", 2], ["found-rq1", "RQ1: browser threads scale like native threads", 3], ["found-rq2", "RQ2: synchronization changes the gap, and the engine decides how", 3], ["found-method", "Measured twice", 3], ["map", "How the project fits together", 2], ["read", "Where to read next", 2]]},
    {"id": "setup", "file": "setup.html", "title": "Installation and first run", "group": "Getting started", "sections": [["machines", "Two machines, two jobs", 2], ["install", "Install and build", 2], ["firstrun", "Run one thing", 2], ["firstrow", "Read one row", 2], ["firsttest", "Run the tests", 2], ["next", "Where to go next", 2]]},
    {"id": "code", "file": "code.html", "title": "Repository tour", "group": "Getting started", "sections": [["folders", "The folders", 2], ["picture", "How the three programs talk", 2], ["boundaries", "What crosses each boundary", 2], ["who", "Who starts whom", 2], ["onemachine", "On the Mac and on the PC", 2], ["bench", "bench/", 2], ["harness", "harness/", 2], ["analysis", "analysis/", 2], ["style", "Style rules and why", 2], ["questions", "Lookup: where is it done?", 2], ["symptoms", "Lookup: something broke", 2]]},
    {"id": "machines", "file": "machines.html", "title": "Threads and cores", "group": "Concepts", "sections": [["program", "A program and a process", 2], ["threads", "Threads: several hands, one memory", 2], ["cores", "Cores: how many hands can work at once", 2], ["clock", "The clock, turbo and SMT", 2], ["remember", "What to remember", 2]]},
    {"id": "memory", "file": "memory.html", "title": "Memory and caches", "group": "Concepts", "sections": [["far", "RAM is far away", 2], ["caches", "Caches: small, near, fast", 2], ["lines", "Data moves in lines of 64 bytes", 2], ["sharing", "Two cores, one line", 2], ["contention", "Contention", 2], ["falsesharing", "False sharing and padding", 2], ["hitm", "Counting line moves", 2]]},
    {"id": "compilers", "file": "compilers.html", "title": "From source to machine code", "group": "Concepts", "sections": [["source", "Source code and machine code", 2], ["compile", "Compiling ahead of time", 2], ["wasm", "WebAssembly: a second step inside the browser", 2], ["jit", "Engines and JIT", 2], ["remember", "What to remember", 2]]},
    {"id": "threads", "file": "threads.html", "title": "Thread pools and fork-join", "group": "Concepts", "sections": [["threads", "Threads and Web Workers", 2], ["rayon", "Rayon and work stealing", 2], ["forkjoin", "Fork-join and its cost", 2], ["grain", "Grain size", 2]]},
    {"id": "atomics", "file": "atomics.html", "title": "Atomic operations", "group": "Concepts", "sections": [["what", "What an atomic add is", 2], ["strategies", "Two ways to add: lock, or try and retry", 2], ["code", "What each engine emits", 2], ["order", "Memory order, for the record", 2], ["forwarding", "Store forwarding at k = 1", 2]]},
    {"id": "measuring", "file": "measuring.html", "title": "Measuring time", "group": "Concepts", "sections": [["noise", "The same program, different times", 2], ["repeat", "Repeat, then summarize", 2], ["spread", "Median, mean and spread", 2], ["sure", "How sure the result is", 2], ["fair", "A fair comparison", 2], ["remember", "What to remember", 2]]},
    {"id": "ratios", "file": "ratios.html", "title": "Ratios, speedup and intervals", "group": "Concepts", "sections": [["ratio", "Times faster, times slower", 2], ["speedup", "Speedup and efficiency", 2], ["log", "Why 2x and 0.5x are the same distance", 2], ["ratioofratios", "A ratio of ratios", 2], ["remember", "What to remember", 2]]},
    {"id": "validity", "file": "validity.html", "title": "How a study can be wrong", "group": "Concepts", "sections": [["internal", "Something else caused it", 2], ["construct", "The wrong thing was measured", 2], ["external", "It only holds here", 2], ["conclusion", "The numbers do not support it", 2], ["remember", "What to remember", 2]]},
    {"id": "rust", "file": "rust.html", "title": "Rust for JavaScript developers", "group": "Concepts", "sections": [["three", "Three ideas", 2], ["basics", "Types, ownership, borrowing", 2], ["traits", "Traits and generics", 2], ["rayon", "Rayon in the code", 2], ["atomics", "Atomics in the code", 2], ["wasm", "From Rust to WASM", 2]]},
    {"id": "questions", "file": "questions.html", "title": "Research questions and design", "group": "The study", "sections": [["why", "Why this matters", 2], ["rqs", "RQ1 and RQ2", 2], ["example", "RQ2 with made-up numbers", 2], ["design", "The design in one table", 2], ["cells", "Vocabulary: environment, workload, N, k", 2], ["runs", "Vocabulary: run, iteration, configuration, campaign", 2], ["builds", "Vocabulary: build, tag, variant", 2], ["numbers", "Vocabulary: the numbers", 2], ["related", "What others measured", 2]]},
    {"id": "workloads", "file": "workloads.html", "title": "Workloads", "group": "The study", "sections": [["filter", "The Gaussian filter", 2], ["histogram", "The histogram, two ways", 2], ["k", "k: the contention dial", 2], ["inputs", "Inputs and checksums", 2]]},
    {"id": "environments", "file": "environments.html", "title": "Environments and builds", "group": "The study", "sections": [["same", "Same source, same flags", 2], ["native", "Native", 2], ["browsers", "Chrome and Firefox", 2], ["update", "A pinned Firefox that updated itself", 2], ["wasm", "What WASM threads need", 2], ["builds", "Builds and tags", 2], ["v2", "The build history", 2]]},
    {"id": "machine", "file": "machine.html", "title": "The machine and environment control", "group": "The study", "sections": [["pc", "One PC, slowed down on purpose", 2], ["pcores", "P-cores only", 2], ["clock", "Turbo, governor, SMT", 2], ["core", "The degraded core", 2], ["quiet", "Shield and quiet mode", 2], ["mask", "A browser that left the mask", 2], ["checked", "Checked on every run", 2]]},
    {"id": "protocol", "file": "protocol.html", "title": "The run protocol", "group": "The study", "sections": [["unit", "The run is the unit", 2], ["pipeline", "From the harness to two files", 2], ["native", "A native run", 2], ["browser", "A browser run", 2], ["server", "The results server", 2], ["csv", "One CSV row, field by field", 2], ["warmup", "Warm-up inside the run", 2], ["startup", "The start delay", 2], ["thirty", "30 runs, 10 iterations", 2], ["order", "Random interleaved order", 2], ["calibration", "Fork-join calibration", 2]]},
    {"id": "reading", "file": "reading.html", "title": "Analysis plan and statistics", "group": "The study", "sections": [["onevalue", "One value per run", 2], ["average", "An average that respects ratios", 2], ["sure", "How sure: the interval", 2], ["decisions", "Ten decisions, a stricter bar", 2], ["notproof", "Not rejecting is not proof", 2], ["speedup", "In depth: speedup and efficiency", 2], ["geomean", "In depth: the geometric mean", 2], ["bootstrap", "In depth: bootstrap intervals", 2], ["rq2metric", "In depth: the RQ2 metric", 2], ["holm", "In depth: Holm and the primary contrasts", 2], ["robust", "In depth: Mann-Whitney and Cliff's delta", 2], ["karp", "In depth: Karp-Flatt", 2]]},
    {"id": "rq1", "file": "rq1.html", "title": "RQ1: scaling", "group": "Results", "sections": [["curves", "Speedup curves", 2], ["ratio", "Browser over native", 2], ["k1-forwarding", "The local histogram at k = 1: one counter, one chain", 3], ["forkjoin", "Fork-join in the results", 2], ["answer", "The answer to RQ1", 2]]},
    {"id": "rq2", "file": "rq2.html", "title": "RQ2: synchronization", "group": "Results", "sections": [["metric", "The metric, with the real numbers", 2], ["primary", "The 10 primary contrasts", 2], ["n1", "A difference with one thread", 2], ["code", "The machine code of one add", 2], ["probe", "A probe that changes only the add", 2], ["tier", "The other compiler of each engine", 2], ["retries", "Retries, counted", 2], ["readfirst", "Line transfers, counted", 2], ["k256", "k = 256: reproduced in direction, mechanism open", 2], ["c2c", "The padding holds", 2], ["answer", "The answer to RQ2", 2]]},
    {"id": "explains", "file": "explains.html", "title": "What explains the results", "group": "Results", "sections": [["how", "How an explanation is tested", 2], ["board", "Nine questions, one board", 2], ["q3", "Question 3: why the browser is slower with one thread", 2], ["q1", "Question 1: why 8 threads give 7, not 8", 2], ["q2", "Question 2: why Firefox scales better", 2], ["q5", "Question 5: a speedup above 8", 2], ["q4", "Question 4: the dip at 6 and 7 threads", 2], ["q67", "Questions 6 and 7: Chrome's atomic add", 2], ["q8", "Question 8: Firefox below 1", 2], ["q9", "Question 9: the noisy cells", 2], ["baseline", "Is the one-thread baseline fair?", 2], ["open", "What stays open", 2]]},
    {"id": "extras", "file": "extras.html", "title": "Exploratory campaigns", "group": "Results", "sections": [["questions", "The questions", 2], ["private", "Private and packed atomics", 2], ["weak", "Weak scaling", 2], ["simd", "SIMD builds", 2], ["hybrid", "P-cores plus E-cores", 2], ["cutoff", "How much work a region needs: the cutoff campaign", 2], ["forkjoin-share", "The fork-join next to the work", 3], ["rule", "The 100:1 rule", 2], ["grain", "How small a task may be: the grain sweep", 2], ["advice", "What this means for a developer", 2]]},
    {"id": "threats", "file": "threats.html", "title": "Threats to validity", "group": "Results", "sections": [["three", "The three that matter most", 2], ["internal", "Internal", 2], ["construct", "Construct", 2], ["external", "External", 2], ["conclusion", "Conclusion", 2]]},
    {"id": "campaigns", "file": "campaigns.html", "title": "Run a campaign", "group": "Guides", "sections": [["what", "What a campaign is", 2], ["spec", "A campaign spec", 2], ["resume", "Sessions, status and resume", 2], ["quality", "The data check", 2], ["list", "Every campaign of the study", 2]]},
    {"id": "reproduce", "file": "reproduce.html", "title": "Reproduce the tables and figures", "group": "Guides", "sections": [["chain", "The chain", 2], ["numbers", "Every paper number, its file", 2], ["explainer", "The numbers of this documentation", 2]]},
    {"id": "workload", "file": "workload.html", "title": "Add a workload", "group": "Guides", "sections": [["trait", "The trait", 2], ["workload", "Write and register the workload", 2], ["campaign", "Give it a campaign", 2], ["analysis", "Add its analysis", 2]]},
    {"id": "changing", "file": "changing.html", "title": "Change the measured path safely", "group": "Guides", "sections": [["rules", "The rules", 2], ["hotpath", "Change the measured code", 2], ["next", "Related guides", 2]]},
    {"id": "debugging", "file": "debugging.html", "title": "Debug a run", "group": "Guides", "sections": [["status", "Start from make status", 2], ["records", "The run's records", 2], ["rerun", "Re-run one id by hand", 2], ["common", "The common failures", 2]]},
    {"id": "trace", "file": "trace.html", "title": "Follow one run through the code", "group": "Guides", "sections": [["shape", "The shape before the steps", 2], ["native", "A native run", 2], ["browser", "A browser run", 2], ["analysis", "Into the analysis", 2]]},
    {"id": "session", "file": "session.html", "title": "The session of a build", "group": "Guides", "sections": [["twice", "Why the study was measured twice", 2], ["steps", "The steps, in order", 2], ["cores", "The per-core check", 2], ["build", "Built twice", 2], ["gate", "The gate, and the cell that failed it", 2], ["rules", "Rules fixed before the data", 2], ["campaigns", "Then the campaigns", 2]]},
    {"id": "workflow", "file": "workflow.html", "title": "Contribute: branches, PRs and ADRs", "group": "Guides", "sections": [["ticket", "A branch, small commits, a PR", 2], ["ci", "What CI checks", 2], ["review", "The bot review and the merge", 2], ["adr", "When a decision needs an ADR", 2], ["limits", "What is off limits", 2]]},
    {"id": "commands", "file": "commands.html", "title": "Commands", "group": "Reference", "sections": [["daily", "The six you use daily", 2], ["make", "make targets", 2], ["campaign", "Campaign commands", 2], ["analysis", "Analysis commands", 2]]},
    {"id": "spec", "file": "spec.html", "title": "Campaign spec format", "group": "Reference", "sections": [["example", "Example", 2], ["required", "Required keys", 2], ["optional", "Optional keys", 2], ["workloads", "Workload objects", 2], ["arms", "Engine arm objects", 2], ["plan", "What the harness plans from a spec", 2]]},
    {"id": "data", "file": "data.html", "title": "Data files, CSV schema and tables", "group": "Reference", "sections": [["onerow", "One row, read aloud", 2], ["raw", "data/raw", 2], ["tables", "data/tables", 2], ["json", "The run record", 2], ["figures", "Figures", 2]]},
    {"id": "decisions", "file": "decisions.html", "title": "ADR index", "group": "Reference", "sections": [["how", "How decisions are kept", 2], ["changed", "Decisions that changed", 2], ["map", "The ADRs by topic", 2]]},
    {"id": "lectures", "file": "lectures.html", "title": "Course lecture map", "group": "Reference", "sections": [["map", "Course concepts in the project", 2], ["l-embarrassing", "1. Embarrassingly parallel programming", 3], ["l-empirical", "2. Software empirical experimentation", 3], ["l-sync", "3. Synchronization", 3], ["l-java", "4. Concurrency in Java and irregular parallelism", 3], ["l-rust", "5. Concurrency in Rust", 3]]},
    {"id": "glossary", "file": "glossary.html", "title": "Glossary", "group": "Reference", "sections": []}
  ];

  // --- small helpers ------------------------------------------------------------
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else if (k === "html") node.innerHTML = attrs[k];
      else if (k.slice(0, 2) === "on") node.addEventListener(k.slice(2), attrs[k]);
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c != null) node.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return node;
  }
  function store(key, value) {
    try {
      if (value === undefined) return JSON.parse(localStorage.getItem("ppc." + key));
      localStorage.setItem("ppc." + key, JSON.stringify(value));
    } catch (e) { return null; }
    return value;
  }
  function fmt(n, digits) {
    if (n == null || isNaN(n)) return "–";
    var d = digits == null ? (Math.abs(n) >= 100 ? 0 : Math.abs(n) >= 10 ? 1 : 2) : digits;
    return Number(n).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function int(n) { return n == null ? "–" : Number(n).toLocaleString("en-US"); }
  function rows(name, where) {
    var all = ((D.tables || {})[name]) || [];
    if (!where) return all;
    return all.filter(function (r) {
      return Object.keys(where).every(function (k) { return String(r[k]) === String(where[k]); });
    });
  }
  function row(name, where) { return rows(name, where)[0] || null; }
  function get(path) {
    return path.split(".").reduce(function (o, k) { return o == null ? undefined : o[k]; }, D);
  }
  // Code links open in the browser or VS Code (a per-viewer choice in the top bar).
  var OPENERS = ["browser", "vscode"];
  var OPENER_LABEL = { browser: "Browser", vscode: "VS Code" };
  function opener() { var o = store("open"); return OPENERS.indexOf(o) >= 0 ? o : "browser"; }
  function repoRoot() {
    var path = decodeURIComponent(location.pathname);
    var at = path.lastIndexOf("/docs/explainer/");
    return at < 0 ? null : path.slice(0, at + 1);
  }
  function hrefFor(file, line) {
    var mode = opener(), root = repoRoot();
    if (mode === "browser" || !root || location.protocol !== "file:") return REPO + file;
    var abs = root + file;
    return "vscode://file" + encodeURI(abs) + (line ? ":" + line : "");
  }
  function repoLink(file, line) {
    var a = el("a", { href: hrefFor(file, line), text: file + (line ? ":" + line : "") });
    a.setAttribute("data-repo", file);
    if (line) a.setAttribute("data-line", line);
    a.title = "Open " + file + (line ? " at line " + line : "") + " (" + OPENER_LABEL[opener()] + ")";
    return a;
  }
  function retarget() {
    $$("a[data-repo]").forEach(function (a) {
      var file = a.getAttribute("data-repo"), line = a.getAttribute("data-line");
      a.href = hrefFor(file, line);
      a.title = "Open " + file + (line ? " at line " + line : "") + " (" + OPENER_LABEL[opener()] + ")";
    });
  }
  function initOpener() {
    var theme = $("#theme-btn");
    if (!theme || location.protocol !== "file:") return;
    var btn = el("button", { class: "icon-btn", id: "open-btn", type: "button", title: "Where code links open: browser or VS Code" });
    function label() { btn.textContent = "Code: " + OPENER_LABEL[opener()]; }
    btn.addEventListener("click", function () {
      store("open", OPENERS[(OPENERS.indexOf(opener()) + 1) % OPENERS.length]);
      label();
      retarget();
    });
    label();
    theme.parentNode.insertBefore(btn, theme);
  }

  // --- theme ----------------------------------------------------------------------
  function applyTheme(mode) {
    var root = document.documentElement;
    if (mode === "light" || mode === "dark") root.setAttribute("data-theme", mode);
    else root.removeAttribute("data-theme");
    var btn = $("#theme-btn");
    if (btn) btn.textContent = mode === "dark" ? "Dark" : mode === "light" ? "Light" : "Auto";
  }
  function initTheme() {
    applyTheme(store("theme") || "auto");
    var btn = $("#theme-btn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var order = ["auto", "light", "dark"];
      var next = order[(order.indexOf(store("theme") || "auto") + 1) % 3];
      store("theme", next);
      applyTheme(next);
    });
  }

  // --- navigation -------------------------------------------------------------------
  var current = document.body.getAttribute("data-page");

  var REAL_PAGES = PAGES.filter(function (p) { return !p.alias; });

  // Left column: every page in its group. The page's own sections are in the right column.
  function initNav() {
    var nav = $("#nav");
    if (!nav) return;
    nav.innerHTML = "";
    var groups = [];
    PAGES.forEach(function (p) {
      var g = groups.filter(function (x) { return x.name === p.group; })[0];
      if (!g) groups.push(g = { name: p.group, pages: [] });
      g.pages.push(p);
    });
    groups.forEach(function (g) {
      nav.appendChild(el("h4", { text: g.name }));
      var ol = el("ol");
      g.pages.forEach(function (p) {
        var a = el("a", { href: p.file, text: p.title });
        if (p.id === current) a.setAttribute("aria-current", "page");
        ol.appendChild(el("li", {}, [a]));
      });
      nav.appendChild(ol);
    });
    var here = $('a[aria-current="page"]', nav);
    if (here) nav.scrollTop = Math.max(0, here.offsetTop - nav.clientHeight / 2);

    var menu = $("#menu-btn");
    if (menu) menu.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menu.setAttribute("aria-expanded", String(open));
    });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) nav.classList.remove("open"); });

    var page = REAL_PAGES.filter(function (p) { return p.id === current; })[0];
    var h1 = $("main h1");
    if (page && h1) h1.parentNode.insertBefore(el("p", { class: "crumb", text: page.group }), h1);
  }

  // Right column: the h2 and h3 of this page, with the section in view highlighted.
  function initOutline() {
    var host = $("#outline");
    if (!host) return;
    var heads = $$("main h2[id], main h3[id]").filter(function (h) { return !h.closest("details, .card, .page-sources"); });
    if (heads.length < 2) return;
    host.appendChild(el("h4", { text: "On this page" }));
    var ol = el("ol");
    heads.forEach(function (h) {
      ol.appendChild(el("li", {}, [el("a", { href: "#" + h.id, "data-toc": h.id, class: h.tagName === "H3" ? "sub" : "", text: h.textContent })]));
    });
    host.appendChild(ol);
    var links = $$("[data-toc]", host);
    function mark() {
      var line = window.scrollY + 120, active = heads[0];
      heads.forEach(function (h) { if (h.getBoundingClientRect().top + window.scrollY <= line) active = h; });
      links.forEach(function (a) {
        var on = a.getAttribute("data-toc") === active.id;
        a.classList.toggle("active", on);
        if (on && host.scrollHeight > host.clientHeight) host.scrollTop = Math.max(0, a.offsetTop - host.clientHeight / 2);
      });
    }
    var queued = false;
    window.addEventListener("scroll", function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () { queued = false; mark(); });
    }, { passive: true });
    mark();
  }

  function initPager() {
    var pager = $("#pager");
    if (!pager) return;
    var i = REAL_PAGES.findIndex(function (p) { return p.id === current; });
    var prev = REAL_PAGES[i - 1], next = REAL_PAGES[i + 1];
    pager.appendChild(prev ? el("a", { href: prev.file, class: "prev" }, [el("small", { text: "Previous" }), prev.title]) : el("span"));
    pager.appendChild(next ? el("a", { href: next.file, class: "next" }, [el("small", { text: "Next" }), next.title]) : el("span"));
  }

  // "This page rests on": every table, file and decision record the page names, in one list at its end.
  function initPageSources() {
    var pager = $("#pager");
    if (!pager || $(".page-sources")) return;
    var seen = {}, files = [];
    $$("main .src a[data-repo]").forEach(function (a) {
      var f = a.getAttribute("data-repo");
      if (!seen[f]) { seen[f] = true; files.push(f); }
    });
    if (!files.length) return;
    files.sort();
    var box = el("section", { class: "page-sources" }, [el("h2", { text: "This page rests on" })]);
    var ul = el("ul");
    files.forEach(function (f) { ul.appendChild(el("li", {}, [repoLink(f)])); });
    box.appendChild(ul);
    pager.parentNode.insertBefore(box, pager);
  }

  // Every code block gets a language label and a copy button.
  var LANGS = { rs: "rust", py: "python", js: "javascript", json: "json", sh: "shell", mk: "make", toml: "toml", md: "markdown", yml: "yaml", csv: "csv", txt: "text", s: "asm", asm: "asm", wat: "wat", log: "log", html: "html" };
  var SHELL_LINE = /^\s*(\$ |make |git |python3 |cargo |bash |cd |sudo |ls |taskset |uv )/m;
  function copyButton(getText) {
    var b = el("button", { type: "button", class: "copy-btn", text: "Copy" });
    function done() { b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1200); }
    function viaSelection() {
      var ta = el("textarea", { style: "position:fixed;opacity:0" });
      ta.value = getText();
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(); } catch (e) { /* the browser refused; nothing else to try */ }
      document.body.removeChild(ta);
    }
    b.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(getText()).then(done, viaSelection);
      else viaSelection();
    });
    return b;
  }
  function langOf(pre) {
    if (pre.getAttribute("data-lang")) return pre.getAttribute("data-lang");
    if (pre.classList.contains("out")) return "output";
    if (pre.classList.contains("plain")) return "asm";
    return SHELL_LINE.test(pre.textContent) ? "shell" : "text";
  }
  function initCopy(root) {
    $$("main pre", root).forEach(function (pre) {
      if (pre._copy || pre.closest("figure.code, .block")) return;
      pre._copy = true;
      var block = el("div", { class: "block" });
      pre.parentNode.insertBefore(block, pre);
      block.appendChild(el("div", { class: "code-head" }, [el("span", { class: "lang", text: langOf(pre) }), copyButton(function () { return pre.textContent; })]));
      block.appendChild(pre);
    });
  }

  // --- search ---------------------------------------------------------------------------
  function searchIndex() {
    var items = [];
    PAGES.forEach(function (p) {
      items.push({ title: p.title, where: p.group, href: p.file, text: p.title });
      p.sections.forEach(function (s) { items.push({ title: s[1], where: p.title, href: p.file + "#" + s[0], text: s[1] }); });
    });
    G.forEach(function (t) { items.push({ title: t.term, where: "Glossary", href: "glossary.html#" + t.id, text: t.term + " " + t.def }); });
    return items;
  }
  function initSearch() {
    var box = $("#search");
    if (!box) return;
    var input = $("input", box), list = $(".results", box);
    var items = searchIndex(), shown = [], sel = -1;
    function render(q) {
      list.innerHTML = "";
      sel = -1;
      q = q.trim().toLowerCase();
      if (!q) { list.classList.remove("open"); return; }
      var words = q.split(/\s+/);
      shown = items.map(function (it) {
        var t = it.text.toLowerCase(), title = it.title.toLowerCase(), score = 0;
        for (var i = 0; i < words.length; i++) {
          if (t.indexOf(words[i]) < 0) return null;
          score += title.indexOf(words[i]) === 0 ? 3 : title.indexOf(words[i]) >= 0 ? 2 : 1;
        }
        return { it: it, score: score };
      }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 12).map(function (x) { return x.it; });
      if (!shown.length) list.appendChild(el("div", { class: "muted", style: "padding:8px 10px", text: "Nothing found." }));
      shown.forEach(function (it, i) {
        list.appendChild(el("a", { href: it.href, role: "option", id: "sr-" + i }, [it.title, el("small", { text: it.where })]));
      });
      list.classList.add("open");
    }
    input.addEventListener("input", function () { render(input.value); });
    input.addEventListener("keydown", function (e) {
      var links = $$("a", list);
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        sel = Math.max(0, Math.min(links.length - 1, sel + (e.key === "ArrowDown" ? 1 : -1)));
        links.forEach(function (a, i) { a.setAttribute("aria-selected", String(i === sel)); });
      } else if (e.key === "Enter" && links.length) {
        location.href = links[Math.max(sel, 0)].href;
      } else if (e.key === "Escape") { input.value = ""; render(""); input.blur(); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== input && !/input|textarea|select/i.test(document.activeElement.tagName)) {
        e.preventDefault(); input.focus();
      }
    });
    document.addEventListener("click", function (e) { if (!box.contains(e.target)) list.classList.remove("open"); });
  }

  // --- glossary terms in the text -------------------------------------------------------
  var pop;
  function initTerms() {
    var byId = {};
    G.forEach(function (t) { byId[t.id] = t; });
    $$("[data-term]").forEach(function (node) {
      var t = byId[node.getAttribute("data-term")];
      if (!t || node._term) return;
      node._term = true;
      node.classList.add("term");
      if (node.tagName !== "A") { node.setAttribute("tabindex", "0"); node.setAttribute("role", "button"); }
      node.setAttribute("aria-label", node.textContent + ": " + t.def);
      function show() {
        hide();
        pop = el("div", { class: "pop", role: "tooltip" }, [el("b", { text: t.term }), document.createElement("br"), t.def + " ",
          el("a", { href: "glossary.html#" + t.id, text: "Glossary" })]);
        document.body.appendChild(pop);
        var r = node.getBoundingClientRect();
        pop.style.left = Math.max(8, Math.min(window.scrollX + r.left, window.scrollX + document.documentElement.clientWidth - pop.offsetWidth - 8)) + "px";
        pop.style.top = (window.scrollY + r.bottom + 6) + "px";
      }
      node.addEventListener("mouseenter", show);
      node.addEventListener("focus", show);
      node.addEventListener("mouseleave", function () { setTimeout(function () { if (pop && !pop.matches(":hover")) hide(); }, 200); });
      node.addEventListener("blur", function () { setTimeout(hide, 150); });
      node.addEventListener("keydown", function (e) { if (e.key === "Escape") hide(); });
    });
  }
  function hide() { if (pop) { pop.remove(); pop = null; } }

  // --- sources --------------------------------------------------------------------------
  // <p class="src" data-src="campaign-v3-scaling, perf-v3-counters"></p> lists the tables behind a
  // widget (D.sources maps each name to its CSV); <p class="src" data-files="bench/src/a.rs:12"></p>
  // lists code files.
  function initSources(root) {
    $$("[data-src]", root).forEach(function (node) {
      if (node._src) return;
      node._src = true;
      var names = node.getAttribute("data-src").split(",").map(function (x) { return x.trim(); }).filter(Boolean);
      names.forEach(function (name, i) {
        if (i) node.appendChild(document.createTextNode(", "));
        node.appendChild(repoLink((D.sources || {})[name] || name));
      });
    });
    $$("[data-files]", root).forEach(function (node) {
      if (node._src) return;
      node._src = true;
      node.getAttribute("data-files").split(",").map(function (f) { return f.trim(); }).forEach(function (f, i) {
        if (i) node.appendChild(document.createTextNode(", "));
        var m = f.match(/^(.*?)(?::(\d+))?$/);
        node.appendChild(repoLink(m[1], m[2]));
      });
    });
  }

  // --- components ------------------------------------------------------------------------
  function code(key, opts) {
    opts = opts || {};
    // key: "path|first line|lines", resolved by scripts/explainer_data.py into D.code.
    var c = typeof key !== "string" ? key : (D.code || {})[key];
    var box = el("figure", { class: "code" });
    if (!c) { box.appendChild(el("pre", { text: "(excerpt not found: " + key + ")" })); return box; }
    var lines = c.text.split("\n"), first = c.line || 1;
    var ext = c.file.split(".").pop();
    box.appendChild(el("header", {}, [el("span", {}, [el("span", { class: "lang", text: LANGS[ext] || ext }), opts.title ? " · " + opts.title : ""]),
      el("span", {}, [repoLink(c.file, first), " ", copyButton(function () { return c.text; })])]));
    var pre = el("pre");
    lines.forEach(function (ln, i) {
      var hl = (opts.highlight && opts.highlight.test(ln)) || (opts.lines && opts.lines.indexOf(first + i) >= 0);
      var row = el("span", { class: "row" + (hl ? " hl" : "") });
      row.appendChild(el("span", { class: "ln", text: String(first + i) }));
      row.appendChild(document.createTextNode(ln));
      pre.appendChild(row);
    });
    box.appendChild(pre);
    return box;
  }

  function segmented(container, options, onChange, initial) {
    var seg = el("div", { class: "seg", role: "group" });
    options.forEach(function (o) {
      var b = el("button", { type: "button", "aria-pressed": "false", text: o.label });
      b.addEventListener("click", function () { pick(o.value); });
      b._value = o.value;
      seg.appendChild(b);
    });
    function pick(v) {
      $$("button", seg).forEach(function (b) { b.setAttribute("aria-pressed", String(b._value === v)); });
      onChange(v);
    }
    container.appendChild(seg);
    pick(initial == null ? options[0].value : initial);
    return { pick: pick };
  }

  // stepper(host, [{title, render(stage)}]): numbered steps with previous/next and the arrow keys.
  function stepper(host, steps, opts) {
    opts = opts || {};
    host.classList.add("stepper");
    var bar = el("div", { class: "steps", role: "tablist" });
    var stage = el("div", { class: "stage", "aria-live": "polite" });
    var ctrl = el("div", { class: "controls" });
    var prev = el("button", { class: "btn", type: "button", text: "← Previous" });
    var next = el("button", { class: "btn primary", type: "button", text: "Next →" });
    var all = el("button", { class: "btn", type: "button", text: "Show all" });
    ctrl.append(prev, next, all);
    host.append(bar, stage, ctrl);
    var i = 0;
    steps.forEach(function (s, k) {
      var b = el("button", { type: "button", role: "tab", text: (k + 1) + ". " + s.title });
      b.addEventListener("click", function () { go(k); });
      bar.appendChild(b);
    });
    function go(k) {
      i = Math.max(0, Math.min(steps.length - 1, k));
      $$("button", bar).forEach(function (b, n) {
        b.classList.toggle("done", n < i);
        if (n === i) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current");
      });
      stage.innerHTML = "";
      steps[i].render(stage, i);
      prev.disabled = i === 0;
      next.disabled = i === steps.length - 1;
      if (opts.onStep) opts.onStep(i);
    }
    prev.addEventListener("click", function () { go(i - 1); });
    next.addEventListener("click", function () { go(i + 1); });
    all.addEventListener("click", function () {
      stage.innerHTML = "";
      steps.forEach(function (s, k) { var part = el("div"); part.appendChild(el("h4", { text: (k + 1) + ". " + s.title })); s.render(part, k); stage.appendChild(part); });
    });
    host.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { go(i + 1); e.preventDefault(); }
      if (e.key === "ArrowLeft") { go(i - 1); e.preventDefault(); }
    });
    go(opts.start || 0);
    return { go: go };
  }

  // trace(host, steps): "follow the call", one step per line that runs.
  // step: { title, code: excerpt key ("etl.timed_load") or excerpt object, line: number or [numbers] to
  //         highlight, say: html (what happens), memory: [[name, value]] (what the variables hold now) }
  function trace(host, steps, opts) {
    opts = opts || {};
    host.classList.add("trace");
    return stepper(host, steps.map(function (s, k) {
      return { title: s.title, render: function (stage) {
        var grid = el("div", { class: "trace-grid" });
        var left = el("div", { class: "trace-code" });
        var c = typeof s.code === "string" ? (D.code || {})[s.code] : s.code;
        var lines = s.line == null ? [] : [].concat(s.line);
        if (c) left.appendChild(code(c, { title: s.file || (c.file + (lines.length ? ":" + lines[0] : "")), lines: lines, highlight: s.highlight }));
        else left.appendChild(el("p", { class: "muted", text: "(excerpt not found: " + s.code + ")" }));
        var right = el("div", { class: "trace-say" });
        right.appendChild(el("div", { class: "trace-step", text: "Step " + (k + 1) + " of " + steps.length }));
        right.appendChild(el("div", { html: s.say || "" }));
        if (s.memory && s.memory.length) {
          var mem = el("table", { class: "t mem" });
          mem.appendChild(el("thead", {}, [el("tr", {}, [el("th", { text: "In memory now" }), el("th", { text: "" })])]));
          var tb = el("tbody");
          s.memory.forEach(function (m) {
            tb.appendChild(el("tr", {}, [el("td", {}, [el("code", { text: m[0] })]), el("td", { html: m[1] })]));
          });
          mem.appendChild(tb);
          right.appendChild(mem);
        }
        if (s.next) right.appendChild(el("p", { class: "trace-next", html: "<b>Next:</b> " + s.next }));
        grid.append(left, right);
        stage.appendChild(grid);
        requestAnimationFrame(function () {
          var pre = left.querySelector("pre"), hl = pre && pre.querySelector(".row.hl");
          if (pre && hl) pre.scrollTop = Math.max(0, hl.offsetTop - pre.clientHeight / 3);
        });
      } };
    }), opts);
  }

  // table(rows, columns): columns [{label, key|value(row), num}]
  function table(rows, columns) {
    var t = el("table", { class: "t" });
    var thead = el("thead"), tr = el("tr");
    columns.forEach(function (c) { tr.appendChild(el("th", { class: c.num ? "n" : "", text: c.label })); });
    thead.appendChild(tr); t.appendChild(thead);
    var tb = el("tbody");
    rows.forEach(function (r) {
      var row = el("tr");
      columns.forEach(function (c) {
        var v = c.value ? c.value(r) : r[c.key];
        var td = el("td", { class: c.num ? "n" : "" });
        if (v instanceof Node) td.appendChild(v); else td.textContent = v == null ? "–" : v;
        row.appendChild(td);
      });
      tb.appendChild(row);
    });
    t.appendChild(tb);
    return el("div", { class: "scroll-x" }, [t]);
  }

  // bars(series, opts): grouped horizontal bars; series [{label, values:[{name, value, cls}]}]; opts {max, min, log, unit, digits}
  function bars(series, opts) {
    opts = opts || {};
    var max = opts.max || Math.max.apply(null, series.reduce(function (a, s) { return a.concat(s.values.map(function (v) { return v.value || 0; })); }, [1]));
    var log = !!opts.log, minv = opts.min || 0.1;
    function scale(v) {
      if (!v) return 0;
      if (log) return Math.max(0, (Math.log10(v) - Math.log10(minv)) / (Math.log10(max) - Math.log10(minv)));
      return v / max;
    }
    var wrap = el("div", { class: "bars" });
    series.forEach(function (s) {
      var row = el("div", { style: "display:grid;grid-template-columns:minmax(80px,140px) 1fr;gap:8px;align-items:center;margin:6px 0" });
      row.appendChild(el("div", { style: "font-size:var(--fs-sm);color:var(--ink)", text: s.label }));
      var col = el("div");
      s.values.forEach(function (v) {
        var line = el("div", { style: "display:flex;align-items:center;gap:6px;margin:2px 0" });
        var bar = el("div", { style: "height:14px;border-radius:4px;background:var(--" + (v.cls || "accent") + ");width:0", title: v.name + ": " + fmt(v.value, opts.digits) + (opts.unit || "") });
        line.appendChild(bar);
        line.appendChild(el("span", { style: "font-size:var(--fs-xs);color:var(--muted);white-space:nowrap", text: (v.label ? v.label + " " : "") + fmt(v.value, opts.digits) + (opts.unit || "") }));
        col.appendChild(line);
        var w = (100 * scale(v.value)) + "%";
        bar.style.width = w;
        if (!REDUCED) { bar.style.transformOrigin = "left"; bar.style.transform = "scaleX(0)"; requestAnimationFrame(function () { bar.style.transition = "transform 0.6s"; bar.style.transform = "none"; }); }
      });
      row.appendChild(col);
      wrap.appendChild(row);
    });
    return wrap;
  }

  // diagram(svgMarkup): inserts an SVG and wires boxes with data-key to a details panel.
  function clickable(svgHost, panel, details) {
    var boxes = $$("[data-key]", svgHost);
    function pick(key) {
      boxes.forEach(function (b) { b.classList.toggle("sel", b.getAttribute("data-key") === key); });
      panel.innerHTML = "";
      var d = details[key];
      if (d) d(panel);
    }
    boxes.forEach(function (b) {
      b.classList.add("click");
      b.setAttribute("tabindex", "0");
      b.setAttribute("role", "button");
      b.addEventListener("click", function () { pick(b.getAttribute("data-key")); });
      b.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(b.getAttribute("data-key")); } });
    });
    return { pick: pick };
  }

  window.UI = {
    D: D, G: G, STATIC: STATIC, REDUCED: REDUCED, REPO: REPO, PAGES: PAGES,
    $: $, $$: $$, el: el, fmt: fmt, int: int, get: get, rows: rows, row: row, repoLink: repoLink, hrefFor: hrefFor,
    code: code, sources: initSources, segmented: segmented, stepper: stepper, trace: trace, table: table, bars: bars, clickable: clickable, store: store
  };

  // <div data-code="bench/src/x.rs|fn name|12" data-title="..."></div> becomes a code excerpt.
  function initCode(root) {
    $$("[data-code]", root).forEach(function (node) {
      if (node._code) return;
      node._code = true;
      var hl = node.getAttribute("data-highlight");
      node.appendChild(code(node.getAttribute("data-code"), { title: node.getAttribute("data-title") || "", highlight: hl ? new RegExp(hl) : null }));
    });
  }

  function boot() {
    if (STATIC) document.documentElement.classList.add("static");
    initTheme();
    initNav();
    initPager();
    initSearch();
    initCode();
    initSources();
    initTerms();
    if (typeof window.page === "function") window.page(window.UI);
    initSources(); // sources and terms added by the page's own widgets
    initTerms();
    initCopy();
    initPageSources();
    initOutline();
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") hide(); });
    // widgets that redraw (tabs, steppers) add new sources and terms later
    var main = $("main"), queued = false;
    if (main && "MutationObserver" in window) new MutationObserver(function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () { queued = false; initSources(main); initTerms(); initCopy(main); });
    }).observe(main, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
