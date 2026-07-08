# Implementation Checklist - AssetCategory & StorageUnit CRUD

- [x] Implement DTOs & UseCases
  - [x] `AssetCategory` DTOS & UseCases (Create, Update, Delete, List, Detail)
  - [x] `StorageUnit` DTOs & UseCases (Create, Update, Delete, List, Detail)
- [x] Implement Forms
  - [x] `StorageUnitBaseForm` in `assets/views/forms/storage_unit_base_form.py`
- [x] Implement Services & Providers updates
  - [x] Add `create_category`, `update_category`, `delete_category` to `AssetService`
  - [x] Add `create_storage_unit`, `update_storage_unit`, `delete_storage_unit` to `AssetService`
  - [x] Register new use cases in `AssetProvider`
- [x] Implement Views
  - [x] Views for `AssetCategory` CRUD & Grid API
  - [x] Views for `StorageUnit` CRUD & Grid API
- [x] Implement URLs
  - [x] Register routes in `assets/urls/asset_categories/urls.py`
  - [x] Register routes in `assets/urls/storage_units/urls.py`
- [x] Implement UI Templates
  - [x] Pages for `AssetCategory` CRUD and components
  - [x] Pages for `StorageUnit` CRUD and components
