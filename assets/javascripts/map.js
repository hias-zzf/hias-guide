(function () {
  'use strict';

  var maps = [];

  function pinIcon() {
    return L.divIcon({
      className: 'techphys-pin',
      html: '<div style="width:16px;height:16px;border-radius:50%;background:#174A94;border:3px solid #ffffff;box-shadow:0 1px 3px rgba(0,0,0,0.4)"></div>',
      iconSize: [16, 16],
      iconAnchor: [8, 8]
    });
  }

  function disposeAll() {
    for (var i = 0; i < maps.length; i++) {
      try { maps[i].remove(); } catch (e) {}
    }
    maps = [];
  }

  function initAll() {
    disposeAll();
    if (typeof L === 'undefined') return;
    var els = document.querySelectorAll('.techphys-map');
    for (var i = 0; i < els.length; i++) {
      (function (el) {
        var lat = parseFloat(el.getAttribute('data-lat'));
        var lon = parseFloat(el.getAttribute('data-lon'));
        var name = el.getAttribute('data-name') || '';
        var addr = el.getAttribute('data-addr') || '';
        if (isNaN(lat) || isNaN(lon)) return;
        var map = L.map(el, { center: [lat, lon], zoom: 16, scrollWheelZoom: false });
        L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
          subdomains: ['1', '2', '3', '4'],
          maxZoom: 19,
          attribution: '&copy; 高德地图'
        }).addTo(map);
        L.marker([lat, lon], { icon: pinIcon() })
          .addTo(map)
          .bindPopup('<b>' + name + '</b><br>' + addr)
          .openPopup();
        maps.push(map);
      })(els[i]);
    }
  }

  function run() {
    initAll();
  }

  function schedule() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', run);
    } else {
      run();
    }
    if (window.document$) {
      window.document$.subscribe(function () { setTimeout(run, 0); });
    }
    window.addEventListener('load', run);
  }

  schedule();
})();