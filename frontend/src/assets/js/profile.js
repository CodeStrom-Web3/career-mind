/* =========================================================
   profile.js — Career Profile page
   ========================================================= */

const saveGoalBtn = document.getElementById('saveGoalBtn');
if (saveGoalBtn) {
  saveGoalBtn.addEventListener('click', () => {
    const goal = document.getElementById('goalInput').value.trim();
    if (!goal) return;
    showToast(`Goal updated to "${goal}"`);
  });
}