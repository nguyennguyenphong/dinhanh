/**
 * Global Page Loader / Spinner Controller for Django + Flowbite
 * Standardized for Production environment.
 */

let loaderElement = null;
let loaderTimeout = null;
const TIMEOUT_DURATION = 12000; // 12 seconds safety threshold

/**
 * Displays the global loader overlay and sets a fallback timeout
 */
export function showLoader() {
    if (!loaderElement) {
        loaderElement = document.getElementById('global-loader');
    }

    if (loaderElement) {
        loaderElement.classList.add('active');

        if (loaderTimeout) clearTimeout(loaderTimeout);

        // Safety Fallback: Prevent UI locking on slow network, 500 error hangs, or disconnected status
        loaderTimeout = setTimeout(() => {
            hideLoader();
            console.warn("[Loader] Automatically dismissed due to server response timeout.");
        }, TIMEOUT_DURATION);
    }
}

/**
 * Hides the global loader overlay and clears active timers
 */
export function hideLoader() {
    if (!loaderElement) {
        loaderElement = document.getElementById('global-loader');
    }

    if (loaderElement) {
        loaderElement.classList.remove('active');
        if (loaderTimeout) clearTimeout(loaderTimeout);
    }
}

/**
 * Intercepts native Fetch API requests globally
 */
function interceptFetch() {
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
        // Optional: Filter out specific telemetry/background analytics endpoints here if needed
        showLoader();
        try {
            return await originalFetch(...args);
        } finally {
            hideLoader();
        }
    };
}

/**
 * Intercepts legacy XMLHttpRequest (XHR) requests globally (Axios / jQuery backup)
 */
function interceptXHR() {
    const XHR = XMLHttpRequest.prototype;
    const originalOpen = XHR.open;
    const originalSend = XHR.send;

    XHR.open = function (...args) {
        this._url = args[1];
        return originalOpen.apply(this, args);
    };

    XHR.send = function (...args) {
        showLoader();
        this.addEventListener('loadend', () => hideLoader());
        return originalSend.apply(this, args);
    };
}

/**
 * Initializes all document and window level global event listeners
 */
export function initSpinner() {
    // Ensure it runs safely if script is loaded after DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupListeners);
    } else {
        setupListeners();
    }
}

function setupListeners() {
    loaderElement = document.getElementById('global-loader');

    // 1. Event Delegation: Handle all standard anchor click events (including dynamic elements)
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');

        // Skip internal anchors, javascript links, new tabs, downloads, or modifier key clicks (Ctrl/Cmd)
        if (!href ||
            href.startsWith('#') ||
            href.startsWith('javascript:') ||
            link.getAttribute('target') === '_blank' ||
            link.hasAttribute('download') ||
            e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1) {
            return;
        }

        showLoader();
    });

    // 2. Event Delegation: Handle all form submission states (including dynamic forms)
    document.addEventListener('submit', (e) => {
        const form = e.target.closest('form');
        if (!form) return;

        // Skip background forms pointing to new tabs or executing downloads
        if (form.getAttribute('target') === '_blank' || form.hasAttribute('download')) {
            return;
        }

        showLoader();
    });

    // 3. Page Lifecycle: Trigger loader upon hard refreshes or address bar navigation transitions
    window.addEventListener('beforeunload', () => {
        showLoader();
    });

    // 4. Bfcache Recovery: Dismiss loader instantly if user navigates back/forward via browser history
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            hideLoader();
        }
    });

    // 5. API Integrations: Activate full network interception hooks
    interceptFetch();
    interceptXHR();
}