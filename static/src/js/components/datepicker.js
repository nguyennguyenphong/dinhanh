class DatePicker {
    constructor(element) {
        if (!element) return;
        this.input = element;
        this.init();
    }

    init() {
        const mode = this.input.dataset.mode || 'single';
        const minDate = this.input.dataset.minDate || null;
        const maxDate = this.input.dataset.maxDate || null;
        const enableTime = this.input.dataset.enableTime === 'true';
        const disableWeekends = this.input.dataset.disableWeekends === 'true';
        
        const customInputClasses = this.input.dataset.inputClass || '';
        
        let disableDates = [];
        try {
            disableDates = JSON.parse(this.input.dataset.disableDates || '[]');
        } catch (e) {
            console.error("Error parsing disable-dates array:", e);
        }

        const disableConfig = [];
        if (disableDates.length > 0) {
            disableConfig.push(...disableDates);
        }
        
        if (disableWeekends) {
            disableConfig.push(function(date) {
                return (date.getDay() === 0 || date.getDay() === 6);
            });
        }

        this.fp = flatpickr(this.input, {
            mode: mode,
            minDate: minDate === 'today' ? 'today' : minDate,
            maxDate: maxDate,
            enableTime: enableTime,
            noCalendar: false,
            dateFormat: enableTime ? "Y-m-d H:i" : "Y-m-d", 
            altInput: true,
            altFormat: enableTime ? "m/d/Y H:i" : "m/d/Y",
            
            altInputClass: customInputClasses, 
            
            disable: disableConfig,
            closeOnSelect: mode === 'single', 
            
            onOpen: (selectedDates, dateStr, instance) => {
                instance.calendarContainer.classList.add(
                    'dark:bg-slate-900', 
                    'dark:border-slate-800', 
                    'shadow-xl', 
                    'rounded-lg', 
                    'border-[1.5px]', 
                    'border-gray-100'
                );
            }
        });
    }

    destroy() {
        if (this.fp) this.fp.destroy();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const datepickerElements = document.querySelectorAll('[data-cms-datepicker]');
    datepickerElements.forEach(el => new DatePicker(el));
});