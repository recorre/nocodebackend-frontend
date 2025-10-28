/**
 * Indie Comments Widget - Embed Script
 * Include this on your site to load the comment widget
 */

(function() {
  'use strict';

  // Configuration
  window.IndieComments = window.IndieComments || {
    apiUrl: 'https://your-api-endpoint.com',
    theme: 'default'
  };

  // Load widget CSS
  const cssLink = document.createElement('link');
  cssLink.rel = 'stylesheet';
  cssLink.href = 'https://cdn.jsdelivr.net/gh/your-repo@main/dist/widget.css';
  document.head.appendChild(cssLink);

  // Load widget JS
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/gh/your-repo@main/dist/widget.min.js';
  script.defer = true;
  document.head.appendChild(script);

  console.log('Indie Comments Widget loaded');
})();
