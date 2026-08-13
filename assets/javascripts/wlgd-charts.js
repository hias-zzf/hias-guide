(function () {
  'use strict';

  var instances = {};

  function getData() {
    var el = document.getElementById('wlgd-charts-data');
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  function optionAdmission(d) {
    return {
      title: { text: '02 与 03 复试 / 拟录取人数对比', left: 'center', textStyle: { fontSize: 15 } },
      color: ['#4C72B0', '#DD8452'],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['复试人数', '拟录取人数'], top: 32 },
      grid: { left: 55, right: 24, top: 72, bottom: 40 },
      xAxis: { type: 'category', data: d.categories },
      yAxis: { type: 'value', min: 0, max: 30, interval: 5, name: '人数' },
      series: [
        { name: '复试人数', type: 'bar', data: d.fushi, barWidth: 24, label: { show: true, position: 'top' } },
        { name: '拟录取人数', type: 'bar', data: d.niqu, barWidth: 24, label: { show: true, position: 'top' } }
      ]
    };
  }

  function optionAvg(d) {
    return {
      title: { text: '02 与 03 录取均分对比', left: 'center', textStyle: { fontSize: 15 } },
      color: ['#4C72B0', '#DD8452'],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['02 方向', '03 方向'], top: 32 },
      grid: [
        { left: 55, width: '46%', top: 72, bottom: 40 },
        { left: '58%', width: '34%', top: 72, bottom: 40 }
      ],
      xAxis: [
        { type: 'category', data: d.subjects, gridIndex: 0 },
        { type: 'category', data: ['总分'], gridIndex: 1 }
      ],
      yAxis: [
        { type: 'value', name: '均分', gridIndex: 0 },
        { type: 'value', name: '总分', min: 330, max: 370, gridIndex: 1 }
      ],
      series: [
        { name: '02 方向', type: 'bar', data: d.s02, xAxisIndex: 0, yAxisIndex: 0, barWidth: 18, label: { show: true, position: 'top' } },
        { name: '03 方向', type: 'bar', data: d.s03, xAxisIndex: 0, yAxisIndex: 0, barWidth: 18, label: { show: true, position: 'top' } },
        { name: '02 方向', type: 'bar', data: [d.total02], xAxisIndex: 1, yAxisIndex: 1, barWidth: 30, label: { show: true, position: 'top' } },
        { name: '03 方向', type: 'bar', data: [d.total03], xAxisIndex: 1, yAxisIndex: 1, barWidth: 30, label: { show: true, position: 'top' } }
      ]
    };
  }

  function optionCurve(scores, title, color) {
    return {
      title: { text: title, left: 'center', textStyle: { fontSize: 15 } },
      color: [color],
      tooltip: { trigger: 'axis' },
      grid: { left: 55, right: 24, top: 72, bottom: 40 },
      xAxis: { type: 'category', data: scores.map(function (_, i) { return i + 1; }), name: '拟录取名次（按总分降序）' },
      yAxis: { type: 'value', name: '总分', scale: true },
      series: [{
        name: '总分', type: 'line', data: scores, smooth: true,
        symbol: 'circle', symbolSize: 7, lineStyle: { width: 2 },
        label: { show: true, position: 'top' }
      }]
    };
  }

  function disposeAll() {
    for (var k in instances) {
      try { instances[k].dispose(); } catch (e) {}
      delete instances[k];
    }
  }

  function renderOne(id, option) {
    var el = document.getElementById(id);
    if (!el) return false;
    if (el.clientWidth === 0 || el.clientHeight === 0) return false;
    var old = instances[id];
    if (old && old.getDom && old.getDom() === el) return true;
    if (old) {
      try { old.dispose(); } catch (e) {}
    }
    try {
      var chart = echarts.init(el);
      chart.setOption(option);
      instances[id] = chart;
      return true;
    } catch (e) {
      return false;
    }
  }

  function renderAll() {
    var data = getData();
    if (!data) {
      disposeAll();
      return true;
    }
    renderOne('wlgd-admission', optionAdmission(data.admission));
    renderOne('wlgd-avg', optionAvg(data.avg));
    renderOne('wlgd-02-curve', optionCurve(data.s02, '02 方向拟录取总分曲线', '#4C72B0'));
    renderOne('wlgd-03-curve', optionCurve(data.s03, '03 方向拟录取总分曲线', '#DD8452'));
    return !!(instances['wlgd-admission'] && instances['wlgd-avg'] && instances['wlgd-02-curve'] && instances['wlgd-03-curve']);
  }

  var retryHandle = null;
  function scheduleRender() {
    if (retryHandle) return;
    var tries = 0;
    function tick() {
      retryHandle = null;
      var done = renderAll();
      if (done) return;
      tries++;
      if (tries >= 40) return;
      retryHandle = setTimeout(tick, 100);
    }
    retryHandle = setTimeout(tick, 0);
  }

  function startObserver() {
    if (!window.MutationObserver) return;
    var observer = new MutationObserver(function (mutations) {
      for (var i = 0; i < mutations.length; i++) {
        var added = mutations[i].addedNodes;
        for (var j = 0; j < added.length; j++) {
          var n = added[j];
          if (n.nodeType !== 1) continue;
          if (n.id && n.id.indexOf('wlgd-') === 0) { scheduleRender(); return; }
          if (n.querySelector) {
            if (n.querySelector('#wlgd-charts-data') || n.querySelector('[id^="wlgd-"]')) {
              scheduleRender();
              return;
            }
          }
        }
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  function init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', scheduleRender);
    } else {
      scheduleRender();
    }
    if (window.document$) {
      window.document$.subscribe(scheduleRender);
    }
    window.addEventListener('load', scheduleRender);
    startObserver();
    var rtimeout = null;
    window.addEventListener('resize', function () {
      if (rtimeout) clearTimeout(rtimeout);
      rtimeout = setTimeout(function () {
        for (var k in instances) {
          try { instances[k].resize(); } catch (e) {}
        }
      }, 120);
    });
  }

  init();
})();