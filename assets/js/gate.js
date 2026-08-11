/* Кодовое слово для доступа к лабораторной работе.
   ВНИМАНИЕ: это клиентская «шторка» для организации занятия, а не защита
   данных — на статическом сайте файлы доступны по прямым ссылкам.
   Настоящее ограничение доступа ставится в е-курсе (Moodle).

   Как поменять пароль: откройте консоль браузера (F12) на любой странице
   сайта и выполните
       gateHash('новое слово')
   — получите хэш и вставьте его в таблицу HASHES ниже.
   Слово не чувствительно к регистру и пробелам по краям. */
(function () {
  'use strict';

  var HASHES = {
    lab01: 'b8e020dd46021780c8e5fcd790c04c4006eb0ff030878b09581daff9b202d70a',
    lab02: '347b901ee4945bed1723587496683e80f1234ccb22a57bd28c142ffb85cc16f0',
    lab03: '1add6914912c98c27d12198239b617fe2672bc09a8f03729f3c29aef3ab008d7',
    lab04: 'f968a233e6f75ee05868ef3e8d2584fe1ae9a60f0a8f8bdd6e552a3f71d74621',
    lab05: '471ac60e5da0a568184e623bc08ca47c78878937cfea3b6aa0994a8a910e6534',
    lab06: 'd80d7d8f7b59659af47b0edfc7c774f46982202221859b44cd8c29e1a786d1fa'
  };

  function sha256hex(text) {
    var data = new TextEncoder().encode(text);
    return crypto.subtle.digest('SHA-256', data).then(function (buf) {
      return Array.from(new Uint8Array(buf))
        .map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
    });
  }

  /* хелпер для преподавателя */
  window.gateHash = function (word) {
    sha256hex(word.trim().toLowerCase()).then(function (h) {
      console.log('Хэш для «' + word + '»:\n' + h);
    });
    return 'считаю…';
  };

  var gate = document.querySelector('[data-gate]');
  if (!gate) return;
  var labId = gate.getAttribute('data-gate');
  var gated = document.querySelector('.gated');
  var input = gate.querySelector('input');
  var btn = gate.querySelector('button');
  var msg = gate.querySelector('.gate-msg');

  function unlock() {
    gate.hidden = true;
    if (gated) gated.hidden = false;
  }

  if (sessionStorage.getItem('unlocked-' + labId) === '1') { unlock(); return; }

  function tryWord() {
    var word = (input.value || '').trim().toLowerCase();
    if (!word) { msg.textContent = 'Введите кодовое слово.'; return; }
    if (!window.crypto || !crypto.subtle) {
      msg.textContent = 'Браузер не поддерживает проверку — откройте сайт по HTTPS.';
      return;
    }
    sha256hex(word).then(function (h) {
      if (h === HASHES[labId]) {
        sessionStorage.setItem('unlocked-' + labId, '1');
        unlock();
      } else {
        msg.textContent = 'Неверное кодовое слово. Его выдаёт преподаватель на занятии.';
        input.select();
      }
    });
  }
  btn.addEventListener('click', tryWord);
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter') tryWord(); });
})();
