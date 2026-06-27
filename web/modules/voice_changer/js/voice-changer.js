/**
 * @file
 * Voice Changer control panel JS — Fetch + WebSocket to Python API.
 */

(function (Drupal, drupalSettings) {
  'use strict';

  Drupal.behaviors.voiceChanger = {
    attach(context, settings) {
      const panel = context.querySelector('#voice-changer-panel');
      if (!panel) return;
      if (panel.dataset.vcAttached) return;
      panel.dataset.vcAttached = '1';

      const apiBase = (settings.voiceChanger && settings.voiceChanger.apiBase)
        ? settings.voiceChanger.apiBase
        : 'http://localhost:8000';

      const indicator = panel.querySelector('#vc-indicator');
      const statusLabel = panel.querySelector('#vc-status-label');
      const bannerOffline = panel.querySelector('#vc-banner-offline');
      const bannerVbCable = panel.querySelector('#vc-banner-vbcable');

      // --- Device check on load ---
      fetch(`${apiBase}/devices`)
        .then(r => r.json())
        .then(data => {
          if (!data.vb_cable_detected) {
            bannerVbCable.hidden = false;
          }
        })
        .catch(() => {
          bannerOffline.hidden = false;
          statusLabel.textContent = Drupal.t('Python backend offline');
        });

      // --- WebSocket level monitor ---
      const wsUrl = apiBase.replace(/^http/, 'ws') + '/ws/level';
      let ws;

      function connectWs() {
        ws = new WebSocket(wsUrl);
        ws.onmessage = (evt) => {
          const data = JSON.parse(evt.data);
          const bar = panel.querySelector('#vc-level-bar');
          if (bar) bar.style.width = (data.level * 100).toFixed(1) + '%';
          if (data.is_running) {
            indicator.classList.add('vc-indicator--active');
            statusLabel.textContent = Drupal.t('Running');
            startBtn.disabled = false;
            startBtn.textContent = Drupal.t('Start Voice Changer');
          } else {
            indicator.classList.remove('vc-indicator--active');
            statusLabel.textContent = Drupal.t('Stopped');
          }
          updateStartStop(data.is_running);
        };
        ws.onerror = () => { bannerOffline.hidden = false; };
        ws.onclose = () => { setTimeout(connectWs, 3000); };
      }
      connectWs();

      // --- Start / Stop ---
      const startBtn = panel.querySelector('#vc-start');
      const stopBtn = panel.querySelector('#vc-stop');

      function updateStartStop(isRunning) {
        startBtn.hidden = isRunning;
        stopBtn.hidden = !isRunning;
      }

      startBtn.addEventListener('click', () => {
        startBtn.disabled = true;
        startBtn.textContent = Drupal.t('Starting...');
        fetch(`${apiBase}/start`, { method: 'POST' })
          .then(r => r.json())
          .then(data => { updateStartStop(data.is_running); })
          .catch(() => { startBtn.disabled = false; startBtn.textContent = Drupal.t('Start Voice Changer'); });
      });

      stopBtn.addEventListener('click', () => {
        fetch(`${apiBase}/stop`, { method: 'POST' })
          .then(r => r.json())
          .then(data => { updateStartStop(data.is_running); });
      });

      // Sync start/stop buttons with WebSocket state
      const origOnMessage = null;

      // --- Quality mode ---
      panel.querySelectorAll('.vc-btn--mode').forEach(btn => {
        btn.addEventListener('click', () => {
          fetch(`${apiBase}/quality-mode`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: btn.dataset.mode }),
          });
          panel.querySelectorAll('.vc-btn--mode').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
        });
      });

      // --- Quality mode params (pitch, formant) ---
      function sendModeParams() {
        const params = {};
        panel.querySelectorAll('.vc-mode-param').forEach(p => {
          params[p.dataset.param] = parseFloat(p.value);
        });
        fetch(`${apiBase}/quality-mode/params`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ params }),
        });
      }

      panel.querySelectorAll('.vc-mode-param').forEach(p => {
        const valEl = p.parentElement.querySelector('.vc-param-value');
        p.addEventListener('input', () => { if (valEl) valEl.textContent = p.value; });
        p.addEventListener('change', sendModeParams);
      });

      // --- Output mode ---
      panel.querySelectorAll('.vc-btn--output').forEach(btn => {
        btn.addEventListener('click', () => {
          fetch(`${apiBase}/output-mode`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: btn.dataset.mode }),
          });
          panel.querySelectorAll('.vc-btn--output').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
        });
      });

      // --- Passthrough ---
      let passthroughEnabled = false;
      const passthroughBtn = panel.querySelector('#vc-passthrough');
      passthroughBtn.addEventListener('click', () => {
        passthroughEnabled = !passthroughEnabled;
        fetch(`${apiBase}/passthrough`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled: passthroughEnabled }),
        });
        passthroughBtn.textContent = passthroughEnabled
          ? Drupal.t('Passthrough ON')
          : Drupal.t('Passthrough OFF');
        passthroughBtn.classList.toggle('active', passthroughEnabled);
      });

      // --- Effects ---
      panel.querySelectorAll('.vc-effect').forEach(effectEl => {
        const effectName = effectEl.dataset.effect;
        const toggle = effectEl.querySelector('.vc-effect-toggle');
        const params = effectEl.querySelectorAll('.vc-effect-param');

        function sendEffect() {
          const paramObj = {};
          params.forEach(p => { paramObj[p.dataset.param] = parseFloat(p.value); });
          fetch(`${apiBase}/effects/${effectName}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: toggle.checked, params: paramObj }),
          });
        }

        toggle.addEventListener('change', sendEffect);
        params.forEach(p => {
          p.addEventListener('input', () => {
            const display = p.parentElement.querySelector('.vc-param-value');
            if (display) display.textContent = p.value;
          });
          p.addEventListener('change', sendEffect);
        });
      });

      // --- Presets ---
      const presetSelect = panel.querySelector('#vc-preset-select');
      const presetNameInput = panel.querySelector('#vc-preset-name');

      panel.querySelector('#vc-preset-load').addEventListener('click', () => {
        const name = presetSelect.value;
        fetch(`${apiBase}/presets/${encodeURIComponent(name)}/load`, { method: 'POST' });
      });

      panel.querySelector('#vc-preset-save').addEventListener('click', () => {
        const name = presetNameInput.value.trim();
        if (!name) return;
        fetch(`${apiBase}/presets/${encodeURIComponent(name)}`, { method: 'POST' });
      });

      panel.querySelector('#vc-preset-export').addEventListener('click', () => {
        const name = presetSelect.value;
        window.location.href = `${apiBase}/presets/${encodeURIComponent(name)}/export`;
      });

      const importFileInput = panel.querySelector('#vc-preset-import-file');
      panel.querySelector('#vc-preset-import').addEventListener('click', () => {
        importFileInput.click();
      });
      importFileInput.addEventListener('change', () => {
        if (!importFileInput.files.length) return;
        const formData = new FormData();
        formData.append('file', importFileInput.files[0]);
        fetch(`${apiBase}/presets/import`, { method: 'POST', body: formData });
      });
    },
  };

})(Drupal, drupalSettings);
