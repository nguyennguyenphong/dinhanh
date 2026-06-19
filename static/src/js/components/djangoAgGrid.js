import { createGrid, ModuleRegistry, AllCommunityModule, themeQuartz } from 'ag-grid-community';

ModuleRegistry.registerModules([ AllCommunityModule ]);

const erpRenderers = {
    image: (params) => {
        if (!params.value) return '<span class="text-gray-400 italic">-</span>';
        return `<img src="${params.value}" class="w-10 h-10 object-contain rounded-md border border-gray-200">`;
    },
    
    status: (params) => {
        const isActive = params.value === "Kích hoạt" || params.value === true || String(params.value).toLowerCase() === "active";
        const colorClass = isActive ? "text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400" : "text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400";
        return `<span class="px-2 py-1 text-xs font-medium rounded-full ${colorClass}">${isActive ? "Kích hoạt" : "Ngừng kích hoạt"}</span>`;
    },
    
    actions: (params) => {
        const cell = params.value;
        if (!cell || !cell.uuid || !cell.app) return '';
        
        if (!window.handleGridDelete) {
            window.handleGridDelete = (app, uuid) => {
                const event = new CustomEvent(`open-delete-${app}-modal`, { detail: { uuid } });
                window.dispatchEvent(event);
            };
        }

        return `
            <div class="flex gap-2 items-center h-full">
                <a href="/${cell.app}/${cell.uuid}/detail/" class="px-3 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 dark:bg-slate-800 dark:text-blue-400">Chi tiết</a>
                <a href="/${cell.app}/${cell.uuid}/update/" class="px-3 py-1 text-xs font-medium text-amber-600 bg-amber-50 rounded-md hover:bg-amber-100 dark:bg-slate-800 dark:text-amber-400">Sửa</a>
                <button onclick="handleGridDelete('${cell.app}', '${cell.uuid}')" class="px-3 py-1 text-xs font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 dark:bg-slate-800 dark:text-red-400">Xóa</button>
            </div>
        `;
    }
};

export default function autoInitDjangoAgGrid() {
    const gridContainers = document.querySelectorAll('.django-ag-grid-container');
    
    gridContainers.forEach(wrapper => {
        const appNamespace = wrapper.getAttribute('data-app');
        if (!appNamespace || !window[appNamespace]) return;

        const rawColumns = window[appNamespace].columnJson || [];
        const rawData = window[appNamespace].dataJson || [];

        const columnDefs = rawColumns.map((col, index) => {
            const agCol = {
                headerName: col.name,
                field: String(index), 
                hide: col.hidden || false,
                sortable: true,
                filter: true,
                resizable: true
            };

            if (col.width) {
                agCol.width = parseInt(col.width);
            }

            if (col.type && erpRenderers[col.type]) {
                agCol.cellRenderer = erpRenderers[col.type];
            }

            return agCol;
        });

        // Tùy biến themeQuartz để xóa bỏ hoàn toàn shadow và tùy chỉnh màu sắc tiệp với Tailwind CSS thông qua Theming API mới
        const customErpTheme = themeQuartz.withParams({
            spacing: 12,
            accentColor: '#3b82f6',
            borderColor: '#e5e7eb',
            headerBackgroundColor: '#f9fafb',
            rowBorder: true
        });

        const gridOptions = {
            // Khai báo theme mới trực tiếp trong cấu hình thay vì import file css bên ngoài
            theme: customErpTheme,
            columnDefs: columnDefs,
            domLayout: 'autoHeight',
            rowData: rawData,
            pagination: true,
            paginationPageSize: 15,
            paginationPageSizeSelector: [15, 30, 50, 100],
            rowHeight: 52,
            headerHeight: 48,
            onFirstDataRendered: (params) => {
                const allColumnIds = params.api.getAllGridColumns().map(col => col.getColId());
                params.api.autoSizeColumns(allColumnIds, false);
            }
        };

        const grid = createGrid(wrapper, gridOptions);
        
        const searchInput = document.getElementById(`${appNamespace}-grid-search`);
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                grid.setGridOption('quickFilterText', e.target.value);
            });
        }
    });
}