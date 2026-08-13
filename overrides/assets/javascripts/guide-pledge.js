(function () {
  'use strict';

  function init() {
    var btn = document.getElementById('guide-pledge-btn');
    if (!btn) return;

    var overlay = document.getElementById('guide-pledge-overlay');
    var result = document.getElementById('guide-pledge-result');
    var KEY = 'hias_guide_pledge_count';
    var count = parseInt(localStorage.getItem(KEY) || '0', 10) || 0;
    var closeTimer = null;

    function setCount(n) {
      var nodes = document.querySelectorAll('.guide-pledge-count');
      for (var i = 0; i < nodes.length; i++) {
        nodes[i].textContent = String(n);
      }
    }

    function hideOverlay() {
      if (!overlay || overlay.hidden) return;
      overlay.hidden = true;
      if (closeTimer) {
        clearTimeout(closeTimer);
        closeTimer = null;
      }
    }

    function showOverlay() {
      if (!overlay) return;
      overlay.hidden = false;
      overlay.focus();
      if (closeTimer) clearTimeout(closeTimer);
      closeTimer = setTimeout(hideOverlay, 3000);
    }

    setCount(count);

    if (overlay) {
      overlay.addEventListener('click', hideOverlay);
      overlay.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
          event.preventDefault();
          hideOverlay();
        }
      });
    }

    btn.addEventListener('click', function () {
      count += 1;
      localStorage.setItem(KEY, String(count));
      setCount(count);
      if (result) {
        result.innerHTML = '您是第 <b>' + count + '</b> 位宣誓者';
      }
      showOverlay();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  if (window.document$) {
    window.document$.subscribe(init);
  }
})();
