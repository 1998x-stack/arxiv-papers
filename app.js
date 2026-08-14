/* arxiv-digest — hero word cloud */
(function () {
  "use strict";

  var terms = [
    ["attention", 34], ["transformers", 30], ["retrieval", 26],
    ["embeddings", 30], ["datasets", 24], ["scope", 22], ["FM-Index", 20],
    ["abstract", 26], ["question", 22], ["ranking", 24], ["generative", 28],
    ["syllabus", 20], ["signature", 22], ["weekly", 18], ["papers", 30],
    ["arXiv", 30], ["model", 26], ["inbox", 22]
  ];

  var cloud = document.getElementById("cloud");
  if (!cloud) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function layout() {
    var r = cloud.getBoundingClientRect();
    var W = r.width, H = r.height;
    cloud.innerHTML = "";
    terms.forEach(function (t, i) {
      var word = document.createElement("span");
      word.className = "term";
      word.textContent = t[0];
      var size = t[1];

      // alternate some words as solid "tags" (light-on-ink) for depth
      if (i % 5 === 2) word.classList.add("tag");

      word.style.fontSize = size + "px";
      word.style.fontWeight = (i % 3 === 0) ? 600 : 400;
      word.style.left = (6 + Math.random() * (W * 0.72)) + "px";
      word.style.top = (4 + Math.random() * (H * 0.78)) + "px";
      word.style.opacity = 0;

      cloud.appendChild(word);

      var target = {
        x: parseFloat(word.style.left),
        y: parseFloat(word.style.top)
      };

      (function (el, baseX, baseY, amp, period, delay) {
        var start = null;
        function frame(ts) {
          if (!start) start = ts;
          var k = reduce ? 1 : Math.min((ts - start) / 900, 1);
          var ease = 1 - Math.pow(1 - k, 3);
          var driftX = amp * Math.sin((ts - start + delay) / period);
          var driftY = amp * Math.cos((ts - start + delay) / (period * 1.4));
          el.style.transform =
            "translate(" + (baseX * ease + driftX * ease) + "px," +
            (baseY * ease + driftY * ease) + "px)";
          el.style.opacity = ease;
          if (k < 1) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
      })(word, 0, 0, 6 + (i % 4) * 3, 2200 + (i % 5) * 700, i * 60);
    });
  }

  var rafId = null;
  function debouncedLayout() {
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(layout);
  }

  layout();
  window.addEventListener("resize", debouncedLayout);
})();