/* PPC explainer: shared behaviour. Plain script (no modules) so pages work from file://. */
(function () {
  "use strict";

  var D = window.PPC || {};
  var G = window.GLOSSARY || [];
  var STATIC = /[?&]static\b/.test(location.search);
  var REDUCED = STATIC || (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
  var REPO = "../../"; // docs/explainer -> repository root

  // Every page, in reading order. sections: [id, title] for search and the page outline.
  var PAGES = [
    { id: "index", file: "index.html", title: "Start here", group: "0 · Start",
      sections: [["story", "The study in a story"], ["map", "The project in one picture"], ["answers", "What we found, in words"], ["how", "How to read this guide"], ["criteria", "For the grader: criterion by criterion"]] },
    { id: "setup", file: "setup.html", title: "Your first day", group: "0 · Start",
      sections: [["machines", "Two machines, two jobs"], ["install", "Install and build"], ["firstrun", "Run one thing"], ["firstrow", "Read one row"], ["firsttest", "Run the tests"], ["next", "Where to go next"]] },
    { id: "machines", file: "machines.html", title: "Programs, processes, threads and cores", group: "1 · Foundations",
      sections: [["program", "A program and a process"], ["threads", "Threads: several hands, one memory"], ["cores", "Cores: how many hands can work at once"], ["clock", "The clock, turbo and SMT"], ["remember", "What to remember"]] },
    { id: "memory", file: "memory.html", title: "Memory and caches: why distance matters", group: "1 · Foundations",
      sections: [["far", "RAM is far away"], ["caches", "Caches: small, near, fast"], ["lines", "Data moves in lines of 64 bytes"], ["sharing", "Two cores, one line"], ["remember", "What to remember"]] },
    { id: "compilers", file: "compilers.html", title: "From source to machine code", group: "1 · Foundations",
      sections: [["source", "Source code and machine code"], ["compile", "Compiling ahead of time"], ["wasm", "WebAssembly: a second step inside the browser"], ["jit", "Engines and JIT"], ["remember", "What to remember"]] },
    { id: "measuring", file: "measuring.html", title: "Measuring time: why one run is not enough", group: "1 · Foundations",
      sections: [["noise", "The same program, different times"], ["repeat", "Repeat, then summarize"], ["spread", "Median, mean and spread"], ["sure", "How sure can we be"], ["fair", "A fair comparison"], ["remember", "What to remember"]] },
    { id: "ratios", file: "ratios.html", title: "Ratios, speedup and the log scale", group: "1 · Foundations",
      sections: [["ratio", "Times faster, times slower"], ["speedup", "Speedup and efficiency"], ["log", "Why 2x and 0.5x are the same distance"], ["ratioofratios", "A ratio of ratios"], ["remember", "What to remember"]] },
    { id: "validity", file: "validity.html", title: "Four ways a study fools itself", group: "1 · Foundations",
      sections: [["internal", "Something else caused it"], ["construct", "We measured the wrong thing"], ["external", "It only holds here"], ["conclusion", "The numbers do not support it"], ["remember", "What to remember"]] },
    { id: "questions", file: "questions.html", title: "Questions and design", group: "2 · The study",
      sections: [["why", "Why this matters"], ["rqs", "RQ1 and RQ2"], ["example", "RQ2 with made-up numbers"], ["design", "The design in one table"], ["related", "What others measured"]] },
    { id: "workloads", file: "workloads.html", title: "The workloads", group: "2 · The study",
      sections: [["filter", "The Gaussian filter"], ["histogram", "The histogram, two ways"], ["k", "k: the contention dial"], ["inputs", "Inputs and checksums"]] },
    { id: "environments", file: "environments.html", title: "Three runtimes, one source", group: "2 · The study",
      sections: [["same", "Same source, same flags"], ["native", "Native"], ["browsers", "Chrome and Firefox"], ["wasm", "What WASM threads need"], ["builds", "Builds and tags"]] },
    { id: "words", file: "words.html", title: "Words of the project", group: "2 · The study",
      sections: [["cells", "Environment, workload, N, k"], ["runs", "Run, iteration, configuration, campaign"], ["builds", "Build, tag, variant"], ["numbers", "The numbers"]] },
    { id: "threads", file: "threads.html", title: "Threads, workers and fork-join", group: "3 · Concepts",
      sections: [["threads", "Threads and Web Workers"], ["rayon", "Rayon and work stealing"], ["forkjoin", "Fork-join and its cost"], ["grain", "Grain size"]] },
    { id: "caches", file: "caches.html", title: "Contention and padding", group: "3 · Concepts",
      sections: [["lines", "One line, one writer"], ["contention", "Contention"], ["falsesharing", "False sharing and padding"], ["hitm", "Counting line moves"]] },
    { id: "atomics", file: "atomics.html", title: "Atomics in machine code", group: "3 · Concepts",
      sections: [["what", "What an atomic add is"], ["strategies", "Two ways to add: lock, or try and retry"], ["code", "What each engine emits"], ["order", "Memory order, for the record"], ["forwarding", "Store forwarding at k = 1"]] },
    { id: "rust", file: "rust.html", title: "Rust for JS developers", group: "3 · Concepts",
      sections: [["three", "Three ideas"], ["basics", "Types, ownership, borrowing"], ["traits", "Traits and generics"], ["rayon", "Rayon in the code"], ["atomics", "Atomics in the code"], ["wasm", "From Rust to WASM"]] },
    { id: "machine", file: "machine.html", title: "The machine and its controls", group: "4 · Method",
      sections: [["pc", "One PC, slowed down on purpose"], ["pcores", "P-cores only"], ["clock", "Turbo, governor, SMT"], ["quiet", "Shield and quiet mode"], ["checked", "Checked on every run"]] },
    { id: "harness", file: "harness.html", title: "From make to a CSV row", group: "4 · Method",
      sections: [["pipeline", "The run pipeline"], ["native", "A native run"], ["browser", "A browser run"], ["server", "The results server"], ["csv", "One CSV row, field by field"]] },
    { id: "protocol", file: "protocol.html", title: "Runs, warm-up and order", group: "4 · Method",
      sections: [["unit", "The run is the unit"], ["warmup", "Warm-up inside the run"], ["thirty", "30 runs, 10 iterations"], ["order", "Random interleaved order"], ["calibration", "Fork-join calibration"]] },
    { id: "session", file: "session.html", title: "The session of a build", group: "4 · Method",
      sections: [["twice", "Why the study was measured twice"], ["steps", "The steps, in order"], ["cores", "The per-core check"], ["build", "Built twice"], ["gate", "The gate, and the cell that failed it"], ["rules", "Rules fixed before the data"], ["campaigns", "Then the campaigns"]] },
    { id: "reading", file: "reading.html", title: "Reading the numbers", group: "4 · Method",
      sections: [["onevalue", "One value per run"], ["average", "An average that respects ratios"], ["sure", "How sure: the interval"], ["decisions", "Ten decisions, a stricter bar"], ["notproof", "Not rejecting is not proof"]] },
    { id: "stats", file: "stats.html", title: "The statistics, in detail", group: "4 · Method",
      sections: [["speedup", "Speedup and efficiency"], ["geomean", "Geometric mean"], ["bootstrap", "Bootstrap intervals"], ["rq2metric", "The RQ2 metric"], ["holm", "Holm and the primary contrasts"], ["robust", "Mann-Whitney and Cliff's delta"], ["karp", "Karp-Flatt"]] },
    { id: "rq1", file: "rq1.html", title: "RQ1: scaling", group: "5 · Results",
      sections: [["curves", "Speedup curves"], ["ratio", "Browser over native"], ["forkjoin", "Fork-join in the results"], ["answer", "The answer to RQ1"]] },
    { id: "rq2", file: "rq2.html", title: "RQ2: synchronization", group: "5 · Results",
      sections: [["metric", "The metric, with the real numbers"], ["primary", "The 10 primary contrasts"], ["n1", "Already at N = 1"], ["answer", "The answer to RQ2"]] },
    { id: "why", file: "why.html", title: "Why Chrome: code and counters", group: "5 · Results",
      sections: [["code", "The machine code"], ["probe", "The test: change only the add"], ["tier", "The engine's other compiler"], ["retries", "Retries, counted"], ["readfirst", "Reading the line first"], ["k256", "k = 256: the sequence wins, the mechanism is open"], ["c2c", "The padding holds"]] },
    { id: "explains", file: "explains.html", title: "What explains the results", group: "5 · Results",
      sections: [["how", "How an explanation is tested"], ["board", "Nine questions, one board"], ["q3", "Question 3: why the browser is slower with one thread"], ["q1", "Question 1: why 8 threads give 7, not 8"], ["q2", "Question 2: why Firefox scales better"], ["q5", "Question 5: a speedup above 8"], ["q4", "Question 4: the dip at 6 and 7 threads"], ["q67", "Questions 6 and 7: Chrome's atomic add"], ["q8", "Question 8: Firefox below 1"], ["q9", "Question 9: the noisy cells"], ["baseline", "Is the one-thread baseline fair?"], ["open", "What stays open"]] },
    { id: "extras", file: "extras.html", title: "Exploratory campaigns", group: "5 · Results",
      sections: [["questions", "Five questions"], ["private", "Private and packed atomics"], ["weak", "Weak scaling"], ["simd", "SIMD builds"], ["hybrid", "P-cores plus E-cores"]] },
    { id: "granularity", file: "granularity.html", title: "When parallelism pays", group: "5 · Results",
      sections: [["advice", "Advice for developers"], ["cutoff", "The cutoff campaign"], ["rule", "The 100:1 rule"], ["grain", "The grain U-curve"]] },
    { id: "pitfalls", file: "pitfalls.html", title: "Problems found and fixed", group: "5 · Results",
      sections: [["mask", "Chrome escapes the CPU mask"], ["startup", "Firefox's start-up"], ["update", "A pinned Firefox updates itself"], ["v2", "Our own asymmetries: the v2 build"]] },
    { id: "threats", file: "threats.html", title: "Threats to validity", group: "5 · Results",
      sections: [["three", "The three that matter most"], ["internal", "Internal"], ["construct", "Construct"], ["external", "External"], ["conclusion", "Conclusion"]] },
    { id: "pieces", file: "pieces.html", title: "How the pieces talk", group: "6 · Working on it",
      sections: [["picture", "Processes, files and ports"], ["boundaries", "What crosses each boundary"], ["who", "Who starts whom"], ["onemachine", "On the Mac and on the PC"]] },
    { id: "commands", file: "commands.html", title: "Every command", group: "6 · Working on it",
      sections: [["daily", "The six you use daily"], ["make", "make targets"], ["campaign", "Campaign commands"], ["analysis", "Analysis commands"]] },
    { id: "campaigns", file: "campaigns.html", title: "Campaigns, specs and resume", group: "6 · Working on it",
      sections: [["what", "What a campaign is"], ["spec", "A campaign spec"], ["resume", "Sessions, status and resume"], ["quality", "The data check"], ["list", "Every campaign of the study"]] },
    { id: "data", file: "data.html", title: "Data folders and files", group: "6 · Working on it",
      sections: [["onerow", "One row, read aloud"], ["raw", "data/raw"], ["tables", "data/tables"], ["json", "The run record"], ["figures", "Figures"]] },
    { id: "reproduce", file: "reproduce.html", title: "From raw runs to the paper", group: "6 · Working on it",
      sections: [["chain", "The chain"], ["numbers", "Every paper number, its file"], ["explainer", "This guide's numbers"]] },
    { id: "changing", file: "changing.html", title: "Change something safely", group: "6 · Working on it",
      sections: [["rules", "The rules and why"], ["workload", "Add a workload"], ["campaign", "Add a campaign"], ["analysis", "Add an analysis"], ["hotpath", "Touching the measured code"]] },
    { id: "debugging", file: "debugging.html", title: "Debugging a run", group: "6 · Working on it",
      sections: [["status", "Start from make status"], ["records", "The run's records"], ["rerun", "Re-run one id by hand"], ["common", "The common failures"]] },
    { id: "workflow", file: "workflow.html", title: "The workflow: tickets, PRs, ADRs", group: "6 · Working on it",
      sections: [["ticket", "A ticket, a branch, a PR"], ["ci", "What CI checks"], ["review", "The bot review and the merge"], ["adr", "When a decision needs an ADR"], ["limits", "What is off limits"]] },
    { id: "code", file: "code.html", title: "How the code is organised", group: "7 · The code",
      sections: [["folders", "The folders"], ["bench", "bench/"], ["harness", "harness/"], ["analysis", "analysis/"], ["style", "Style rules and why"]] },
    { id: "trace", file: "trace.html", title: "One run, start to end", group: "7 · The code",
      sections: [["shape", "The shape before the steps"], ["native", "A native run"], ["browser", "A browser run"], ["analysis", "Into the analysis"]] },
    { id: "where", file: "where.html", title: "Where is…?", group: "7 · The code",
      sections: [["questions", "Where is it done?"], ["symptoms", "Something broke: where to look"]] },
    { id: "decisions", file: "decisions.html", title: "Decisions: the ADRs", group: "7 · The code",
      sections: [["how", "How decisions are kept"], ["changed", "Decisions that changed"], ["map", "The ADRs by topic"]] },
    { id: "lectures", file: "lectures.html", title: "Lecture map", group: "Appendix",
      sections: [["map", "Course concepts in the project"]] },
    { id: "glossary", file: "glossary.html", title: "Glossary", group: "Appendix", sections: [] }
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

  function initNav() {
    var nav = $("#nav");
    if (!nav) return;
    var seen = store("seen") || {};
    seen[current] = true;
    store("seen", seen);
    nav.innerHTML = "";
    var groups = {};
    PAGES.forEach(function (p) { (groups[p.group] = groups[p.group] || []).push(p); });
    Object.keys(groups).forEach(function (g) {
      nav.appendChild(el("h4", { text: g }));
      var ol = el("ol");
      groups[g].forEach(function (p) {
        var li = el("li", { class: seen[p.id] ? "seen" : "" });
        var a = el("a", { href: p.file }, [el("span", { class: "dot", "aria-hidden": "true" }), p.title]);
        if (p.id === current) a.setAttribute("aria-current", "page");
        li.appendChild(a);
        if (p.id === current) {
          var heads = $$("main h2[id]");
          if (heads.length) {
            var toc = el("ol", { class: "toc" });
            heads.forEach(function (h) {
              toc.appendChild(el("li", {}, [el("a", { href: "#" + h.id, "data-toc": h.id, text: h.textContent })]));
            });
            li.appendChild(toc);
          }
        }
        ol.appendChild(li);
      });
      nav.appendChild(ol);
    });
    var count = PAGES.filter(function (p) { return seen[p.id]; }).length;
    var prog = el("div", { class: "progress" }, [count + " of " + PAGES.length + " pages read", el("div", { class: "bar" }, [el("i")])]);
    nav.appendChild(prog);
    requestAnimationFrame(function () { $("i", prog).style.transform = "scaleX(" + (count / PAGES.length) + ")"; });

    var menu = $("#menu-btn");
    if (menu) menu.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menu.setAttribute("aria-expanded", String(open));
    });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) nav.classList.remove("open"); });

    // highlight the section being read
    if ("IntersectionObserver" in window) {
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          $$("[data-toc]").forEach(function (a) { a.classList.toggle("active", a.getAttribute("data-toc") === en.target.id); });
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      $$("main h2[id]").forEach(function (h) { obs.observe(h); });
    }
  }

  function initPager() {
    var pager = $("#pager");
    if (!pager) return;
    var i = PAGES.findIndex(function (p) { return p.id === current; });
    var prev = PAGES[i - 1], next = PAGES[i + 1];
    pager.appendChild(prev ? el("a", { href: prev.file, class: "prev" }, [el("small", { text: "← Previous" }), prev.title]) : el("span"));
    pager.appendChild(next ? el("a", { href: next.file, class: "next" }, [el("small", { text: "Next →" }), next.title]) : el("span"));
  }

  // --- search ---------------------------------------------------------------------------
  function searchIndex() {
    var items = [];
    PAGES.forEach(function (p) {
      items.push({ title: p.title, where: "Page", href: p.file, text: p.title });
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
          el("a", { href: "glossary.html#" + t.id, text: "Glossary →" })]);
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
    box.appendChild(el("header", {}, [el("span", { text: opts.title || "" }), repoLink(c.file, first)]));
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
    initOpener();
    initNav();
    initPager();
    initSearch();
    initCode();
    initSources();
    initTerms();
    if (typeof window.page === "function") window.page(window.UI);
    initSources(); // sources and terms added by the page's own widgets
    initTerms();
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") hide(); });
    // widgets that redraw (tabs, steppers) add new sources and terms later
    var main = $("main"), queued = false;
    if (main && "MutationObserver" in window) new MutationObserver(function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () { queued = false; initSources(main); initTerms(); });
    }).observe(main, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
