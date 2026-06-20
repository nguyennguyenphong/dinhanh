import json


class DjangoGridColumn:
    """
    Represents a single AG Grid column definition.
    """

    def __init__(
        self,
        field,
        header_name,
        col_type="text",
        width=None,
        sortable=True,
        filter=True,
        hidden=False,
        cell_renderer_params=None,
    ):
        self.field = field
        self.header_name = header_name
        self.col_type = col_type
        self.width = width
        self.sortable = sortable
        self.filter = filter
        self.hidden = hidden
        self.cell_renderer_params = cell_renderer_params or {}

    def to_dict(self):
        res = {
            "field": self.field,
            "headerName": self.header_name,
            "type": self.col_type,
            "sortable": self.sortable,
            "filter": self.filter,
            "hide": self.hidden,
        }
        if self.width is not None:
            res["width"] = self.width
        if self.cell_renderer_params:
            res["cellRendererParams"] = self.cell_renderer_params
        return res


class DjangoGridBuilder:
    """
    Builder helper to generate grid column configurations and options.
    """

    def __init__(self, grid_id, api_url, page_size=50, options=None):
        self.grid_id = grid_id
        self.api_url = api_url
        self.page_size = page_size
        self.columns = []
        self.options = options or {}

    def add_column(
        self,
        field,
        header_name,
        col_type="text",
        width=None,
        sortable=True,
        filter=True,
        hidden=False,
        cell_renderer_params=None,
    ):
        column = DjangoGridColumn(
            field=field,
            header_name=header_name,
            col_type=col_type,
            width=width,
            sortable=sortable,
            filter=filter,
            hidden=hidden,
            cell_renderer_params=cell_renderer_params,
        )
        self.columns.append(column)
        return self

    def get_columns_json(self):
        return json.dumps([c.to_dict() for c in self.columns])

    def get_options_json(self):
        opts = {"pageSize": self.page_size, **self.options}
        return json.dumps(opts)
