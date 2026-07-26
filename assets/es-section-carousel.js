(() => {
  const instances = new WeakMap();

  class ESResponsiveCarousel {
    constructor(root) {
      this.root = root;
      this.viewport = root.querySelector('[data-es-carousel-viewport]');
      this.track = root.querySelector('[data-es-carousel-track]');
      this.items = [...root.querySelectorAll('[data-es-carousel-item]')];
      this.prev = root.querySelector('[data-es-carousel-prev]');
      this.next = root.querySelector('[data-es-carousel-next]');
      this.page = 0;
      this.resizeTimer = null;
      this.bind();
      this.update();
    }

    isMobile() {
      return window.matchMedia('(max-width: 749px)').matches;
    }

    isMobileGrid() {
      return this.isMobile() && this.root.dataset.mobileLayout === 'grid';
    }

    columns() {
      const value = this.isMobile()
        ? Number(this.root.dataset.mobileColumns || 2)
        : Number(this.root.dataset.desktopColumns || 3);
      return Math.max(1, value || 1);
    }

    pageCount() {
      return Math.max(1, Math.ceil(this.items.length / this.columns()));
    }

    bind() {
      this.prev?.addEventListener('click', () => this.go(this.page - 1));
      this.next?.addEventListener('click', () => this.go(this.page + 1));
      window.addEventListener('resize', () => {
        window.clearTimeout(this.resizeTimer);
        this.resizeTimer = window.setTimeout(() => this.update(), 100);
      });
    }

    go(nextPage) {
      const max = this.pageCount() - 1;
      this.page = Math.min(Math.max(0, nextPage), max);
      this.render();
    }

    update() {
      this.root.classList.toggle('is-mobile-grid', this.isMobileGrid());
      this.page = Math.min(this.page, this.pageCount() - 1);
      this.render();
    }

    render() {
      const pages = this.pageCount();
      const gridMode = this.isMobileGrid();
      if (this.track) {
        this.track.style.transform = gridMode ? '' : `translate3d(${-this.page * 100}%, 0, 0)`;
      }
      if (this.prev) {
        this.prev.disabled = this.page <= 0;
        this.prev.hidden = gridMode || pages <= 1;
      }
      if (this.next) {
        this.next.disabled = this.page >= pages - 1;
        this.next.hidden = gridMode || pages <= 1;
      }
      this.root.dataset.page = String(this.page + 1);
      this.root.dataset.pages = String(pages);
    }
  }

  const init = (scope = document) => {
    const roots = scope.matches?.('[data-es-responsive-carousel]')
      ? [scope]
      : [...scope.querySelectorAll?.('[data-es-responsive-carousel]') || []];
    roots.forEach((root) => {
      if (!instances.has(root)) instances.set(root, new ESResponsiveCarousel(root));
      else instances.get(root).update();
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init(), { once: true });
  } else {
    init();
  }

  document.addEventListener('shopify:section:load', (event) => init(event.target));
  window.EnterpriseSharesCarousel = { init };
})();
