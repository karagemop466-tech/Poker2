// Lightweight progressive enhancement: mark the current section in navigation.
const links = [...document.querySelectorAll('.side a')];
const targets = links.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) {
      links.forEach(link => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
    }
  }, { rootMargin: '-15% 0px -70% 0px' });
  targets.forEach(target => observer.observe(target));
}
