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
        { name: '复试人数', type: 'bar', data: d.fushi, barWidth: 24 },
        { name: '拟录取人数', type: 'bar', data: d.niqu, barWidth: 24 }
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
        { name: '02 方向', type: 'bar', data: d.s02, xAxisIndex: 0, yAxisIndex: 0, barWidth: 18 },
        { name: '03 方向', type: 'bar', data: d.s03, xAxisIndex: 0, yAxisIndex: 0, barWidth: 18 },
        { name: '02 方向', type: 'bar', data: [d.total02], xAxisIndex: 1, yAxisIndex: 1, barWidth: 30 },
        { name: '03 方向', type: 'bar', data: [d.total03], xAxisIndex: 1, yAxisIndex: 1, barWidth: 30 }
      ]
    };
  }

  function optionCombo(d, title) {
    return {
      title: { text: title, left: 'center', textStyle: { fontSize: 15 } },
      color: ['#4C72B0', '#DD8452', '#C0392B'],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['复试人数', '录取人数', '录取概率'], top: 32 },
      grid: { left: 55, right: 55, top: 72, bottom: 45 },
      xAxis: { type: 'category', data: d.buckets, name: '初试总分' },
      yAxis: [
        { type: 'value', name: '人数', min: 0 },
        { type: 'value', name: '录取概率', min: 0, max: 100, axisLabel: { formatter: '{value}%' } }
      ],
      series: [
        { name: '复试人数', type: 'bar', data: d.fushi, yAxisIndex: 0, barWidth: 14 },
        { name: '录取人数', type: 'bar', data: d.niqu, yAxisIndex: 0, barWidth: 14 },
        { name: '录取概率', type: 'line', data: d.prob, yAxisIndex: 1, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: { width: 2.5 } }
      ]
    };
  }

  function optionTrendScore(d) {
    return {
      title: { text: '历年分数线与拟录取平均分', left: 'center', textStyle: { fontSize: 15 } },
      color: ['#DD8452', '#4C72B0', '#FDB462', '#6BAED6'],
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['智能光电 复试线', '小卫星联培 复试线', '智能光电 拟录取平均分', '小卫星联培 拟录取平均分'],
        top: 32
      },
      grid: { left: 60, right: 30, top: 80, bottom: 45 },
      xAxis: { type: 'category', data: d.categories },
      yAxis: { type: 'value', name: '分数线', min: 300, max: 370, interval: 10 },
      series: [
        { name: '智能光电 复试线', type: 'line', data: d.znLine, smooth: true, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2.5 }, connectNulls: false },
        { name: '小卫星联培 复试线', type: 'line', data: d.wxLine, smooth: true, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2.5 }, connectNulls: false },
        { name: '智能光电 拟录取平均分', type: 'line', data: d.znAvg, smooth: true, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2, type: 'dashed' }, connectNulls: false },
        { name: '小卫星联培 拟录取平均分', type: 'line', data: d.wxAvg, smooth: true, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2, type: 'dashed' }, connectNulls: false }
      ]
    };
  }

  function optionTrendCount(d) {
    return {
      title: { text: '历年招生录取人数对比', left: 'center', textStyle: { fontSize: 15 } },
      color: ['#4C72B0', '#DD8452'],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['复试人数', '拟录取人数'], top: 32 },
      grid: { left: 60, right: 30, top: 70, bottom: 45 },
      xAxis: { type: 'category', data: d.categories },
      yAxis: { type: 'value', name: '人数', min: 0 },
      series: [
        { name: '复试人数', type: 'bar', data: d.fushi, barWidth: 24 },
        { name: '拟录取人数', type: 'bar', data: d.niqu, barWidth: 24 }
      ]
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
    var defs = [
      ['wlgd-admission', data.admission, null],
      ['wlgd-avg', data.avg, null],
      ['wlgd-02-combo', data.combo02, '02 方向初试总分分段统计'],
      ['wlgd-03-combo', data.combo03, '03 方向初试总分分段统计'],
      ['wlgd-25-combo', data.combo25, '02 方向初试总分分段统计（25 年）'],
      ['wlgd-trend-score', data.trendScore, null],
      ['wlgd-trend-count', data.trendCount, null]
    ];
    var allReady = true;
    for (var i = 0; i < defs.length; i++) {
      var id = defs[i][0];
      var d = defs[i][1];
      var title = defs[i][2];
      var el = document.getElementById(id);
      if (!el) continue;
      if (!d) { allReady = false; continue; }
      var option;
      if (id === 'wlgd-admission') { option = optionAdmission(d); }
      else if (id === 'wlgd-avg') { option = optionAvg(d); }
      else if (id === 'wlgd-trend-score') { option = optionTrendScore(d); }
      else if (id === 'wlgd-trend-count') { option = optionTrendCount(d); }
      else { option = optionCombo(d, title); }
      renderOne(id, option);
      if (!instances[id]) { allReady = false; }
    }
    return allReady;
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