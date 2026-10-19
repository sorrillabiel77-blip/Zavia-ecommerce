(() => {
  const toggle = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('#nav-links');
  if (toggle && menu) toggle.addEventListener('click', () => menu.classList.toggle('is-open'));
  document.querySelectorAll('[data-thumb]').forEach(button => {
    button.addEventListener('click', () => {
      const main = document.querySelector('#mainProductPhoto');
      if (main) main.src = button.dataset.thumb;
    });
  });
})();
