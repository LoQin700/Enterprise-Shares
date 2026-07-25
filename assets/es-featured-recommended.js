(() => {
  const initSlider = (root) => {
    root.querySelectorAll('[data-es-slider]').forEach((slider) => {
      if (slider.dataset.esBound === 'true') return;
      slider.dataset.esBound = 'true';

      const slides = [...slider.querySelectorAll('[data-es-slide]')];
      const pages = [...slider.querySelectorAll('[data-es-page]')];
      const previous = slider.querySelector('[data-es-prev]');
      const next = slider.querySelector('[data-es-next]');
      let current = 0;

      const setPage = (index) => {
        current = Math.min(Math.max(index, 0), slides.length - 1);

        slides.forEach((slide, slideIndex) => {
          const active = slideIndex === current;
          slide.hidden = !active;
          slide.classList.toggle('is-active', active);
        });

        pages.forEach((page, pageIndex) => {
          const active = pageIndex === current;
          page.classList.toggle('is-active', active);
          page.setAttribute('aria-current', active ? 'page' : 'false');
        });

        if (previous) previous.disabled = current === 0;
        if (next) next.disabled = current === slides.length - 1;

        window.EnterpriseSharesCards?.init(slides[current] || slider);
        window.EnterpriseSharesWishlist?.init(slides[current] || slider);
      };

      pages.forEach((page) => {
        page.addEventListener('click', () => setPage(Number(page.dataset.esPage)));
      });
      previous?.addEventListener('click', () => setPage(current - 1));
      next?.addEventListener('click', () => setPage(current + 1));
      setPage(0);
    });
  };

  const init = (root = document) => initSlider(root);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init(document), { once: true });
  } else {
    init(document);
  }

  document.addEventListener('shopify:section:load', (event) => init(event.target));
})();
