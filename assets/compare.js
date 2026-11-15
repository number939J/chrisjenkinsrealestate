(function () {
  var root = document.getElementById('compare-tool');
  if (!root) return;
  var money = function (n) { return '$' + Math.round(n).toLocaleString('en-US'); };
  var num = function (n) { return Math.round(n).toLocaleString('en-US'); };
  fetch('/assets/neighborhood-stats.json').then(function (r) { return r.json(); }).then(function (data) {
    var H = data.hoods, names = data.city_names;
    var byKey = {}; H.forEach(function (h) { byKey[h.c + '/' + h.s] = h; });
    var embed = root.getAttribute('data-embed') === '1';
    function opts(sel, pick) {
      ['chesapeake', 'virginia-beach'].forEach(function (c) {
        var g = document.createElement('optgroup'); g.label = names[c] + ', VA';
        H.filter(function (h) { return h.c === c; }).sort(function (a, b) { return a.n.localeCompare(b.n); }).forEach(function (h) {
          var o = document.createElement('option'); o.value = h.c + '/' + h.s; o.textContent = h.n; if (h.c + '/' + h.s === pick) o.selected = true; g.appendChild(o);
        }); sel.appendChild(g);
      });
    }
    var a = root.querySelector('#cmp-a'), b = root.querySelector('#cmp-b'), out = root.querySelector('#cmp-out');
    var qs = new URLSearchParams(location.search);
    opts(a, qs.get('a') || 'chesapeake/south-norfolk'); opts(b, qs.get('b') || 'virginia-beach/ashville-park');
    function mult(x, y) { if (!x || !y) return ''; var r = y / x; return (r >= 1 ? r.toFixed(1) + 'x' : (1 / r).toFixed(1) + 'x lower'); }
    function row(label, A, B, fmt, withMult) {
      if (A == null || B == null) return '';
      return '<tr><th scope="row">' + label + '</th><td class="num">' + fmt(A) + '</td><td class="num">' + fmt(B) + '</td><td class="num">' + (withMult ? mult(A, B) : '') + '</td></tr>';
    }
    function link(h) { return '<a href="' + (embed ? 'https://chrisjenkinsrealestate.com' : '') + '/neighborhoods/' + h.c + '/' + h.s + '/"' + (embed ? ' target="_blank" rel="noopener"' : '') + '>' + h.n + '</a>'; }
    function render() {
      var A = byKey[a.value], B = byKey[b.value];
      var diff = B.m / A.m, sentence;
      if (A === B) sentence = 'Pick two different neighborhoods to compare.';
      else sentence = B.n + ' had a median sold price of ' + money(B.m) + ', which is ' + (diff >= 1 ? diff.toFixed(1) + 'x' : (1 / diff).toFixed(1) + 'x lower than') + (diff >= 1 ? ' the ' : ' ') + A.n + ' median of ' + money(A.m) + '.';
      out.innerHTML = '<p class="cmp-sentence">' + sentence + '</p>' +
        '<div class="table-wrap"><table class="data-table"><caption>' + A.n + ' and ' + B.n + ' compared, ' + data.window + '</caption><thead><tr><th scope="col">Measure</th><th scope="col" class="num">' + link(A) + '</th><th scope="col" class="num">' + link(B) + '</th><th scope="col" class="num">' + B.n + ' vs ' + A.n + '</th></tr></thead><tbody>' +
        row('Closed sales', A.k, B.k, num, false) + row('Median sold price', A.m, B.m, money, true) +
        '<tr><th scope="row">Middle half of sales</th><td class="num">' + money(A.a) + ' – ' + money(A.b) + '</td><td class="num">' + money(B.a) + ' – ' + money(B.b) + '</td><td></td></tr>' +
        row('Median price per sq ft', A.p, B.p, money, true) + row('Median days on market', A.d, B.d, num, true) +
        row('Median home size (sq ft)', A.f, B.f, num, true) + row('Median year built', A.y, B.y, function (v) { return v; }, false) +
        row('Median sale-to-list ratio', A.r, B.r, function (v) { return v.toFixed(1) + '%'; }, false) +
        (A.z && B.z ? '<tr><th scope="row">Most common ZIP code</th><td class="num">' + A.z + '</td><td class="num">' + B.z + '</td><td></td></tr>' : '') +
        '</tbody></table></div><p class="cmp-note">Source: REIN MLS closed residential sales, ' + data.window + '. Medians of past sales, not an appraisal.' + (embed ? ' Tool by <a href="https://chrisjenkinsrealestate.com/tools/neighborhood-compare/" target="_blank" rel="noopener">Chris Jenkins, Better Homes and Gardens Real Estate – Native American Group</a>.' : '') + '</p>';
      if (!embed && history.replaceState) history.replaceState(null, '', '?a=' + a.value + '&b=' + b.value);
    }
    a.addEventListener('change', render); b.addEventListener('change', render); render();
  }).catch(function () { root.querySelector('#cmp-out').textContent = 'The comparison could not load. Please see the table below.'; });
})();
