// theme.js - handles dark/light mode toggle and persistence

document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  if (toggleBtn) {
    toggleBtn.textContent = savedTheme === 'dark' ? 'Modo Claro' : 'Modo Escuro';
    toggleBtn.addEventListener('click', () => {
      const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      toggleBtn.textContent = newTheme === 'dark' ? 'Modo Claro' : 'Modo Escuro';
    });
  }
});
