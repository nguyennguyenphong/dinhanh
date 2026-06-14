export default function initBackdrop() {
    const backdropStack = []; // Stack save backdrop element active

    /**
     * Create a new backdrop element
     */
    function createBackdrop(zIndex) {
        const bd = document.createElement('div');
        bd.className = 'ui-backdrop fixed inset-0 bg-black/50';
        bd.style.zIndex = zIndex;
        document.body.appendChild(bd);
        return bd;
    }

    /**
     * Get z-index of overlay
     */
    function getZIndex(el) {
        return parseInt(getComputedStyle(el).zIndex) || 50;
    }

    /**
     * Open overlay → push backdrop
     */
    function onOverlayOpen(overlay) {
        const overlayZ = getZIndex(overlay);
        const bd = createBackdrop(overlayZ - 1);

        // Click backdrop → đóng overlay này
        bd.addEventListener('click', () => {
            overlay
                .querySelectorAll('[data-modal-hide], [data-drawer-hide]')
                .forEach(btn => btn.click());
        });

        backdropStack.push({ overlay, backdrop: bd });
    }

    /**
     * Close overlay → pop backdrop 
     */
    function onOverlayClose(overlay) {
        const idx = backdropStack.findLastIndex(item => item.overlay === overlay);
        if (idx === -1) return;

        const { backdrop } = backdropStack[idx];
        backdrop.remove();
        backdropStack.splice(idx, 1);
    }

    /**
     * Observe all overlay in DOM
     */
    function observeOverlay(el) {
        let wasOpen = isOpen(el);

        const obs = new MutationObserver(() => {
            const nowOpen = isOpen(el);
            if (!wasOpen && nowOpen) onOverlayOpen(el);
            if (wasOpen && !nowOpen) onOverlayClose(el);
            wasOpen = nowOpen;
        });

        obs.observe(el, { attributes: true, attributeFilter: ['class'] });

        if (wasOpen) onOverlayOpen(el);
    }

    function isOpen(el) {
        if (el.classList.contains('hidden')) return false;
        if (el.classList.contains('-translate-x-full')) return false;
        return true;
    }

    document.querySelectorAll('.ui-overlay').forEach(observeOverlay);

    const domObserver = new MutationObserver(mutations => {
        mutations.forEach(m => {
            m.addedNodes.forEach(node => {
                if (node.nodeType !== 1) return;
                if (node.classList?.contains('ui-overlay')) observeOverlay(node);
                node.querySelectorAll?.('.ui-overlay').forEach(observeOverlay);
            });
        });
    });
    domObserver.observe(document.body, { childList: true, subtree: true });

    document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape' || !backdropStack.length) return;
        const top = backdropStack[backdropStack.length - 1];
        top.overlay
            .querySelectorAll('[data-modal-hide], [data-drawer-hide]')
            .forEach(btn => btn.click());
    });
}