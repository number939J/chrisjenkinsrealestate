/* Lead-action tracking for Google Analytics 4. Sends events only if gtag is present. */
(function () {
  function send(name, params) { try { if (window.gtag) window.gtag('event', name, params || {}); } catch (e) {} }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var where = location.pathname;
    if (a.classList.contains('talk-float')) send('click_talk_to_chris', { link_location: 'floating_button', page_path: where });
    else if (href.indexOf('/talk-to-chris') === 0) send('click_talk_to_chris', { link_location: 'link', page_path: where });
    else if (href.indexOf('tel:') === 0) send('click_phone', { link_location: where });
    else if (href.indexOf('mailto:') === 0) send('click_email', { link_location: where });
  }, true);
})();
