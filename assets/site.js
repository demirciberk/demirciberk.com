const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- header rule once the page moves ---------- */
const header = document.getElementById('top');
const onScroll = () => header.classList.toggle('is-stuck', window.scrollY > 8);
onScroll();
window.addEventListener('scroll', onScroll, { passive: true });

/* ---------- reveals: text fades up; plates "print": black pass, then red slides into register ---------- */
document.querySelectorAll('[data-stagger]').forEach((group) => {
  Array.from(group.children).forEach((child, i) => { child.style.transitionDelay = Math.min(i, 5) * 80 + 'ms'; });
});
const targets = document.querySelectorAll('[data-reveal], .print');
if (reduceMotion || !('IntersectionObserver' in window)) {
  targets.forEach((el) => el.classList.add('is-in'));
} else {
  document.querySelectorAll('.print .r').forEach((r) => { r.style.transitionDelay = '250ms'; });
  const ro = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      ro.unobserve(e.target);
      // once printed, hover and pointer moves should respond without the entrance delay
      const r = e.target.querySelector('.print .r, .r');
      if (r) setTimeout(() => { r.style.transitionDelay = '0ms'; }, 1300);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });
  targets.forEach((el) => ro.observe(el));
}

/* ---------- hero: the pointer pulls the red pass out of register ---------- */
const hero = document.getElementById('hero');
if (hero && !reduceMotion && window.matchMedia('(pointer: fine)').matches) {
  let raf = 0;
  hero.addEventListener('pointermove', (ev) => {
    const b = hero.getBoundingClientRect();
    const x = (ev.clientX - b.left) / b.width - 0.5;
    const y = (ev.clientY - b.top) / b.height - 0.5;
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => {
      hero.style.setProperty('--rx', (x * 22).toFixed(1) + 'px');
      hero.style.setProperty('--ry', (y * 14).toFixed(1) + 'px');
    });
  });
  hero.addEventListener('pointerleave', () => { hero.style.setProperty('--rx', '0px'); hero.style.setProperty('--ry', '0px'); });
}

const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = String(new Date().getFullYear());
