/* =========================================================
   memory-center.js — search + filter over memory cards
   ========================================================= */

const memorySearch = document.getElementById('memorySearch');
const memoryGrid = document.getElementById('memoryContainer') || document.getElementById('memoryGrid');
const noResults = document.getElementById('noResults');
const filterTabs = document.querySelectorAll('.tab[data-filter]');

let activeFilter = 'all';

function applyFilters() {
  const query = (memorySearch?.value || '').trim().toLowerCase();
  let visibleCount = 0;

  if (!memoryGrid) return;

  memoryGrid.querySelectorAll('.memory-card').forEach((card) => {
    const category = (card.querySelector('.memory-category')?.textContent || card.getAttribute('data-type') || '').toLowerCase();
    const title = (card.querySelector('.memory-title')?.textContent || '').toLowerCase();
    const content = (card.querySelector('.memory-card-content')?.textContent || card.getAttribute('data-text') || '').toLowerCase();
    const fullText = `${category} ${title} ${content}`;

    const matchesFilter = activeFilter === 'all' || category.includes(activeFilter) || fullText.includes(activeFilter);
    const matchesSearch = !query || fullText.includes(query);
    const show = matchesFilter && matchesSearch;

    card.style.display = show ? '' : 'none';
    if (show) visibleCount++;
  });

  if (noResults) noResults.style.display = visibleCount === 0 ? '' : 'none';
}

if (memorySearch) memorySearch.addEventListener('input', applyFilters);

filterTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    filterTabs.forEach((t) => t.classList.remove('active'));
    tab.classList.add('active');
    activeFilter = tab.getAttribute('data-filter');
    applyFilters();
  });
});