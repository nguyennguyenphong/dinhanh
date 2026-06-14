// static/src/js/components/notyf.js
import { Notyf } from 'notyf';
import 'notyf/notyf.min.css';

const notyf = new Notyf({
    duration: 3000,
    position: { x: 'right', y: 'top' },
    dismissible: true,
    types: [
        {
            type: 'success',
            background: '#32c832',
            icon: {
                className: 'notyf__icon--success',
                tagName: 'i'
            }
        },
        {
            type: 'error',
            background: '#ff3333',
            icon: {
                className: 'notyf__icon--error',
                tagName: 'i'
            }
        },
        {
            type: 'warning',
            background: '#ffc107',
            icon: {
                className: 'notyf__icon--warning',
                tagName: 'i'
            }
        },
        {
            type: 'info',
            background: '#17a2b8',
            icon: {
                className: 'notyf__icon--info',
                tagName: 'i',
                text: 'i'
            }
        }
    ]
});

export const showToast = (message, type = 'success') => {
    notyf.open({
        type: type,
        message: message,
    });
};