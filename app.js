/* =============================================================================
   app.js — 3ページ共通シェル
   -----------------------------------------------------------------------------
   ・ambient 背景と topbar(ブランド/ナビ/テーマ・明暗切替) を全ページに注入
   ・テーマ(studio/editorial/focus)と明暗(light/dark)を localStorage に永続化
   ・切替時に document へ 'ds:themechange' を発火 → 各ページが再描画に使える
   各ページは <body> に <div class="wrap"> … </div> を持つだけでよい。
   ========================================================================== */
(function () {
  "use strict";

  var THEMES = [
    { cls: "theme-studio", label: "Studio" },
    { cls: "theme-editorial", label: "Editorial" },
    { cls: "theme-focus", label: "Focus" },
  ];
  var NAV = [
    { href: "index.html", label: "スタイルガイド" },
    { href: "library.html", label: "ライブラリ" },
    { href: "proposals.html", label: "構成" },
    { href: "slides.html", label: "作成済み" },
  ];
  var LS_THEME = "ds.themeClass";
  var LS_MODE = "ds.mode";

  function read(key, fallback) {
    try { return localStorage.getItem(key) || fallback; } catch (e) { return fallback; }
  }
  function write(key, val) {
    try { localStorage.setItem(key, val); } catch (e) { /* プライベートモード等 */ }
  }

  // --- 永続値を読み出し、即適用 (フラッシュ最小化) ----------------------
  var themeClass = read(LS_THEME, "theme-studio");
  if (!THEMES.some(function (t) { return t.cls === themeClass; })) themeClass = "theme-studio";
  var mode = read(LS_MODE, "light");
  if (mode !== "light" && mode !== "dark") mode = "light";

  function applyTheme() {
    document.body.classList.remove("theme-studio", "theme-editorial", "theme-focus");
    document.body.classList.add(themeClass);
    document.documentElement.setAttribute("data-theme", mode);
  }

  function fire() {
    document.dispatchEvent(new CustomEvent("ds:themechange", {
      detail: { themeClass: themeClass, mode: mode },
    }));
  }

  // --- 現在ページ判定 ---------------------------------------------------
  function currentPage() {
    var path = location.pathname.split("/").pop() || "index.html";
    return path === "" ? "index.html" : path;
  }

  // --- DOM 構築 ---------------------------------------------------------
  function buildAmbient() {
    if (document.querySelector(".ambient")) return;
    var amb = document.createElement("div");
    amb.className = "ambient";
    amb.setAttribute("aria-hidden", "true");
    amb.innerHTML = '<span class="blob blob--1"></span><span class="blob blob--2"></span><span class="blob blob--3"></span>';
    document.body.insertBefore(amb, document.body.firstChild);
  }

  function buildTopbar() {
    var wrap = document.querySelector(".wrap");
    if (!wrap || wrap.querySelector(".topbar")) return;

    var page = currentPage();
    var navHTML = NAV.map(function (n) {
      var cur = n.href === page ? ' aria-current="page"' : "";
      return '<a href="' + n.href + '"' + cur + ">" + n.label + "</a>";
    }).join("");

    var themeHTML = THEMES.map(function (t) {
      var pressed = t.cls === themeClass ? "true" : "false";
      return '<button data-theme-class="' + t.cls + '" aria-pressed="' + pressed + '">' + t.label + "</button>";
    }).join("");

    var bar = document.createElement("div");
    bar.className = "topbar";
    bar.innerHTML =
      '<span class="brand">Design System</span>' +
      '<nav class="nav" aria-label="ページ">' + navHTML + "</nav>" +
      '<div class="seg" id="theme-seg" role="group" aria-label="アクセントテーマ">' + themeHTML + "</div>" +
      '<div class="seg" id="mode-seg" role="group" aria-label="明暗モード">' +
        '<button data-mode="light" aria-pressed="' + (mode === "light") + '">Light</button>' +
        '<button data-mode="dark" aria-pressed="' + (mode === "dark") + '">Dark</button>' +
      "</div>";
    wrap.insertBefore(bar, wrap.firstChild);

    bar.querySelector("#theme-seg").addEventListener("click", function (e) {
      var btn = e.target.closest("button"); if (!btn) return;
      themeClass = btn.dataset.themeClass;
      write(LS_THEME, themeClass);
      applyTheme();
      [].forEach.call(this.children, function (b) { b.setAttribute("aria-pressed", b === btn); });
      fire();
    });
    bar.querySelector("#mode-seg").addEventListener("click", function (e) {
      var btn = e.target.closest("button"); if (!btn) return;
      mode = btn.dataset.mode;
      write(LS_MODE, mode);
      applyTheme();
      [].forEach.call(this.children, function (b) { b.setAttribute("aria-pressed", b === btn); });
      fire();
    });
  }

  function init() {
    applyTheme();
    buildAmbient();
    buildTopbar();
    fire(); // 初期状態を各ページへ通知
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
