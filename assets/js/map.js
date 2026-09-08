/* ============================================================
   ROUTE MAP — Leaflet over vendored OpenStreetMap tiles.
   Depends on data.js and on assets/vendor/leaflet-1.9.4.

   Leaflet itself is vendored, not pulled from a CDN, so the page
   works with no network. The TILES still need one, which is why
   the illustrated SVG above is the primary artefact and this is
   only an enhancement -- and why a tile failure reveals a notice
   rather than leaving a blank grey box.
   ============================================================ */
(function () {
  'use strict';

  if (typeof L === 'undefined' || !document.getElementById('map')) { return; }

  var STOPS = [
    { n: 1, lat: TRIP.origin.lat,      lon: TRIP.origin.lon,      label: 'Knoxville — depart 8:30 AM' },
    { n: 2, lat: COURSES.maggie.lat,   lon: COURSES.maggie.lon,   label: 'Maggie Valley Club — 12:10 PM' },
    { n: 3, lat: LODGING.lat,          lon: LODGING.lon,          label: 'The chalet — Summit Drive' },
    { n: 4, lat: COURSES.sequoyah.lat, lon: COURSES.sequoyah.lon, label: 'Sequoyah National — 2:30 PM' }
  ];

  var map = L.map('map', { scrollWheelZoom: false });

  var osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 17,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  });
  var topo = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    maxZoom: 16,
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
                 'contributors, SRTM | Tiles &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)'
  });
  topo.addTo(map);
  L.control.layers({ 'Topographic': topo, 'Standard': osm }, null, { position: 'topright' }).addTo(map);

  // If tiles cannot load, say so instead of showing an empty box.
  var failed = 0;
  function onTileError() {
    if (++failed < 4) { return; }
    var el = document.querySelector('.map__fallback');
    if (el) { el.classList.add('is-shown'); }
  }
  topo.on('tileerror', onTileError);
  osm.on('tileerror', onTileError);

  var legs = [
    { key: 'knox_mvc',     color: '#006747', weight: 4, dash: null  },
    { key: 'mvc_chalet',   color: '#006747', weight: 3, dash: '4 5' },
    { key: 'chalet_seq',   color: '#1E7A55', weight: 4, dash: null  },
    { key: 'seq_knox_441', color: '#C6A664', weight: 3, dash: '8 7' }
  ];

  var all = [];
  legs.forEach(function (l) {
    var leg = ROUTE[l.key];
    if (!leg) { return; }
    L.polyline(leg.geom, {
      color: l.color, weight: l.weight, opacity: 0.9,
      dashArray: l.dash, lineJoin: 'round'
    }).addTo(map).bindPopup(leg.from + ' &rarr; ' + leg.to + '<br>' +
      leg.miles + ' mi &middot; ' + leg.minutes + ' min');
    all = all.concat(leg.geom);
  });

  STOPS.forEach(function (s) {
    L.marker([s.lat, s.lon], {
      icon: L.divIcon({
        className: '',
        html: '<div class="map-pin">' + s.n + '</div>',
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      }),
      title: s.label
    }).addTo(map).bindPopup(s.label);
  });

  map.fitBounds(L.latLngBounds(all), { padding: [28, 28] });
})();
