(function () {
  var f = document.getElementById('va-calc'); if (!f) return;
  var $ = function (id) { return document.getElementById(id); };
  var money = function (n) { return '$' + Math.round(n).toLocaleString('en-US'); };
  var TAX = { chesapeake: 1.01, 'virginia-beach': 0.97, other: 1.00 };
  function val(id) { var v = parseFloat($(id).value); return isNaN(v) ? 0 : v; }
  function feeRate(downPct, use, exempt) {
    if (exempt) return 0;
    if (downPct >= 10) return 1.25;
    if (downPct >= 5) return 1.5;
    return use === 'subsequent' ? 3.3 : 2.15;
  }
  function calc() {
    var price = val('price'), downPct = val('down'), rate = val('rate'), years = val('term') || 30;
    var down = price * downPct / 100, base = Math.max(price - down, 0);
    var fr = feeRate(downPct, $('use').value, $('exempt').checked), fee = base * fr / 100;
    var financed = $('finance').checked, loan = financed ? base + fee : base;
    var n = years * 12, r = rate / 100 / 12;
    var pi = r === 0 ? loan / n : loan * r / (1 - Math.pow(1 + r, -n));
    var tax = price * val('taxrate') / 100 / 12, ins = val('ins') / 12, flood = val('flood') / 12, hoa = val('hoa');
    var total = pi + tax + ins + flood + hoa, bah = val('bah');
    var rows = [['Principal and interest', pi], ['Property tax (estimate)', tax], ['Homeowner’s insurance', ins], ['Flood insurance', flood], ['HOA or condo dues', hoa]];
    var h = '<div class="table-wrap"><table class="data-table"><caption>Estimated monthly payment</caption><tbody>';
    rows.forEach(function (x) { if (x[1] > 0) h += '<tr><th scope="row">' + x[0] + '</th><td class="num">' + money(x[1]) + '</td></tr>'; });
    h += '<tr><th scope="row"><strong>Total per month</strong></th><td class="num"><strong>' + money(total) + '</strong></td></tr></tbody></table></div>';
    h += '<div class="table-wrap"><table class="data-table"><caption>Loan and cash needed</caption><tbody>' +
      '<tr><th scope="row">Down payment</th><td class="num">' + money(down) + '</td></tr>' +
      '<tr><th scope="row">VA funding fee (' + fr + '%)</th><td class="num">' + money(fee) + (financed ? ' (added to loan)' : ' (paid at closing)') + '</td></tr>' +
      '<tr><th scope="row">Loan amount</th><td class="num">' + money(loan) + '</td></tr></tbody></table></div>';
    if (bah > 0) {
      var m = total / bah;
      h += '<p class="cmp-sentence">Your estimated payment is ' + m.toFixed(2) + 'x your BAH of ' + money(bah) + ' (' + (m <= 1 ? money(bah - total) + ' of BAH left over each month' : money(total - bah) + ' above BAH each month') + ').</p>';
    }
    $('va-out').innerHTML = h;
  }
  $('city').addEventListener('change', function () { $('taxrate').value = TAX[$('city').value]; calc(); });
  f.querySelectorAll('input,select').forEach(function (e) { e.addEventListener('input', calc); e.addEventListener('change', calc); });
  calc();
})();
