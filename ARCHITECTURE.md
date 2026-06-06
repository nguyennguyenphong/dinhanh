# Tenants Module Architecture

## Introduction

The `tenants` module follows a layered architecture inspired by **Domain-Driven Design (DDD)**, **Clean Architecture**, and the **Repository Pattern**.

The primary goals of this architecture are:

* Separation of concerns
* High maintainability
* Scalability
* Testability
* Independence from frameworks and databases
* Clear business logic boundaries

Instead of placing all logic directly inside Django Views or Models, responsibilities are divided into dedicated layers.

---

# Directory Structure

```text
tenants/

├── services/
│
├── repositories/
│   ├── interfaces/
│   └── implement/
│
├── domain/
│   └── entities/
│
├── application/
│   ├── dtos/
│   └── usecases/
│
├── policies/
├── middleware/
├── tasks/
├── signals/
├── urls/
├── views/
├── tests/
├── templates/
├── commands/
├── providers/
├── serializers/
│
├── app.py
└── admin.py
```

---

# Architecture Layers

## 1. Domain Layer

Location:

```text
domain/entities/
```

The Domain Layer contains pure business objects.

These entities represent business concepts and rules without depending on Django, databases, APIs, or infrastructure.

Example:

```python
class TenantEntity:
    def __init__(
        self,
        id: int,
        code: str,
        name: str,
        domain: str
    ):
        self.id = id
        self.code = code
        self.name = name
        self.domain = domain
```

Responsibilities:

* Business rules
* Domain validation
* Business behavior
* Core domain concepts

Should NOT contain:

* Django ORM
* HTTP requests
* Database queries
* Framework-specific logic

---

## 2. Repository Layer

Location:

```text
repositories/
```

The Repository Layer abstracts data access.

### Repository Interface

Location:

```text
repositories/interfaces/
```

Defines contracts for data operations.

Example:

```python
from abc import ABC, abstractmethod

class TenantRepositoryInterface(ABC):

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def find_by_id(self, tenant_id):
        pass
```

### Repository Implementation

Location:

```text
repositories/implement/
```

Implements repository interfaces using Django ORM.

Example:

```python
class TenantRepository(
    TenantRepositoryInterface
):
    def find_all(self):
        return Tenant.objects.all()
```

Responsibilities:

* Database access
* ORM interaction
* Query optimization
* Data persistence

Benefits:

* Easy to swap database implementation
* Easier unit testing
* Decouples business logic from ORM

---

## 3. Application Layer

Location:

```text
application/
```

This layer coordinates business processes.

### DTOs

Location:

```text
application/dtos/
```

DTO (Data Transfer Object) is used to transport data between layers.

Example:

```python
@dataclass
class TenantCreateDTO:
    code: str
    name: str
    domain: str
```

Benefits:

* Clear contract between layers
* Avoid passing raw request objects
* Easier validation

---

### Use Cases

Location:

```text
application/usecases/
```

Use Cases contain application-specific business workflows.

Example:

```python
class CreateTenantUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        dto: TenantCreateDTO
    ):
        ...
```

Responsibilities:

* Execute business workflows
* Coordinate repositories
* Apply policies
* Return results

Examples:

```text
CreateTenantUseCase
UpdateTenantUseCase
DeleteTenantUseCase
GetTenantDetailUseCase
GetTenantListUseCase
```

---

## 4. Services Layer

Location:

```text
services/
```

Services contain reusable business operations shared across multiple use cases.

Example:

```python
class TenantDomainService:

    def generate_code(self):
        ...
```

Responsibilities:

* Complex business operations
* Cross-use-case functionality
* Shared business logic

Use services when logic is reused in multiple places.

---

## 5. Policies Layer

Location:

```text
policies/
```

Policies define authorization rules.

Example:

```python
class TenantPolicy:

    def can_update(
        self,
        user,
        tenant
    ):
        return user.is_superuser
```

Responsibilities:

* Authorization
* Permission checks
* Access control

Benefits:

* Keeps permissions outside views
* Easier maintenance

---

## 6. Providers Layer

