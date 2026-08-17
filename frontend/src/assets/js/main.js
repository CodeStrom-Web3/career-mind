/* =========================================================
   main.js — shared helpers used across every page
   (toast messages, generic tab switching)
   ========================================================= */

// simple toast helper — call showToast("Saved!")
function showToast(message, duration = 2200) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
}

// generic tabs: any element with .tabs > .tab[data-tab] paired with #tab-<name>
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tabs').forEach((tabGroup) => {
    const tabs = tabGroup.querySelectorAll('.tab[data-tab]');
    if (!tabs.length) return;
    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        tabs.forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        const target = tab.getAttribute('data-tab');
        document.querySelectorAll('.tab-panel').forEach((panel) => {
          panel.style.display = panel.id === `tab-${target}` ? '' : 'none';
        });
        if (target === 'progress' && typeof updateProgressBars === 'function') {
          setTimeout(updateProgressBars, 50);
        }
        if (target === 'skills' && typeof renderSkills === 'function') {
          setTimeout(renderSkills, 50);
        }
      });
    });
  });
});