import { Grid, h } from "gridjs";
import "gridjs/dist/theme/mermaid.css";

const erpFormatters = {
    image: (cell) => cell 
        ? h('img', { src: cell, class: 'w-10 h-10 object-contain rounded-md border border-gray-200' }) 
        : h('span', { class: 'text-gray-400 italic' }, '-'),
        
    status: (cell) => {
        const isActive = cell === "Kích hoạt" || cell === true || String(cell).toLowerCase() === "active";
        const colorClass = isActive ? "text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400" : "text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400";
        return h('span', { class: `px-2 py-1 text-xs font-medium rounded-full ${colorClass}` }, isActive ? "Kích hoạt" : "Ngừng kích hoạt");
    },
    
    actions: (cell) => {
        if (!cell || !cell.uuid || !cell.app) return null;
        return h('div', { class: 'flex gap-2' }, [
            h('a', { 
                href: `/${cell.app}/${cell.uuid}/detail/`, 
                class: 'px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 dark:bg-slate-800 dark:text-blue-400' 
            }, 'Chi tiết'),
            h('a', { 
                href: `/${cell.app}/${cell.uuid}/update/`, 
                class: 'px-3 py-1.5 text-xs font-medium text-amber-600 bg-amber-50 rounded-md hover:bg-amber-100 dark:bg-slate-800 dark:text-amber-400' 
            }, 'Sửa'),
            h('button', { 
                class: 'px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 dark:bg-slate-800 dark:text-red-400',
                onClick: () => {
                    const event = new CustomEvent(`open-delete-${cell.app}-modal`, { detail: { uuid: cell.uuid } });
                    window.dispatchEvent(event);
                }
            }, 'Xóa')
        ]);
    }
};

export default function initGridTable() {
    const tableContainers = document.querySelectorAll('.django-grid-table-container');
    
    tableContainers.forEach(wrapper => {
        const appNamespace = wrapper.getAttribute('data-app');
        if (!appNamespace || !window[appNamespace]) return;

        const rawColumns = window[appNamespace].columnJson || [];
        const rawData = window[appNamespace].dataJson || [];

        const resolvedColumns = rawColumns.map(col => {
            const baseCol = { ...col };
            
            if (baseCol.type && erpFormatters[baseCol.type]) {
                baseCol.formatter = erpFormatters[baseCol.type];
            }
            
            return baseCol;
        });

        const baseConfig = {
            columns: resolvedColumns,
            data: rawData,
            search: true,
            sort: true,
            resizable: false,
            fixedHeader: true,
            pagination: {
                limit: 15
            },
            className: {
                container: 'shadow-none django-grid-table',
                table: 'min-w-full table-layout-auto divide-y divide-gray-200 dark:divide-slate-800',
                thead: 'bg-gray-50/70 dark:bg-slate-800/50',
                th: 'px-6 py-3.5 text-start text-xs font-bold uppercase text-gray-400 tracking-wider',
                tbody: 'divide-y divide-gray-200 dark:divide-slate-800',
                td: 'px-6 py-3.5 text-start text-xs text-gray-500 dark:text-slate-400 font-medium'
            },
            language: {
                search: { placeholder: 'Tìm kiếm nhanh...' },
                pagination: {
                    previous: 'Trước',
                    next: 'Tiếp',
                    showing: 'Hiển thị',
                    to: 'đến',
                    of: 'trên',
                    results: 'kết quả'
                }
            }
        };

        const grid = new Grid(baseConfig);
        grid.render(wrapper);
    });
}