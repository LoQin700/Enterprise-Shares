(() => {
  const normalize = (value) => String(value || '').trim().toLowerCase();

  const uniqueLinks = (root) => {
    const seen = new Set();
    const links = [];
    root.querySelectorAll('a[href]').forEach((anchor) => {
      const title = anchor.textContent.trim();
      const href = anchor.getAttribute('href');
      if (!title || !href) return;
      const key = `${title}|${href}`;
      if (seen.has(key)) return;
      seen.add(key);
      links.push({ title, href });
    });
    return links;
  };

  const enhanceMenu = (menu) => {
    if (!menu || menu.dataset.esEnhanced === 'true') return;
    const configs = [...menu.querySelectorAll('.es-mega-config')];
    const items = [...menu.querySelectorAll('.menu-list__list-item:not([slot="overflow"])')];

    items.forEach((item, index) => {
      const trigger = item.querySelector(':scope > .menu-list__link');
      const submenu = item.querySelector(':scope > .menu-list__submenu');
      const grid = submenu?.querySelector('.mega-menu__grid');
      if (!trigger || !submenu || !grid) return;

      const title = trigger.textContent.trim();
      const href = trigger.getAttribute('href') || '#';
      const config = configs.find((node) => normalize(node.dataset.esMegaTitle) === normalize(title)) || configs[index];
      const links = uniqueLinks(grid).filter((link) => normalize(link.title) !== normalize(title));

      const layout = document.createElement('div');
      layout.className = 'es-mega-layout';

      const categories = document.createElement('div');
      categories.className = 'es-mega-categories';

      const titleLink = document.createElement('a');
      titleLink.className = 'es-mega-categories__title';
      titleLink.href = href;
      titleLink.innerHTML = `<span>${title}</span><span aria-hidden="true">›</span>`;
      categories.appendChild(titleLink);

      const linksGrid = document.createElement('div');
      linksGrid.className = 'es-mega-categories__links';
      links.slice(0, 18).forEach((link) => {
        const anchor = document.createElement('a');
        anchor.href = link.href;
        anchor.textContent = link.title;
        linksGrid.appendChild(anchor);
      });
      categories.appendChild(linksGrid);
      layout.appendChild(categories);

      const template = config?.querySelector('template[data-es-mega-template]');
      if (template?.content?.childNodes?.length) {
        layout.appendChild(template.content.cloneNode(true));
      }

      grid.replaceChildren(layout);
    });

    menu.dataset.esEnhanced = 'true';
    window.EnterpriseSharesCards?.init(menu);
    window.EnterpriseSharesWishlist?.init(menu);
  };

  const init = (scope = document) => {
    const menus = scope.matches?.('header-menu') ? [scope] : [...scope.querySelectorAll?.('header-menu') || []];
    menus.forEach(enhanceMenu);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init(), { once: true });
  } else {
    init();
  }

  document.addEventListener('shopify:section:load', (event) => init(event.target));
})();
