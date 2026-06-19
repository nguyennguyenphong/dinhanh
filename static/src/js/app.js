import '../css/input.css';

// Flowbite
import 'flowbite';
import { initFlowbite } from 'flowbite';

// Alpine
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
// Spinner
import { initSpinner } from './components/spinner';
// Toast
import { initToast } from './components/toast';
// Gridjs
import autoInitDjangoAgGrid from "./components/djangoAgGrid";

document.addEventListener('DOMContentLoaded', () => {
    // Flowbite
    initFlowbite();
    // Backdrop
    initBackdrop();
    // Spinner
    initSpinner();
    // Toast
    initToast();
    //Gridjs
    autoInitDjangoAgGrid();
});