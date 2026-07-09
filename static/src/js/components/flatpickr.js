import flatpickr from 'flatpickr';
import { Vietnamese } from 'flatpickr/dist/l10n/vn.js';

const PICKER_CONFIG = {
    locale: Vietnamese,
    allowInput: true,
    altInput: true,
    altFormat: "d/m/Y",
    dateFormat: "Y-m-d",
    clickOpens: true,
    animate: false,
    monthSelectorType: "dropdown",
    yearSelectorType: "dropdown",
    onReady: function(selectedDates, dateStr, instance) {
        instance.altInput.classList.add('form-control');
        instance.altInput.setAttribute('autocomplete', 'off');
        instance.altInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                instance.close();
            }
        });
    },
    onOpen: function(selectedDates, dateStr, instance) {
        if (!instance.isOpen && instance.altInput.value === '') {
            instance.setDate(new Date(), false);
        }
    }
};

const initDatePicker = (selector = '.flatpickr-input') => {
    const elements = document.querySelectorAll(selector);
    const instances = [];
    
    elements.forEach(element => {
        if (element._flatpickr) {
            element._flatpickr.destroy();
        }
        
        const isDateTime = element.classList.contains('datetime-picker') || element.dataset.type === 'datetime';
        const isTimeOnly = element.classList.contains('time-picker') || element.dataset.type === 'time';
        
        let customConfig = { ...PICKER_CONFIG };
        
        if (isDateTime) {
            customConfig.enableTime = true;
            customConfig.time_24hr = true;
            customConfig.altFormat = "d/m/Y H:i";
            customConfig.dateFormat = "Y-m-d H:i:s";
        } else if (isTimeOnly) {
            customConfig.enableTime = true;
            customConfig.noCalendar = true;
            customConfig.time_24hr = true;
            customConfig.altFormat = "H:i";
            customConfig.dateFormat = "H:i:s";
        }
        
        const instance = flatpickr(element, customConfig);
        instances.push(instance);
    });
    
    return instances;
};

export default initDatePicker;
