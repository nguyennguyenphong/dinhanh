import { createGrid, ModuleRegistry, AllCommunityModule, themeQuartz } from 'ag-grid-community';

ModuleRegistry.registerModules([ AllCommunityModule ]);

const erpRenderers = {
    image: (params) => {
        if (!params.value) return '<span class="text-gray-400 italic">-</span>';
        return `<div class="flex items-center h-full"><img src="${params.value}" class="w-10 h-10 object-contain rounded-md border border-gray-200 bg-white"></div>`;
    },
    
    status: (params) => {
        let isActive = false;

        const val = typeof params.value === 'string' ? params.value.toLowerCase() : params.value;

        switch (true) {
            case val === "kích hoạt":
            case val === true:
            case val === "active":
            case val === "in_use":
                isActive = true;
                break;
            default:
                isActive = false;
        }

        const colorClass = isActive 
            ? "text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400" 
            : "text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400";

        return `<div class="flex items-center h-full"><span class="px-2 py-1 text-xs font-medium rounded-full ${colorClass}">${isActive ? "Kích hoạt" : "Ngừng kích hoạt"}</span></div>`;
    },
    
    datetime: (params) => {
        if (!params.value) return '<span class="text-gray-400 italic">-</span>';
        try {
            const date = new Date(params.value);
            return `<span class="font-medium text-gray-700 dark:text-slate-300">${date.toLocaleString('vi-VN')}</span>`;
        } catch (e) {
            return params.value;
        }
    },
    
    actions: (params) => {
        const app = params.app || 'tenants';
        const key = params.key || 'uuid';
        const val = params.data ? params.data[key] : null;
        const name = params.data ? (params.data.name || params.data.label || params.data.uuid || '') : '';
        if (!val) return '';
            
        return `
            <div class="flex gap-2 items-center h-full">
                <a href="/${app}/detail/${val}/"
                   class="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-md dark:bg-slate-800 dark:text-blue-400">
                    Chi tiết
                </a>

                <a href="/${app}/update/${val}/"
                   class="px-3 py-1.5 text-xs font-medium text-amber-600 bg-amber-50 hover:bg-amber-100 rounded-md dark:bg-slate-800 dark:text-amber-400">
                    Sửa
                </a>

                <button onclick="window.dispatchEvent(new CustomEvent('open-delete-${app}-modal', { detail: { uuid: '${val}', name: '${name}' } }))"
                        class="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md dark:bg-slate-800 dark:text-red-400 cursor-pointer">
                    Xóa
                </button>
            </div>
        `;
    }
};

export default function initAgGrid() {
    const gridContainers = document.querySelectorAll('.django-ag-grid-container');
    
    gridContainers.forEach(wrapper => {
        const apiEndpoint = wrapper.getAttribute('data-endpoint');
        const rawColumns = JSON.parse(wrapper.getAttribute('data-columns') || '[]');
        const options = JSON.parse(wrapper.getAttribute('data-options') || '{}');
        const searchInputId = wrapper.getAttribute('data-search-input');
        const searchInput = searchInputId ? document.getElementById(searchInputId) : null;

        // Map column configurations
        const columnDefs = rawColumns.map(col => {
            const agCol = {
                headerName: col.headerName,
                field: col.field,
                hide: col.hide || false,
                sortable: col.sortable !== undefined ? col.sortable : true,
                filter: col.filter !== undefined ? col.filter : true,
                resizable: true
            };

            if (col.width) {
                agCol.width = parseInt(col.width);
            }

            if (col.cellRendererParams) {
                agCol.cellRendererParams = col.cellRendererParams;
            }

            if (col.type && erpRenderers[col.type]) {
                agCol.cellRenderer = erpRenderers[col.type];
            }

            return agCol;
        });

        // Quartz theme customization
        const customErpTheme = themeQuartz.withParams({
            spacing: 12,
            accentColor: '#3b82f6',
            borderColor: '#e5e7eb',
            headerBackgroundColor: '#f9fafb',
            rowBorder: true
        });

        const pageSize = options.pageSize || 50;

        // Base grid configuration
        const gridOptions = {
            theme: customErpTheme,
            columnDefs: columnDefs,
            rowModelType: apiEndpoint ? 'infinite' : 'clientSide',
            pagination: true,
            paginationPageSize: pageSize,
            paginationPageSizeSelector: [15, 30, 50, 100],
            rowHeight: options.rowHeight || 52,
            headerHeight: options.headerHeight || 48,
            onFirstDataRendered: (params) => {
                const allColumnIds = params.api.getAllGridColumns().map(col => col.getColId());
                params.api.autoSizeColumns(allColumnIds, false);
            }
        };

        let grid;

        if (apiEndpoint) {
            // Setup datasource for Infinite Row Model
            const datasource = {
                getRows: (params) => {
                    const start = params.startRow;
                    const end = params.endRow;
                    const limit = end - start;
                    const offset = start;

                    // Parse sorting
                    let ordering = '';
                    if (params.sortModel && params.sortModel.length > 0) {
                        const sort = params.sortModel[0];
                        ordering = sort.sort === 'desc' ? `-${sort.colId}` : sort.colId;
                    }

                    // Parse search term
                    let search = '';
                    if (searchInput) {
                        search = searchInput.value;
                    }

                    const url = new URL(apiEndpoint, window.location.origin);
                    url.searchParams.set('limit', limit);
                    url.searchParams.set('offset', offset);
                    if (ordering) {
                        url.searchParams.set('ordering', ordering);
                    }
                    if (search) {
                        url.searchParams.set('search', search);
                    }

                    fetch(url)
                        .then(res => {
                            if (!res.ok) throw new Error('Network response was not ok');
                            return res.json();
                        })
                        .then(data => {
                            // Map row indexes (STT) on the client side
                            const rows = (data.results || []).map((row, index) => ({
                                ...row,
                                idx: offset + index + 1
                            }));
                            params.successCallback(rows, data.total || 0);
                        })
                        .catch(err => {
                            console.error('Error fetching ag-grid data:', err);
                            params.failCallback();
                        });
                }
            };

            gridOptions.datasource = datasource;
            grid = createGrid(wrapper, gridOptions);

            // Set up search debounce
            if (searchInput) {
                let searchTimeout;
                searchInput.addEventListener('input', () => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {
                        grid.setGridOption('datasource', datasource);
                    }, 300);
                });
            }
        } else {
            // Standard client-side fallback
            gridOptions.rowData = options.rowData || [];
            grid = createGrid(wrapper, gridOptions);

            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    grid.setGridOption('quickFilterText', e.target.value);
                });
            }
        }
    });
}