/* ════════════════════════════════════════════
   Smart Warehouse — Main JS
   ════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar Toggle ──────────────────────────────────────────────
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar   = document.getElementById('sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      const isMobile = window.innerWidth <= 768;
      if (isMobile) {
        sidebar.classList.toggle('mobile-open');
      } else {
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
      }
    });

    // Restore sidebar state
    const collapsed = localStorage.getItem('sidebarCollapsed');
    if (collapsed === 'true' && window.innerWidth > 768) {
      sidebar.classList.add('collapsed');
    }

    // Close sidebar on mobile overlay click
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 768 &&
          sidebar.classList.contains('mobile-open') &&
          !sidebar.contains(e.target) &&
          e.target !== toggleBtn) {
        sidebar.classList.remove('mobile-open');
      }
    });
  }

  // ── Auto-dismiss alerts ─────────────────────────────────────────
  document.querySelectorAll('.alert.alert-success, .alert.alert-info').forEach(function (el) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 4000);
  });

  // ── Confirm delete prompts (data-confirm) ───────────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // ── Order number auto-generate ──────────────────────────────────
  const orderNumField = document.getElementById('id_order_number');
  if (orderNumField && !orderNumField.value) {
    const ts = Date.now().toString().slice(-8);
    orderNumField.value = 'ORD-' + ts;
  }

  // ── Datetime-local fields: default to now ───────────────────────
  document.querySelectorAll('input[type="datetime-local"]:not([value])').forEach(function (el) {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    el.defaultValue = now.toISOString().slice(0, 16);
  });

  // ── Table row clickable ─────────────────────────────────────────
  document.querySelectorAll('tr[data-href]').forEach(function (row) {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function () {
      window.location.href = row.dataset.href;
    });
  });

  // ── Tooltip init ────────────────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

});
