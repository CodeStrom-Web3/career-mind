/* =========================================================
   projects.js — Projects page: show/hide add-project form
   and append a new memory card to the grid
   ========================================================= */

const addProjectForm = document.getElementById('addProjectForm');
const projectGrid = document.getElementById('projectGrid');

function openForm() {
  addProjectForm.style.display = '';
  addProjectForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
function closeForm() {
  addProjectForm.style.display = 'none';
  document.getElementById('projTitle').value = '';
  document.getElementById('projStack').value = '';
  document.getElementById('projDesc').value = '';
}

document.getElementById('addProjectBtn')?.addEventListener('click', openForm);
document.getElementById('emptyAddProjectBtn')?.addEventListener('click', openForm);
document.getElementById('cancelProjectBtn')?.addEventListener('click', closeForm);

document.getElementById('saveProjectBtn')?.addEventListener('click', () => {
  const title = document.getElementById('projTitle').value.trim();
  const stack = document.getElementById('projStack').value.trim();
  const desc = document.getElementById('projDesc').value.trim();
  if (!title) { showToast('Give your project a title first'); return; }

  const card = document.createElement('div');
  card.className = 'memory-card';
  card.innerHTML = `
    <span class="tag">${stack || 'Project'}</span>
    <h4>${title}</h4>
    <p>${desc || 'No description added.'}</p>
    <div class="meta">Just now</div>
  `;
  projectGrid.insertBefore(card, projectGrid.lastElementChild);

  closeForm();
  showToast('Project saved to memory');
});