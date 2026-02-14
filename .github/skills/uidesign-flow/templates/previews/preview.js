(function () {
  function setTheme(next) {
    if (next === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    try { localStorage.setItem("uidesign_theme", next); } catch (_) {}
  }

  function getTheme() {
    try { return localStorage.getItem("uidesign_theme"); } catch (_) { return null; }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const saved = getTheme();
    if (saved === "dark") setTheme("dark");

    const btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.addEventListener("click", function () {
        const isDark = document.documentElement.getAttribute("data-theme") === "dark";
        setTheme(isDark ? "light" : "dark");
      });
    }
  });
})();
