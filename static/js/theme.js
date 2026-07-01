// theme.js - handles dark/light mode toggle and persistence

document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('theme') || 'dark';
  
  if (savedTheme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }

  if (toggleBtn) {
    toggleBtn.textContent = savedTheme === 'light' ? 'Modo Escuro' : 'Modo Claro';
    toggleBtn.addEventListener('click', () => {
      const isLight = document.documentElement.getAttribute('data-theme') === 'light';
      const newTheme = isLight ? 'dark' : 'light';
      
      if (newTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
      
      localStorage.setItem('theme', newTheme);
      toggleBtn.textContent = newTheme === 'light' ? 'Modo Escuro' : 'Modo Claro';
    });
  }
});
