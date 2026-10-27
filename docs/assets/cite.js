(function () {
  var btn = document.querySelector("[data-copy]");
  if (!btn) return;
  var src = document.getElementById(btn.getAttribute("data-copy"));
  if (!src || !navigator.clipboard) { btn.hidden = true; return; }
  btn.addEventListener("click", function () {
    navigator.clipboard.writeText(src.innerText.trim()).then(function () {
      var was = btn.textContent;
      btn.textContent = "Copied";
      setTimeout(function () { btn.textContent = was; }, 1600);
    }).catch(function () {
      btn.textContent = "Press Ctrl+C";
    });
  });
})();