Location:

```text
providers/
```

Providers integrate external services.

Examples:

```text
EmailProvider
SMSProvider
StorageProvider
PaymentProvider
```

Responsibilities:

* Third-party APIs
* Cloud services
* External integrations

---

## 7. Serializers Layer

Location:

```text
serializers/
```

Handles request validation and transformation.

Responsibilities:

* Input validation
* Request normalization
* API payload validation

Example:

```python
class TenantCreateSerializer(
    serializers.Serializer
):
    code = serializers.CharField()
    name = serializers.CharField()
```

---

## 8. Views Layer

Location:

```text
views/
```

Views are responsible only for handling HTTP requests and responses.

Responsibilities:

* Receive requests
* Validate input
* Execute use cases
* Return response

Example Flow:

```python
class TenantCreateView(View):

    def post(self, request):

        serializer = TenantCreateSerializer(
            data=request.POST
        )

        serializer.is_valid(
            raise_exception=True
        )

        dto = TenantCreateDTO(
            **serializer.validated_data
        )

        use_case = CreateTenantUseCase()

        result = use_case.execute(dto)

        return JsonResponse(result)
```

Views should remain thin and contain minimal business logic.

---

## 9. Middleware Layer

Location:

```text
middleware/
```

Responsibilities:

* Tenant identification
* Request logging
* Security
* Request preprocessing

Examples:

```text
TenantMiddleware
RequestLogMiddleware
```

---

## 10. Tasks Layer

Location:

```text
tasks/
```

Contains asynchronous background jobs.

Examples:

```text
SendWelcomeEmailTask
SyncTenantTask
```

Typically executed using:

* Celery
* Django Q
* RQ

---

## 11. Signals Layer

Location:

```text
signals/
```

Handles event-driven actions.

Example:

```python
tenant_created
tenant_updated
tenant_deleted
```

Responsibilities:

* Decouple side effects
* Trigger notifications
* Trigger background tasks

---

## 12. Commands Layer

Location:

```text
commands/
```

Contains Django custom management commands.

Example:

```bash
python manage.py sync_tenants
```

Responsibilities:

* Data migration
* Batch processing
* Scheduled operations

---

## 13. Templates Layer

Location:

```text
templates/
```

Contains HTML templates for rendering views.

Responsibilities:

* Presentation only
* No business logic

---

## 14. Tests Layer

Location:

```text
tests/
```

Test structure:

```text
tests/
├── repositories/
├── usecases/
├── services/
├── views/
└── policies/
```

Responsibilities:

* Unit testing
* Integration testing
* Feature testing

---

# Request Lifecycle

The complete request flow is:

```text
HTTP Request
        │
        ▼
Serializer
        │
        ▼
DTO
        │
        ▼
View
        │
        ▼
Use Case
        │
        ▼
Policy Check
        │
        ▼
Service
        │
        ▼
Repository Interface
        │
        ▼
Repository Implementation
        │
        ▼
Database
```

Response Flow:

```text
Database
    │
    ▼
Repository
    │
    ▼
Use Case
    │
    ▼
View
    │
    ▼
HTTP Response
```

---

# Architectural Principles

### Dependency Direction

```text
View
 ↓
Use Case
 ↓
Repository Interface
 ↓
Repository Implementation
```

Upper layers must never depend directly on lower-level infrastructure.

---

### Single Responsibility Principle

Each layer should have one clear responsibility.

Examples:

| Layer      | Responsibility |
| ---------- | -------------- |
| View       | HTTP           |
| Serializer | Validation     |
| DTO        | Data Transfer  |
| Use Case   | Business Flow  |
| Service    | Shared Logic   |
| Policy     | Authorization  |
| Repository | Data Access    |
| Entity     | Domain Rules   |

---

# Benefits

This architecture provides:

* Clear separation of concerns
* Better maintainability
* Easier testing
* Scalability for large projects
* Framework-independent business logic
* Cleaner code organization
* Improved developer experience

It is particularly suitable for medium to large Django applications where business logic grows beyond simple CRUD operations.
