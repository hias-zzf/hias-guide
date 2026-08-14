(function () {
  'use strict';

  var instances = {};

  function getData() {
    var el = document.getElementById('intel-charts-data');
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  function optionAdmission(d) {
    return {
      title: { text: 'AI 与 CS 复试 / 拟录取人数对比', left: 'center', textStyle: { fontSize: 15 } },
      color: ['#4C72B0', '#DD8452'],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['复试人数', '拟录取人数'], top: 32 },
      grid: { left: 55, right: 24, top: 72, bottom: 40 },
      xAxis: { type: 'category', data: d.categories },
      yAxis: { type: 'value', min: 0, interval: 10, name: '人数' },
      series: [
        { name: '复试人数', type: 'bar', data: d.fushi, barWidth: 30 },
        { name: '拟录取人数', type: 'bar', data: d.niqu, barWidth: 30 }
      ]
    };
  }

  function optionAvg(d) {
    return {
      title: { text: 'AI 与 CS 录取均分对比', left: 'center', textStyle: { fontSize: 15 } },
      color: ['#4C72B0', '#DD8452'],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['AI', 'CS'], top: 32 },
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
        { type: 'value', name: '总分', min: 360, max: 395, gridIndex: 1 }
      ],
      series: [
        { name: 'AI', type: 'bar', data: d.sAI, xAxisIndex: 0, yAxisIndex: 0, barWidth: 18 },
        { name: 'CS', type: 'bar', data: d.sCS, xAxisIndex: 0, yAxisIndex: 0, barWidth: 18 },
        { name: 'AI', type: 'bar', data: [d.totalAI], xAxisIndex: 1, yAxisIndex: 1, barWidth: 34 },
        { name: 'CS', type: 'bar', data: [d.totalCS], xAxisIndex: 1, yAxisIndex: 1, barWidth: 34 }
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

  function optionEmploymentSplit(d) {
    return {
      title: { text: '2024 届毕业去向占比', left: 'center', textStyle: { fontSize: 15 } },
      color: ['#4C72B0', '#DD8452'],
      tooltip: { trigger: 'item', formatter: '{b}<br/>{c} 人（{d}%）' },
      legend: { data: d.categories, bottom: 10 },
      series: [
        {
          name: '毕业去向',
          type: 'pie',
          radius: ['38%', '62%'],
          center: ['50%', '46%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { formatter: '{b}\n{c} 人' },
          data: d.categories.map(function (name, i) {
            return { name: name, value: d.values[i] };
          })
        }
      ]
    };
  }

  function optionEmploymentDest(d) {
    var items = d.companies.map(function (name, i) {
      return { name: name, value: d.counts[i] };
    }).sort(function (a, b) { return a.value - b.value; });
    return {
      title: { text: '2024 届就业单位分布', left: 'center', textStyle: { fontSize: 15 } },
      color: ['#4C72B0'],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>{c} 人' },
      grid: { left: 110, right: 30, top: 60, bottom: 30 },
      xAxis: { type: 'value', minInterval: 1, name: '人数' },
      yAxis: { type: 'category', data: items.map(function (x) { return x.name; }) },
      series: [
        {
          name: '人数',
          type: 'bar',
          data: items.map(function (x) { return x.value; }),
          barWidth: 16,
          itemStyle: { borderRadius: [0, 4, 4, 0] },
          label: { show: true, position: 'right', formatter: '{c} 人' }
        }
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
    if (data.admission && data.avg && data.comboAI && data.comboCS) {
      renderOne('intel-admission', optionAdmission(data.admission));
      renderOne('intel-avg', optionAvg(data.avg));
      renderOne('intel-ai-combo', optionCombo(data.comboAI, 'AI 初试总分分段统计'));
      renderOne('intel-cs-combo', optionCombo(data.comboCS, 'CS 初试总分分段统计'));
    }
    if (data.employment) {
      renderOne('intel-employment-split', optionEmploymentSplit(data.employment.split));
      renderOne('intel-employment-dest', optionEmploymentDest(data.employment.dest));
    }
    return !!(instances['intel-admission'] && instances['intel-avg'] && instances['intel-ai-combo'] && instances['intel-cs-combo']);
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
          if (n.id && n.id.indexOf('intel-') === 0) { scheduleRender(); return; }
          if (n.querySelector) {
            if (n.querySelector('#intel-charts-data') || n.querySelector('[id^="intel-"]')) {
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
