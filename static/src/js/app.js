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
import initAgGrid from "./components/aggrid";
// 404 Error
import init404Error from "./errors/404";
window.init404Error = init404Error;
// Flatpickr
import initDatePicker from "./components/flatpickr";
// Sesstion Timeout
import "./utils/session_timeout";

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
    initAgGrid();
    // Flatpickr
    initDatePicker();
});