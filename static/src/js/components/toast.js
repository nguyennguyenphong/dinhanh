/**
 * Initializes and displays system messages sent from Django's messaging framework.
 * Parses JSON data embedded within the DOM and triggers the global toast component.
 */
export function initToast() {
    const dataEl = document.getElementById('toast-data');
    if (!dataEl) return;

    try {
        // Safe regex replacement to fix single-quoted JSON strings from Python/Django context
        const rawMessages = dataEl.dataset.messages ? dataEl.dataset.messages.replace(/'/g, '"') : '[]';
        const messages = JSON.parse(rawMessages);

        if (!Array.isArray(messages)) {
            console.error("[Toast] Parsing succeeded but the structure is not a valid array.");
            return;
        }

        messages.forEach(msg => {
            // Defensive check to ensure the global toast function is available
            if (typeof window.showToast === 'function') {
                window.showToast(msg.text, msg.tags);
            } else {
                console.error(`[Toast] window.showToast is not defined. Failed to render message: "${msg.text}"`);
            }
        });

    } catch (error) {
        console.error("[Toast] Failed to parse messages dataset from Django template:", error);
    }
}