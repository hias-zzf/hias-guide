(function () {
  'use strict';

  var API_BASE = 'https://abacus.jasoncameron.dev';
  var NAMESPACE = 'hias-guide-pledge';
  var COUNT_KEY = 'hias_guide_pledge_shared_count';
  var DAY_KEY = 'hias_guide_pledge_shared_date';
  var TOTAL_KEY = 'total';
  var TOTAL_COUNT_KEY = 'hias_guide_pledge_shared_total';
  var attached = false;
  var count = 0;
  var total = 0;

  function init() {
    var btn = document.getElementById('guide-pledge-btn');
    if (!btn || attached) return;
    attached = true;

    var overlay = document.getElementById('guide-pledge-overlay');
    var result = document.getElementById('guide-pledge-result');
    var closeTimer = null;
    var pledging = false;

    count = parseInt(localStorage.getItem(COUNT_KEY) || '0', 10) || 0;
    total = parseInt(localStorage.getItem(TOTAL_COUNT_KEY) || '0', 10) || 0;

    function setCount(n) {
      count = n;
      var nodes = document.querySelectorAll('.guide-pledge-count');
      for (var i = 0; i < nodes.length; i++) {
        nodes[i].textContent = String(n);
      }
    }

    function setTotal(n) {
      total = n;
      var nodes = document.querySelectorAll('.guide-pledge-total');
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

    function todayString() {
      var formatter = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Shanghai',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
      return formatter.format(new Date());
    }

    function fetchValue(action, date) {
      return fetch(API_BASE + '/' + action + '/' + NAMESPACE + '/' + date, { cache: 'no-store' })
        .then(function (response) {
          if (!response.ok) {
            throw new Error('bad status');
          }
          return response.json();
        })
        .then(function (data) {
          var value = parseInt(data.value, 10);
          if (!isFinite(value)) {
            throw new Error('bad value');
          }
          return value;
        });
    }

    function loadSharedCount() {
      Promise.all([
        fetchValue('get', todayString()),
        fetchValue('get', TOTAL_KEY)
      ]).then(function (values) {
        localStorage.setItem(COUNT_KEY, String(values[0]));
        setCount(values[0]);
        localStorage.setItem(TOTAL_COUNT_KEY, String(values[1]));
        setTotal(values[1]);
      }).catch(function () {});
    }

    setCount(count);
    setTotal(total);
    loadSharedCount();

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
      if (pledging) return;
      var today = todayString();
      if (localStorage.getItem(DAY_KEY) === today) {
        if (result) {
          result.innerHTML = '你已展示你的决心，圣杭高会照耀你。';
        }
        showOverlay();
        return;
      }

      pledging = true;
      if (result) {
        result.innerHTML = '正在登记你的忠诚...';
      }
      fetchValue('hit', today).then(function (value) {
        localStorage.setItem(DAY_KEY, today);
        localStorage.setItem(COUNT_KEY, String(value));
        setCount(value);
        return fetchValue('hit', TOTAL_KEY);
      }).then(function (totalValue) {
        localStorage.setItem(TOTAL_COUNT_KEY, String(totalValue));
        setTotal(totalValue);
        if (result) {
          result.innerHTML = '您是今天第 <b>' + count + '</b> 位忠诚者，累计第 <b>' + totalValue + '</b> 位';
        }
        showOverlay();
      }).catch(function () {
        if (localStorage.getItem(DAY_KEY) === today && result) {
          result.innerHTML = '您是今天第 <b>' + count + '</b> 位忠诚者，累计数据暂未更新';
        } else if (result) {
          result.innerHTML = '网络连接失败，请稍后再试';
        }
        showOverlay();
      }).then(function () {
        pledging = false;
      });
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
