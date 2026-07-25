(() => {
  const config = window.EnterpriseSharesWishlist || {};
  const guestStorageKey = config.storageKey || 'enterprise_shares_wishlist';
  const storageKey = config.customerId ? `${guestStorageKey}:${config.customerId}` : guestStorageKey;
  const state = {
    items: new Set(),
    initialized: false,
    syncing: false,
    syncPending: false
  };

  const normalizeHandles = (items) => {
    if (!Array.isArray(items)) return [];
    return [...new Set(items.filter((item) => typeof item === 'string' && /^[a-z0-9][a-z0-9-]*$/.test(item)).slice(0, 200))];
  };

  const readStorage = (key) => {
    try {
      return normalizeHandles(JSON.parse(localStorage.getItem(key) || '[]'));
    } catch (_) {
      return [];
    }
  };

  const readLocal = () => readStorage(storageKey);

  const clearGuestStorage = () => {
    if (!config.customerId || storageKey === guestStorageKey) return;
    try {
      localStorage.removeItem(guestStorageKey);
    } catch (_) {
      // Ignore storage failures in privacy modes.
    }
  };

  const writeLocal = () => {
    try {
      localStorage.setItem(storageKey, JSON.stringify([...state.items]));
    } catch (_) {
      // Ignore storage failures in privacy modes.
    }
  };

  const proxyRequest = async (method, body) => {
    if (!config.customerId || !config.syncEnabled || !config.proxyPath) return null;

    const options = {
      method,
      headers: {
        Accept: 'application/json'
      },
      credentials: 'same-origin'
    };

    if (body) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }

    const response = await fetch(config.proxyPath, options);
    if (!response.ok) throw new Error(`Wishlist sync failed: ${response.status}`);
    return response.json();
  };

  const saveRemote = async () => {
    if (!config.customerId || !config.syncEnabled) return;

    state.syncPending = true;
    if (state.syncing) return;

    state.syncing = true;
    try {
      while (state.syncPending) {
        state.syncPending = false;
        const snapshot = [...state.items];
        await proxyRequest('POST', { items: snapshot });
      }
    } catch (error) {
      console.warn('[Enterprise Shares] Wishlist sync failed.', error);
    } finally {
      state.syncing = false;
    }
  };

  const updateButtons = (root = document) => {
    root.querySelectorAll('[data-es-wishlist-button]').forEach((button) => {
      const handle = button.dataset.productHandle;
      const saved = state.items.has(handle);
      button.classList.toggle('is-saved', saved);
      button.setAttribute('aria-pressed', saved ? 'true' : 'false');
      button.setAttribute('aria-label', `${saved ? 'Remove' : 'Save'} ${handle.replace(/-/g, ' ')}`);
    });
  };

  const dispatchChange = () => {
    document.dispatchEvent(new CustomEvent('enterprise:wishlist:change', {
      detail: { items: [...state.items] }
    }));
  };

  const toggle = (handle) => {
    if (!handle) return;
    if (state.items.has(handle)) state.items.delete(handle);
    else state.items.add(handle);
    writeLocal();
    updateButtons(document);
    dispatchChange();
    saveRemote();
  };

  const bindButtons = (root = document) => {
    root.querySelectorAll('[data-es-wishlist-button]').forEach((button) => {
      if (button.dataset.esWishlistBound === 'true') return;
      button.dataset.esWishlistBound = 'true';
      button.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        toggle(button.dataset.productHandle);
      });
    });
    updateButtons(root);
  };

  const loadWishlistPage = async (root = document) => {
    const page = root.matches?.('[data-es-wishlist-page]') ? root : root.querySelector?.('[data-es-wishlist-page]');
    if (!page || page.dataset.esLoaded === 'true') return;
    page.dataset.esLoaded = 'true';

    const grid = page.querySelector('[data-es-wishlist-grid]');
    const empty = page.querySelector('[data-es-wishlist-empty]');
    const status = page.querySelector('[data-es-wishlist-status]');
    if (!grid || !empty || !status) return;

    const handles = [...state.items];
    if (!handles.length) {
      empty.hidden = false;
      status.textContent = '';
      return;
    }

    empty.hidden = true;
    status.textContent = `Loading ${handles.length} saved product${handles.length === 1 ? '' : 's'}…`;

    const rootPath = (config.routesRoot || '/').replace(/\/$/, '');
    const cards = await Promise.all(handles.map(async (handle) => {
      try {
        const response = await fetch(`${rootPath}/products/${encodeURIComponent(handle)}?view=es-card`, {
          headers: { Accept: 'text/html' }
        });
        if (!response.ok) return null;
        return response.text();
      } catch (_) {
        return null;
      }
    }));

    const validCards = cards.filter(Boolean);
    grid.innerHTML = validCards.join('');
    status.textContent = `${validCards.length} saved product${validCards.length === 1 ? '' : 's'}`;

    if (!validCards.length) {
      empty.hidden = false;
      status.textContent = '';
    }

    bindButtons(grid);
    window.EnterpriseSharesCards?.init(grid);
  };

  const syncInitial = async () => {
    const accountItems = readLocal();
    const guestItems = config.customerId ? readStorage(guestStorageKey) : [];
    state.items = new Set(normalizeHandles([...accountItems, ...guestItems]));

    if (config.customerId && config.syncEnabled) {
      try {
        const remote = await proxyRequest('GET');
        const merged = normalizeHandles([...(remote?.items || []), ...accountItems, ...guestItems]);
        state.items = new Set(merged);
        writeLocal();
        clearGuestStorage();
        await proxyRequest('POST', { items: merged });
      } catch (error) {
        console.warn('[Enterprise Shares] Wishlist account sync unavailable; using browser storage.', error);
      }
    }

    state.initialized = true;
    updateButtons(document);
    bindButtons(document);
    await loadWishlistPage(document);
    dispatchChange();
  };

  const init = (root = document) => {
    if (!config.enabled) return;
    bindButtons(root);
    if (state.initialized) loadWishlistPage(root);
  };

  Object.assign(config, {
    init,
    toggle,
    getItems: () => [...state.items]
  });
  window.EnterpriseSharesWishlist = config;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncInitial, { once: true });
  } else {
    syncInitial();
  }

  document.addEventListener('shopify:section:load', (event) => init(event.target));
  document.addEventListener('enterprise:wishlist:change', () => {
    const page = document.querySelector('[data-es-wishlist-page]');
    if (page) {
      page.dataset.esLoaded = 'false';
      const grid = page.querySelector('[data-es-wishlist-grid]');
      if (grid) grid.innerHTML = '';
      loadWishlistPage(page);
    }
  });
})();
