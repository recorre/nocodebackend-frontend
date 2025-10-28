// Indie Comments Widget - Hydration Script
// Enhances SSR widget with AJAX functionality

(function() {
  'use strict';

  // Utility function to find widgets on page
  function findWidgets() {
    return document.querySelectorAll('[data-widget-form]');
  }

  // Enhanced form submission with AJAX
  function enhanceForm(form) {
    const threadId = form.querySelector('input[name="thread_id"]').value;
    const announcer = document.getElementById(`ic-announcer-${threadId}`) ||
                     document.querySelector('[role="status"][aria-live="polite"]');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(form);
      const submitBtn = form.querySelector('button[type="submit"]');

      // Disable button and show loading
      submitBtn.disabled = true;
      submitBtn.textContent = 'Enviando...';

      if (announcer) {
        announcer.textContent = 'Enviando comentário...';
      }

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(Object.fromEntries(formData))
        });

        if (response.ok) {
          form.reset();
          submitBtn.textContent = 'Enviar Comentário';
          submitBtn.disabled = false;

          if (announcer) {
            announcer.textContent = 'Comentário enviado com sucesso! Aguardando moderação.';
          }

          // Optional: reload comments after delay
          setTimeout(() => {
            if (announcer) announcer.textContent = '';
            location.reload();
          }, 2000);

        } else {
          throw new Error('Erro ao enviar comentário');
        }
      } catch (error) {
        console.error('Erro no envio:', error);
        submitBtn.textContent = 'Enviar Comentário';
        submitBtn.disabled = false;

        if (announcer) {
          announcer.textContent = 'Erro ao enviar comentário. Tente novamente.';
        }
      }
    });
  }

  // Initialize all widgets on page
  function initWidgets() {
    const forms = findWidgets();
    forms.forEach(enhanceForm);
    console.log(`Enhanced ${forms.length} comment forms with AJAX`);
  }

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWidgets);
  } else {
    initWidgets();
  }

  // Export for manual initialization if needed
  window.IndieComments = window.IndieComments || {};
  window.IndieComments.init = initWidgets;

})();