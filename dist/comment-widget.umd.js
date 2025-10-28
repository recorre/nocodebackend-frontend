(function (factory) {
    typeof define === 'function' && define.amd ? define(factory) :
    factory();
})((function () { 'use strict';

    /**
     * API Client for Comment Widget
     * Handles communication with FastAPI proxy
     */

    class APIClient {
        constructor(baseUrl = 'https://comment-widget-backend.vercel.app') {
            this.baseUrl = baseUrl;
            this.defaultHeaders = {
                'Content-Type': 'application/json'
            };
        }

        async request(endpoint, options = {}) {
            const url = `${this.baseUrl}${endpoint}`;
            const config = {
                headers: { ...this.defaultHeaders, ...options.headers },
                ...options
            };

            try {
                const response = await fetch(url, config);

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
                }

                return await response.json();
            } catch (error) {
                if (error.name === 'TypeError' && error.message.includes('fetch')) {
                    throw new Error('Network error: Unable to connect to API');
                }
                throw error;
            }
        }

        // Comments API
        async getComments(threadId, options = {}) {
            const params = new URLSearchParams({
                thread_id: threadId,
                ...options
            });

            return this.request(`/widget/comments/${threadId}?${params}`);
        }

        async createComment(commentData) {
            return this.request('/comments', {
                method: 'POST',
                body: JSON.stringify(commentData)
            });
        }

        async updateComment(commentId, commentData) {
            return this.request(`/comments/${commentId}`, {
                method: 'PUT',
                body: JSON.stringify(commentData)
            });
        }

        async deleteComment(commentId) {
            return this.request(`/comments/${commentId}`, {
                method: 'DELETE'
            });
        }

        async moderateComment(commentId, moderationData) {
            return this.request(`/comments/${commentId}/moderate`, {
                method: 'PUT',
                body: JSON.stringify(moderationData)
            });
        }

        // Threads API
        async getThread(threadId) {
            return this.request(`/threads/${threadId}`);
        }

        async createThread(threadData) {
            return this.request('/threads', {
                method: 'POST',
                body: JSON.stringify(threadData)
            });
        }

        // Demo API
        async getDemoThread() {
            return this.request('/demo/thread');
        }

        // Health check
        async healthCheck() {
            return this.request('/health');
        }
    }

    /**
     * Comment Renderer for Widget
     * Handles HTML rendering of comments with nesting
     */

    class CommentRenderer {
        constructor() {
            this.templates = {
                widget: (data) => `
                <div class="comment-widget" data-theme="${data.theme}">
                    <div class="comment-header">
                        <h3>💬 Comments</h3>
                        ${data.showThemeSelector ? this.renderThemeSelector(data.theme, data.onThemeChange) : ''}
                    </div>

                    ${data.error ? this.renderError(data.error) : ''}

                    ${data.loading ? this.renderLoading() : ''}

                    ${!data.loading && !data.error ? this.renderCommentForm(data.onSubmit) : ''}

                    <div class="comment-list">
                        ${data.comments.length > 0
                            ? data.comments.map(comment => this.renderComment(comment, 0, data.maxDepth)).join('')
                            : this.renderEmptyState()
                        }
                    </div>
                </div>
            `,

                comment: (comment, level, maxDepth) => `
                <div class="comment-item level-${level}" data-id="${comment.id}">
                    <div class="comment-avatar">
                        <div class="avatar-placeholder">
                            ${comment.author_name.charAt(0).toUpperCase()}
                        </div>
                    </div>
                    <div class="comment-content">
                        <div class="comment-meta">
                            <span class="comment-author">${this.escapeHtml(comment.author_name)}</span>
                            <span class="comment-date">${this.formatDate(comment.created_at)}</span>
                        </div>
                        <div class="comment-text">${this.formatContent(comment.content)}</div>
                        <div class="comment-actions">
                            ${level < maxDepth ? `<button class="reply-btn" data-parent-id="${comment.id}">Reply</button>` : ''}
                        </div>
                        ${comment.replies && comment.replies.length > 0
                            ? `<div class="comment-replies">${comment.replies.map(reply => this.renderComment(reply, level + 1, maxDepth)).join('')}</div>`
                            : ''
                        }
                    </div>
                </div>
            `,

                form: (onSubmit) => `
                <form class="comment-form" id="comment-form">
                    <div class="form-group">
                        <input type="text" id="author-name" placeholder="Your name" required>
                    </div>
                    <div class="form-group">
                        <input type="email" id="author-email" placeholder="Your email" required>
                    </div>
                    <div class="form-group">
                        <textarea id="comment-content" placeholder="Write your comment..." required rows="4"></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="submit-btn">Post Comment</button>
                    </div>
                </form>
            `,

                themeSelector: (currentTheme, onChange) => `
                <select class="theme-selector" id="theme-selector">
                    <option value="default" ${currentTheme === 'default' ? 'selected' : ''}>Default</option>
                    <option value="dark" ${currentTheme === 'dark' ? 'selected' : ''}>Dark</option>
                    <option value="matrix" ${currentTheme === 'matrix' ? 'selected' : ''}>Matrix</option>
                    <option value="neocities" ${currentTheme === 'neocities' ? 'selected' : ''}>NeoCities</option>
                    <option value="serene-mist" ${currentTheme === 'serene-mist' ? 'selected' : ''}>Serene Mist</option>
                    <option value="neon-pulse" ${currentTheme === 'neon-pulse' ? 'selected' : ''}>Neon Pulse</option>
                    <option value="geometric-prime" ${currentTheme === 'geometric-prime' ? 'selected' : ''}>Geometric Prime</option>
                    <option value="forest-flow" ${currentTheme === 'forest-flow' ? 'selected' : ''}>Forest Flow</option>
                    <option value="digital-chaos" ${currentTheme === 'digital-chaos' ? 'selected' : ''}>Digital Chaos</option>
                </select>
            `,

                loading: () => `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Loading comments...</p>
                </div>
            `,

                error: (message) => `
                <div class="error-state">
                    <p>❌ ${this.escapeHtml(message)}</p>
                </div>
            `,

                empty: () => `
                <div class="empty-state">
                    <p>💭 No comments yet. Be the first to comment!</p>
                </div>
            `
            };
        }

        render(data) {
            return this.templates.widget(data);
        }

        renderComment(comment, level, maxDepth) {
            return this.templates.comment(comment, level, maxDepth);
        }

        renderCommentForm(onSubmit) {
            return this.templates.form(onSubmit);
        }

        renderThemeSelector(currentTheme, onChange) {
            return this.templates.themeSelector(currentTheme, onChange);
        }

        renderLoading() {
            return this.templates.loading();
        }

        renderError(message) {
            return this.templates.error(message);
        }

        renderEmptyState() {
            return this.templates.empty();
        }

        // Utility methods
        formatDate(dateString) {
            if (!dateString) return '';

            const date = new Date(dateString);
            const now = new Date();
            const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));

            if (diffInHours < 1) return 'Just now';
            if (diffInHours < 24) return `${diffInHours}h ago`;

            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        formatContent(content) {
            // Basic markdown-like formatting
            return this.escapeHtml(content)
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>');
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    /**
     * Enhanced Theme Manager for Comment Widget
     * Integrates with the dashboard theme system
     */

    class ThemeManager {
        constructor(currentTheme = 'default') {
            this.currentTheme = currentTheme;
            this.themes = {
                'default': this.getDefaultTheme(),
                'dark': this.getDarkTheme(),
                'matrix': this.getMatrixTheme(),
                'neocities': this.getNeocitiesTheme(),
                'serene-mist': this.getSereneMistTheme(),
                'neon-pulse': this.getNeonPulseTheme(),
                'geometric-prime': this.getGeometricPrimeTheme(),
                'forest-flow': this.getForestFlowTheme(),
                'digital-chaos': this.getDigitalChaosTheme()
            };
            this.themeCSS = new Map();
            this.transitionDuration = 300;
            this.init();
        }

        init() {
            // Listen for dashboard theme changes
            document.addEventListener('themeChange', (e) => {
                this.syncWithDashboard(e.detail.theme);
            });

            // Load external theme CSS
            this.loadThemeCSS();
        }

        setTheme(theme, animate = true) {
            if (!this.themes[theme]) {
                console.warn(`Theme "${theme}" not found, falling back to default`);
                theme = 'default';
            }

            const previousTheme = this.currentTheme;
            this.currentTheme = theme;

            // Apply theme with animation
            this.applyTheme(animate);

            // Dispatch custom event
            this.dispatchThemeChange(previousTheme, theme);
        }

        syncWithDashboard(dashboardTheme) {
            // Map dashboard themes to widget themes
            const themeMapping = {
                'default': 'default',
                'dark': 'dark',
                'matrix': 'matrix',
                'neocities': 'neocities'
            };

            const widgetTheme = themeMapping[dashboardTheme] || 'default';
            if (widgetTheme !== this.currentTheme) {
                this.setTheme(widgetTheme, true);
            }
        }

        applyTheme(animate = true) {
            const theme = this.themes[this.currentTheme] || this.themes.default;

            // Apply CSS variables
            this.applyCSSVariables(theme, animate);

            // Apply theme-specific effects
            this.applyThemeEffects(theme);

            // Update meta theme-color
            this.updateMetaThemeColor(theme.colors.primary);
        }

        applyCSSVariables(theme, animate = true) {
            const root = document.documentElement;

            // Set transition properties
            if (animate) {
                root.style.setProperty('--widget-transition-duration', theme.transitions.duration);
                root.style.setProperty('--widget-transition-easing', theme.transitions.easing);
            } else {
                root.style.setProperty('--widget-transition-duration', '0s');
            }

            // Apply colors
            Object.entries(theme.colors).forEach(([key, value]) => {
                root.style.setProperty(`--widget-${key}`, value);
            });

            // Apply typography
            Object.entries(theme.fonts).forEach(([key, value]) => {
                root.style.setProperty(`--widget-font-${key}`, value);
            });

            // Apply spacing
            Object.entries(theme.spacing).forEach(([key, value]) => {
                root.style.setProperty(`--widget-spacing-${key}`, value);
            });

            // Apply design tokens
            root.style.setProperty('--widget-border-radius', theme.borderRadius);
        }

        applyThemeEffects(theme) {
            // Remove existing theme classes
            const widget = document.querySelector('comment-widget');
            if (widget && widget.shadowRoot) {
                const app = widget.shadowRoot.querySelector('#indie-comments-app');
                if (app) {
                    app.className = app.className.replace(/theme-\w+/g, '');
                    app.classList.add(`theme-${this.currentTheme}`);
                }
            }

            // Apply theme-specific effects
            switch (this.currentTheme) {
                case 'matrix':
                    this.applyMatrixEffects();
                    break;
                case 'neocities':
                    this.applyNeocitiesEffects();
                    break;
                case 'dark':
                    this.applyDarkEffects();
                    break;
                case 'serene-mist':
                    this.applySereneMistEffects();
                    break;
                case 'neon-pulse':
                    this.applyNeonPulseEffects();
                    break;
                case 'geometric-prime':
                    this.applyGeometricPrimeEffects();
                    break;
                case 'forest-flow':
                    this.applyForestFlowEffects();
                    break;
                case 'digital-chaos':
                    this.applyDigitalChaosEffects();
                    break;
                default:
                    this.applyDefaultEffects();
            }
        }

        applyMatrixEffects() {
            // Matrix-specific effects can be added here
            console.log('Matrix theme effects applied');
        }

        applyNeocitiesEffects() {
            // NeoCities-specific effects can be added here
            console.log('NeoCities theme effects applied');
        }

        applyDarkEffects() {
            // Dark theme-specific effects can be added here
            console.log('Dark theme effects applied');
        }

        applyDefaultEffects() {
            // Default theme-specific effects can be added here
            console.log('Default theme effects applied');
        }

        applySereneMistEffects() {
            // Organic breathing animation
            this.widgetElement.style.animation = 'serene-breath 4s ease-in-out infinite';
        }

        applyNeonPulseEffects() {
            // Pulsing neon glow
            this.widgetElement.style.animation = 'neon-pulse 2s ease-in-out infinite';
        }

        applyGeometricPrimeEffects() {
            // 3D geometric transforms
            this.widgetElement.style.animation = 'geometric-rotate 8s linear infinite';
        }

        applyForestFlowEffects() {
            // Flowing wave animation
            this.widgetElement.style.animation = 'forest-wave 6s ease-in-out infinite';
        }

        applyDigitalChaosEffects() {
            // Glitch and scan line effects
            this.widgetElement.style.animation = 'digital-glitch 0.3s ease-in-out infinite, scan-line 2s linear infinite';
        }

        updateMetaThemeColor(color) {
            let metaThemeColor = document.querySelector('meta[name="theme-color"]');
            if (!metaThemeColor) {
                metaThemeColor = document.createElement('meta');
                metaThemeColor.name = 'theme-color';
                document.head.appendChild(metaThemeColor);
            }
            metaThemeColor.content = color;
        }

        dispatchThemeChange(previousTheme, newTheme) {
            document.dispatchEvent(new CustomEvent('commentWidgetThemeChange', {
                detail: {
                    theme: newTheme,
                    previousTheme: previousTheme,
                    config: this.themes[newTheme]
                }
            }));
        }

        async loadThemeCSS() {
            // Load external theme CSS files
            const themeFiles = {
                'dark': '/frontend/static/css/themes/dark.css',
                'matrix': '/frontend/static/css/themes/matrix.css',
                'neocities': '/frontend/static/css/themes/neocities.css'
            };

            for (const [theme, file] of Object.entries(themeFiles)) {
                try {
                    const response = await fetch(file);
                    if (response.ok) {
                        const css = await response.text();
                        this.themeCSS.set(theme, css);
                    }
                } catch (error) {
                    console.warn(`Failed to load theme CSS for ${theme}:`, error);
                }
            }
        }

        getThemeCSS(theme) {
            return this.themeCSS.get(theme) || '';
        }

        // Theme definitions using CSS variables
        getDefaultTheme() {
            return `
            /* Default theme with CSS variables */
            .comment-widget {
                font-family: var(--widget-font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
                max-width: 680px;
                margin: 2rem auto;
                padding: 1.5rem;
                background: var(--widget-background, #fff);
                border: 1px solid var(--widget-border, #e0e0e0);
                border-radius: var(--widget-border-radius, 8px);
                box-shadow: 0 2px 10px var(--widget-shadow, rgba(0,0,0,0.1));
                color: var(--widget-text, #333);
                transition: var(--widget-transition, all 0.3s ease);
            }

            .comment-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid var(--widget-border, #e0e0e0);
            }

            .comment-header h3 {
                margin: 0;
                color: var(--widget-text, #333);
                font-size: 1.5rem;
                font-weight: 600;
            }

            .theme-selector {
                padding: 0.5rem;
                border: 1px solid var(--widget-border, #ddd);
                border-radius: var(--widget-border-radius, 4px);
                background: var(--widget-surface, #fff);
                color: var(--widget-text, #333);
                font-size: 0.9rem;
            }

            .comment-form {
                background: var(--widget-surface, #f8f9fa);
                padding: 1.5rem;
                border-radius: var(--widget-border-radius, 6px);
                margin-bottom: 2rem;
                border: 1px solid var(--widget-border, #e9ecef);
            }

            .form-group {
                margin-bottom: 1rem;
            }

            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid var(--widget-border, #ddd);
                border-radius: var(--widget-border-radius, 4px);
                font-size: 1rem;
                box-sizing: border-box;
                font-family: inherit;
                background: var(--widget-surface, #fff);
                color: var(--widget-text, #333);
                transition: var(--widget-transition, border-color 0.2s);
            }

            .form-group input:focus,
            .form-group textarea:focus {
                border-color: var(--widget-primary, #007cba);
                box-shadow: 0 0 0 0.2rem rgba(0, 124, 186, 0.25);
            }

            .form-group textarea {
                min-height: 100px;
                resize: vertical;
            }

            .form-actions {
                text-align: right;
            }

            .submit-btn {
                background: var(--widget-primary, #007cba);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: var(--widget-border-radius, 4px);
                font-size: 1rem;
                cursor: pointer;
                transition: var(--widget-transition, background 0.2s);
            }

            .submit-btn:hover {
                background: var(--widget-primary, #007cba);
                opacity: 0.9;
                transform: translateY(-1px);
            }

            .comment-list {
                margin-top: 1.5rem;
            }

            .comment-item {
                display: flex;
                padding: 1rem;
                margin-bottom: 1rem;
                background: var(--widget-surface, #fff);
                border: 1px solid var(--widget-border, #eee);
                border-radius: var(--widget-border-radius, 6px);
                border-left: 3px solid var(--widget-primary, #007cba);
                transition: var(--widget-transition, all 0.2s);
            }

            .comment-item:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px var(--widget-shadow, rgba(0,0,0,0.1));
            }

            .comment-item.level-1 {
                margin-left: 2rem;
                border-left-width: 2px;
                border-left-color: var(--widget-secondary, #888);
            }

            .comment-item.level-2 {
                margin-left: 3rem;
                border-left-width: 1px;
                border-left-color: var(--widget-border, #ccc);
            }

            .comment-avatar {
                margin-right: 1rem;
                flex-shrink: 0;
            }

            .avatar-placeholder {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: var(--widget-primary, #007cba);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 1.1rem;
            }

            .comment-content {
                flex: 1;
            }

            .comment-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
            }

            .comment-author {
                font-weight: 600;
                color: var(--widget-primary, #007cba);
            }

            .comment-date {
                color: var(--widget-text-muted, #888);
            }

            .comment-text {
                line-height: 1.6;
                color: var(--widget-text, #444);
                margin-bottom: 0.5rem;
            }

            .comment-actions {
                font-size: 0.8rem;
            }

            .reply-btn {
                background: none;
                border: none;
                color: var(--widget-primary, #007cba);
                cursor: pointer;
                text-decoration: underline;
                font-size: 0.8rem;
                transition: var(--widget-transition, color 0.2s);
            }

            .reply-btn:hover {
                color: var(--widget-primary, #007cba);
                opacity: 0.8;
            }

            .comment-replies {
                margin-top: 1rem;
                margin-left: 1rem;
            }

            .loading-state,
            .error-state,
            .empty-state {
                text-align: center;
                padding: 2rem;
                font-style: italic;
            }

            .loading-state {
                color: var(--widget-text-muted, #666);
            }

            .error-state {
                color: var(--widget-danger, #dc3545);
                background: rgba(220, 53, 69, 0.1);
                border: 1px solid var(--widget-danger, #dc3545);
                border-radius: var(--widget-border-radius, 4px);
            }

            .empty-state {
                color: var(--widget-text-muted, #666);
            }

            .spinner {
                border: 3px solid var(--widget-light, #f3f3f3);
                border-top: 3px solid var(--widget-primary, #007cba);
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            @media (max-width: 768px) {
                .comment-widget {
                    margin: 1rem;
                    padding: 1rem;
                }

                .comment-item.level-1,
                .comment-item.level-2 {
                    margin-left: 1rem;
                }

                .theme-selector {
                    margin-top: 0.5rem;
                    width: 100%;
                }

                .comment-header {
                    flex-direction: column;
                    align-items: stretch;
                }
            }
        `;
        }

        getDarkTheme() {
            return `
            .comment-widget {
                background: #2d2d2d;
                border-color: #444;
                color: #e0e0e0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }

            .comment-header h3 {
                color: #e0e0e0;
            }

            .theme-selector {
                background: #3a3a3a;
                border-color: #555;
                color: #e0e0e0;
            }

            .comment-form {
                background: #3a3a3a;
                border-color: #555;
            }

            .form-group input,
            .form-group textarea {
                background: #3a3a3a;
                border-color: #555;
                color: #e0e0e0;
            }

            .submit-btn {
                background: #4fc3f7;
                color: #000;
            }

            .submit-btn:hover {
                background: #29b6f6;
            }

            .comment-item {
                background: #2d2d2d;
                border-color: #444;
                color: #e0e0e0;
                border-left-color: #4fc3f7;
            }

            .comment-item.level-1 {
                border-left-color: #888;
            }

            .comment-item.level-2 {
                border-left-color: #ccc;
            }

            .avatar-placeholder {
                background: #4fc3f7;
                color: #000;
            }

            .comment-author {
                color: #4fc3f7;
            }

            .comment-date {
                color: #b0b0b0;
            }

            .comment-text {
                color: #e0e0e0;
            }

            .reply-btn {
                color: #4fc3f7;
            }

            .reply-btn:hover {
                color: #29b6f6;
            }

            .loading-state,
            .empty-state {
                color: #b0b0b0;
            }

            .error-state {
                color: #ff6b6b;
                background: rgba(255, 107, 107, 0.1);
                border-color: rgba(255, 107, 107, 0.3);
            }
        `;
        }

        getMatrixTheme() {
            return `
            .comment-widget {
                background: #000;
                border-color: #0a0;
                color: #0f0;
                font-family: 'Courier New', monospace;
                box-shadow: 0 2px 10px rgba(0,255,0,0.1);
            }

            .comment-header h3 {
                color: #0f0;
            }

            .theme-selector {
                background: #010;
                border-color: #080;
                color: #0f0;
                font-family: 'Courier New', monospace;
            }

            .comment-form {
                background: #010;
                border-color: #080;
            }

            .form-group input,
            .form-group textarea {
                background: #010;
                border-color: #080;
                color: #0f0;
                font-family: 'Courier New', monospace;
            }

            .submit-btn {
                background: #0a0;
                color: #000;
                font-family: 'Courier New', monospace;
            }

            .submit-btn:hover {
                background: #0f0;
                box-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
            }

            .comment-item {
                background: #000;
                border-color: #0a0;
                color: #0f0;
                border-left-color: #0f0;
                font-family: 'Courier New', monospace;
            }

            .comment-item.level-1 {
                border-left-color: #080;
            }

            .comment-item.level-2 {
                border-left-color: #040;
            }

            .avatar-placeholder {
                background: #0f0;
                color: #000;
            }

            .comment-author {
                color: #0f0;
            }

            .comment-date {
                color: #6b7280;
            }

            .comment-text {
                color: #0f0;
            }

            .reply-btn {
                color: #0f0;
            }

            .reply-btn:hover {
                color: #0a0;
                text-shadow: 0 0 3px rgba(0, 255, 0, 0.5);
            }

            .loading-state,
            .empty-state {
                color: #6b7280;
            }

            .error-state {
                color: #ff4444;
                background: rgba(255, 68, 68, 0.1);
                border-color: rgba(255, 68, 68, 0.3);
            }
        `;
        }

        getNeocitiesTheme() {
            return `
            .comment-widget {
                background: #ccffff;
                border: 2px dashed #996699;
                color: #330033;
                box-shadow: 0 4px 15px rgba(153, 102, 153, 0.2);
            }

            .comment-header h3 {
                color: #330033;
            }

            .theme-selector {
                background: #ffff99;
                border: 2px dotted #669966;
                color: #330033;
            }

            .comment-form {
                background: #ffff99;
                border: 2px dotted #669966;
            }

            .form-group input,
            .form-group textarea {
                background: #ffff99;
                border: 2px dotted #669966;
                color: #330033;
            }

            .submit-btn {
                background: #ffccff;
                color: #330033;
                border: 2px solid #996699;
            }

            .submit-btn:hover {
                background: #ff99ff;
            }

            .comment-item {
                background: #ccffff;
                border: 2px dashed #996699;
                color: #330033;
                border-left: 4px solid #996699;
            }

            .comment-item.level-1 {
                border-left-color: #669966;
                border-left-style: dotted;
            }

            .comment-item.level-2 {
                border-left-color: #cc99ff;
                border-left-style: dashed;
            }

            .avatar-placeholder {
                background: #ffccff;
                color: #330033;
                border: 2px solid #996699;
            }

            .comment-author {
                color: #663399;
                font-weight: bold;
            }

            .comment-date {
                color: #666699;
            }

            .comment-text {
                color: #330033;
            }

            .reply-btn {
                color: #663399;
                background: #ffccff;
                border: 1px solid #996699;
                padding: 0.2rem 0.5rem;
                border-radius: 3px;
            }

            .reply-btn:hover {
                background: #ff99ff;
            }

            .loading-state,
            .empty-state {
                color: #666699;
            }

            .error-state {
                color: #cc0000;
                background: rgba(255, 204, 204, 0.7);
                border: 2px dashed #cc6666;
            }
        `;
        }

        getSereneMistTheme() {
            return {
                colors: {
                    primary: '#8B9D77',
                    secondary: '#A8B5A0',
                    background: '#F8F9F7',
                    surface: '#FFFFFF',
                    text: '#4A5D3A',
                    'text-muted': '#7A8F69',
                    border: '#D4E2D0',
                    light: '#F0F2EF',
                    danger: '#C17D5F'
                },
                fonts: {
                    family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    size: '14px',
                    weight: '400'
                },
                spacing: {
                    small: '8px',
                    medium: '16px',
                    large: '24px'
                },
                borderRadius: '12px',
                transitions: {
                    duration: '0.4s',
                    easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
                }
            };
        }

        getNeonPulseTheme() {
            return {
                colors: {
                    primary: '#00FF88',
                    secondary: '#FF0080',
                    background: '#0A0A0A',
                    surface: '#1A1A1A',
                    text: '#FFFFFF',
                    'text-muted': '#888888',
                    border: '#333333',
                    light: '#2A2A2A',
                    danger: '#FF4444'
                },
                fonts: {
                    family: "'JetBrains Mono', 'Courier New', monospace",
                    size: '14px',
                    weight: '400'
                },
                spacing: {
                    small: '8px',
                    medium: '16px',
                    large: '24px'
                },
                borderRadius: '4px',
                transitions: {
                    duration: '0.2s',
                    easing: 'ease-out'
                }
            };
        }

        getGeometricPrimeTheme() {
            return {
                colors: {
                    primary: '#FF6B35',
                    secondary: '#F7931E',
                    background: '#2C2C2C',
                    surface: '#3A3A3A',
                    text: '#FFFFFF',
                    'text-muted': '#CCCCCC',
                    border: '#555555',
                    light: '#4A4A4A',
                    danger: '#FF4444'
                },
                fonts: {
                    family: "'IBM Plex Sans', sans-serif",
                    size: '14px',
                    weight: '500'
                },
                spacing: {
                    small: '12px',
                    medium: '20px',
                    large: '32px'
                },
                borderRadius: '0px',
                transitions: {
                    duration: '0.3s',
                    easing: 'ease-in-out'
                }
            };
        }

        getForestFlowTheme() {
            return {
                colors: {
                    primary: '#2D5A3D',
                    secondary: '#4A7C59',
                    background: '#F5F8F5',
                    surface: '#FFFFFF',
                    text: '#1A3D2A',
                    'text-muted': '#5A8F6B',
                    border: '#B8D4BB',
                    light: '#E8F5E8',
                    danger: '#8B4513'
                },
                fonts: {
                    family: "'Crimson Text', serif",
                    size: '15px',
                    weight: '400'
                },
                spacing: {
                    small: '10px',
                    medium: '18px',
                    large: '28px'
                },
                borderRadius: '16px',
                transitions: {
                    duration: '0.5s',
                    easing: 'ease-in-out'
                }
            };
        }

        getDigitalChaosTheme() {
            return {
                colors: {
                    primary: '#FF00FF',
                    secondary: '#00FFFF',
                    background: '#000000',
                    surface: '#0F0F0F',
                    text: '#FFFFFF',
                    'text-muted': '#AAAAAA',
                    border: '#333333',
                    light: '#1A1A1A',
                    danger: '#FF0000'
                },
                fonts: {
                    family: "'Share Tech Mono', monospace",
                    size: '13px',
                    weight: '400'
                },
                spacing: {
                    small: '6px',
                    medium: '12px',
                    large: '18px'
                },
                borderRadius: '2px',
                transitions: {
                    duration: '0.1s',
                    easing: 'step-end'
                }
            };
        }
    }

    /**
     * Utility functions for Comment Widget
     */

    class Utils {
        static generateThreadId() {
            // Generate thread ID based on current page URL
            return btoa(window.location.href).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
        }

        static generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        }

        static debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        static throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            }
        }

        static escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        static formatDate(dateString) {
            if (!dateString) return '';

            const date = new Date(dateString);
            const now = new Date();
            const diffInSeconds = Math.floor((now - date) / 1000);
            const diffInMinutes = Math.floor(diffInSeconds / 60);
            const diffInHours = Math.floor(diffInMinutes / 60);
            const diffInDays = Math.floor(diffInHours / 24);

            if (diffInSeconds < 60) return 'Just now';
            if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
            if (diffInHours < 24) return `${diffInHours}h ago`;
            if (diffInDays < 7) return `${diffInDays}d ago`;

            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        static formatContent(content) {
            // Basic markdown-like formatting
            return this.escapeHtml(content)
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/`(.*?)`/g, '<code>$1</code>')
                .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
        }

        static validateEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        }

        static validateComment(comment) {
            const errors = [];

            if (!comment.author_name || comment.author_name.trim().length < 2) {
                errors.push('Name must be at least 2 characters long');
            }

            if (!comment.author_email || !this.validateEmail(comment.author_email)) {
                errors.push('Please enter a valid email address');
            }

            if (!comment.content || comment.content.trim().length < 10) {
                errors.push('Comment must be at least 10 characters long');
            }

            if (comment.content && comment.content.length > 2000) {
                errors.push('Comment must be less than 2000 characters');
            }

            return {
                isValid: errors.length === 0,
                errors
            };
        }

        static showNotification(message, type = 'info', duration = 3000) {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;

            // Style the notification
            Object.assign(notification.style, {
                position: 'fixed',
                top: '20px',
                right: '20px',
                padding: '12px 16px',
                borderRadius: '4px',
                color: 'white',
                fontSize: '14px',
                zIndex: '10000',
                opacity: '0',
                transform: 'translateY(-20px)',
                transition: 'all 0.3s ease',
                maxWidth: '300px',
                wordWrap: 'break-word'
            });

            // Set background color based on type
            const colors = {
                success: '#28a745',
                error: '#dc3545',
                warning: '#ffc107',
                info: '#007bff'
            };
            notification.style.backgroundColor = colors[type] || colors.info;

            // Add to page
            document.body.appendChild(notification);

            // Animate in
            setTimeout(() => {
                notification.style.opacity = '1';
                notification.style.transform = 'translateY(0)';
            }, 10);

            // Remove after duration
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, duration);
        }

        static copyToClipboard(text) {
            if (navigator.clipboard && window.isSecureContext) {
                return navigator.clipboard.writeText(text);
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                return new Promise((resolve, reject) => {
                    if (document.execCommand('copy')) {
                        resolve();
                    } else {
                        reject(new Error('Failed to copy text'));
                    }
                    document.body.removeChild(textArea);
                });
            }
        }

        static getViewportSize() {
            return {
                width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
                height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
            };
        }

        static isMobile() {
            return this.getViewportSize().width < 768;
        }

        static isTouchDevice() {
            return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        }

        static scrollToElement(element, offset = 0) {
            if (!element) return;

            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }

        static animateElement(element, animation, duration = 300) {
            if (!element) return Promise.resolve();

            return new Promise((resolve) => {
                element.style.animation = `${animation} ${duration}ms ease`;
                setTimeout(() => {
                    element.style.animation = '';
                    resolve();
                }, duration);
            });
        }

        static deepClone(obj) {
            if (obj === null || typeof obj !== 'object') return obj;
            if (obj instanceof Date) return new Date(obj.getTime());
            if (obj instanceof Array) return obj.map(item => this.deepClone(item));
            if (typeof obj === 'object') {
                const cloned = {};
                Object.keys(obj).forEach(key => {
                    cloned[key] = this.deepClone(obj[key]);
                });
                return cloned;
            }
        }

        static sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    }

    /**
     * Comment Widget v2.0 - Improved Architecture
     * Modular, themeable, and API-integrated comment system
     */


    class CommentWidget extends HTMLElement {
        constructor() {
            super();

            // Configuration from attributes
            this.threadId = this.getAttribute('thread-id') || Utils.generateThreadId();
            this.apiBaseUrl = this.getAttribute('api-base-url') || 'https://comment-widget-backend.vercel.app';
            this.theme = this.getAttribute('theme') || 'default';
            this.maxDepth = parseInt(this.getAttribute('max-depth')) || 3;

            // Initialize components
            this.api = new APIClient(this.apiBaseUrl);
            this.renderer = new CommentRenderer();
            this.themeManager = new ThemeManager(this.theme);

            // Widget state
            this.comments = [];
            this.loading = false;
            this.error = null;

            // Create shadow DOM
            this.shadow = this.attachShadow({ mode: 'open' });

            // Initialize
            this.init();
        }

        async init() {
            try {
                this.loading = true;
                this.render();

                // Load comments from API
                await this.loadComments();

                this.loading = false;
                this.render();

            } catch (error) {
                console.error('Widget initialization error:', error);
                this.error = error.message;
                this.loading = false;
                this.render();
            }
        }

        async loadComments() {
            try {
                const response = await this.api.getComments(this.threadId);
                this.comments = response.comments || [];
            } catch (error) {
                console.error('Error loading comments:', error);
                this.error = 'Failed to load comments';
            }
        }

        async submitComment(commentData) {
            try {
                this.loading = true;
                this.render();

                const result = await this.api.createComment({
                    thread_id: parseInt(this.threadId),
                    author_name: commentData.author_name,
                    author_email: commentData.author_email,
                    content: commentData.content,
                    parent_id: commentData.parent_id || null
                });

                // Reload comments after successful submission
                await this.loadComments();

                this.loading = false;
                this.render();

                return result;

            } catch (error) {
                console.error('Error submitting comment:', error);
                this.error = error.message;
                this.loading = false;
                this.render();
                throw error;
            }
        }

        setTheme(theme) {
            this.theme = theme;
            this.themeManager.setTheme(theme);
            this.render();
        }

        connectedCallback() {
            // Listen for theme changes from page
            document.addEventListener('themeChange', (e) => {
                if (e.detail && e.detail.theme) {
                    this.setAttribute('theme', e.detail.theme);
                    this.setTheme(e.detail.theme);
                }
            });
        }

        render() {
            // Load enhanced CSS
            this.loadEnhancedCSS();

            const styles = this.themeManager.getStyles();
            const html = this.renderer.render({
                comments: this.comments,
                loading: this.loading,
                error: this.error,
                theme: this.theme,
                maxDepth: this.maxDepth,
                onSubmit: (data) => this.submitComment(data),
                onThemeChange: (theme) => this.setTheme(theme)
            });

            this.shadow.innerHTML = `
            <style>${styles}</style>
            ${html}
        `;
        }

        loadEnhancedCSS() {
            // Load the enhanced widget CSS if not already loaded
            if (!this.shadow.querySelector('#widget-enhanced-css')) {
                const link = document.createElement('link');
                link.id = 'widget-enhanced-css';
                link.rel = 'stylesheet';
                link.href = '/widget/src/widget.css';
                this.shadow.appendChild(link);
            }
        }

        // Public API methods
        refresh() {
            this.loadComments();
        }

        getComments() {
            return this.comments;
        }

        getTheme() {
            return this.theme;
        }
    }

    // Register the custom element
    customElements.define('comment-widget', CommentWidget);

    // Auto-initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', () => {
        console.log('Comment Widget v2.0 loaded');
    });

    // Export for testing
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { CommentWidget };
    }

}));
//# sourceMappingURL=comment-widget.umd.js.map
