#!/bin/bash

# Script to build the Indie Comments Widget
# Creates a bundled, minified version for production

set -e

echo "🏗️  Building Indie Comments Widget..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Use npx esbuild (available via package.json)

# Create dist directory
mkdir -p dist

# Build with esbuild (simpler and more reliable)
echo "📦 Bundling widget with esbuild..."
npx esbuild static/js/widget.js --bundle --minify --outfile=dist/comment-widget.min.js --format=iife --global-name=CommentWidget

# Copy CSS
echo "🎨 Copying CSS..."
cp src/widget.css dist/widget.css

# Copy templates
echo "📄 Copying templates..."
cp templates/widget.html dist/
cp templates/widget_inline.css dist/

# Create embed script
echo "🔗 Creating embed script..."
cat > dist/embed.js << 'EOF'
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
EOF

echo -e "${GREEN}✅ Widget built successfully!${NC}"
echo ""
echo "📁 Output files:"
echo "   - dist/widget.min.js (bundled JS)"
echo "   - dist/widget.css (styles)"
echo "   - dist/widget.html (SSR template)"
echo "   - dist/embed.js (embed script)"
echo ""
echo "🚀 To use:"
echo "   1. Upload dist/ files to your CDN"
echo "   2. Include embed.js on your site"
echo "   3. Use the SSR template on your backend"