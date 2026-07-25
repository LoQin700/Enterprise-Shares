(() => {
  const state = window.EnterpriseSharesCards || {
    countdownTimer: null
  };

  const getCountdownText = (deadline, endedText) => {
    const distance = deadline.getTime() - Date.now();
    if (!Number.isFinite(distance) || distance <= 0) return endedText || 'Ended';

    const minutes = Math.max(1, Math.ceil(distance / 60000));
    const days = Math.floor(minutes / 1440);
    const hours = Math.floor((minutes % 1440) / 60);

    if (days > 0) return `${days} day${days === 1 ? '' : 's'} left`;
    if (hours > 0) return `${hours} hour${hours === 1 ? '' : 's'} left`;
    return `${minutes} minute${minutes === 1 ? '' : 's'} left`;
  };

  const updateCountdowns = (root = document) => {
    root.querySelectorAll('[data-es-countdown]').forEach((element) => {
      const output = element.querySelector('[data-es-countdown-text]');
      const value = element.dataset.deadline;
      if (!output || !value) return;

      const deadline = new Date(value);
      output.textContent = getCountdownText(deadline, element.dataset.endedText);
      element.classList.toggle('is-ended', deadline.getTime() <= Date.now());
    });
  };

  const bindMedia = (root = document) => {
    root.querySelectorAll('[data-es-product-card]').forEach((card) => {
      if (card.dataset.esMediaBound === 'true') return;
      card.dataset.esMediaBound = 'true';

      const video = card.querySelector('video.es-card__video');
      if (!video) return;

      const play = () => {
        video.muted = true;
        const promise = video.play();
        if (promise && typeof promise.catch === 'function') promise.catch(() => {});
      };

      const stop = () => {
        video.pause();
        try {
          video.currentTime = 0;
        } catch (_) {
          // Ignore browsers that do not allow resetting before metadata loads.
        }
      };

      card.addEventListener('mouseenter', play);
      card.addEventListener('mouseleave', stop);
      card.addEventListener('focusin', play);
      card.addEventListener('focusout', (event) => {
        if (!card.contains(event.relatedTarget)) stop();
      });
    });
  };

  const init = (root = document) => {
    updateCountdowns(root);
    bindMedia(root);

    if (!state.countdownTimer) {
      state.countdownTimer = window.setInterval(() => updateCountdowns(document), 30000);
    }
  };

  state.init = init;
  state.updateCountdowns = updateCountdowns;
  window.EnterpriseSharesCards = state;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init(document), { once: true });
  } else {
    init(document);
  }

  document.addEventListener('shopify:section:load', (event) => init(event.target));
})();
