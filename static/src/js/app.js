import '../css/input.css';

import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'

Alpine.plugin(persist)

window.Alpine = Alpine

Alpine.start()

// Notyf
import { showToast } from './components/notyf';
window.showToast = showToast;

// Backdrop
import initBackdrop from './components/backdrop';

document.addEventListener('DOMContentLoaded', () => {
    // Backdrop
    initBackdrop();
});