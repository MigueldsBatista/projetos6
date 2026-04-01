# Domain-Driven Django Architecture Guide

This guide outlines a pragmatic approach to building scalable Django applications using Domain-Driven Design (DDD) principles. It treats Django "apps" as "software domains" with strong bounded contexts.

## 1. Architectural Division

Instead of the standard Django MTV (Model-Template-View) pattern, each domain (app) is divided into four primary layers:

### 📂 `models.py` (The Data Layer)
- **Role**: Defines data structure and simple informational logic.
- **Rule**: Keep them **skinny**. No complex business logic.
- **Constraints**: 
    - No imports from `services.py`, `apis.py`, or `interfaces.py`.
    - No ForeignKeys across domains (use UUID fields instead).
    - Owns simple computed properties (e.g., `full_name`).

### 📂 `services.py` (The Logic Layer)
- **Role**: Coordination and transactional logic. This is where the "business" happens.
- **Responsibility**: Orchestrating updates across multiple models or dispatching actions to other domains.
- **Style**: Prefers stateless functions (can be grouped in a class like `BookService`).

### 📂 `apis.py` (The Presentation Layer)
- **Role**: Public entry points and presentation logic. Replaces `views.py`.
- **Function**: Defines the API schema (REST via DRF, GraphQL via Graphene, or internal Python APIs).
- **DRF Integration**: 
    - This is the home for **ViewSets** and **APIViews**.
    - If complexity grows, use a directory: `apis/rest.py` and `apis/graphql.py`.
- **Rule**: Must talk to `services.py` to get or modify data. **Never** talk to `models.py` directly.

### 📂 `serializers.py` (The Schema Layer - Optional)
- **Role**: Definition of data shapes and basic validation.
- **Placement**: Usually lives alongside `apis.py` in the domain.
- **Function**: Serializers transform Model instances (or Service dicts) into JSON and validate incoming request data.

### 📂 `interfaces.py` (The Integration Layer)
- **Role**: Bounded context/Anti-Corruption Layer.
- **Function**: All communication with *other* domains or external services goes here.
- **Benefit**: If an external domain moves to a separate microservice, you only update this file.

---

## 2. Handling the Architecture

### Imports
- **Use always** absolute imports for internal or other domains or 3rd party packages.
- **Flow**: `Consumer -> apis.py -> services.py -> models.py`.
- **Cross-Domain Flow**: `Domain A Service -> Domain A Interface -> Domain B API`.

### Data Transfer
- APIs should return serializable data (dicts, lists) rather than raw Django Model instances to maintain decoupling.

---

## 3. How to Scale

### Vertical Scaling (Complexity)
If a domain becomes too large (typically when more than 4-6 developers are working on it simultaneously), split it.
1. Identify a sub-domain.
2. Create a new Django app.
3. Move relevant logic.
4. Update `interfaces.py` in the original domain to point to the new one.

### Horizontal Scaling (Deployment)
Because domains are decoupled via `interfaces.py` and avoid hard database constraints (ForeignKeys) across apps, they are "microservice-ready". You can move a domain to a separate repository/server with minimal changes to the rest of the monolith.

---

## 4. Introducing "Views"

In this architecture, **`views.py` is explicitly disallowed**. 

### How to handle "View" logic:
1. **API Views**: Use `apis.py` to define DRF `APIView` or Graphene `Mutation/Query`.
2. **Template Rendering**: If you *must* use server-side rendering (Django Templates):
    - Create a `web_apis.py` or similar.
    - Treat the Template as just another "presentation" layer.
    - The "View" function should still call a `Service` to get data and only handle the `render()` call.
3. **Validation**: Serializers (DRF) or Form classes can be placed in `serializers.py` or `forms.py` and are called by the `apis.py` layer.

---

## 6. Integrating Django Rest Framework (DRF)

When using DRF with this architecture, the goal is to prevent the "fat serializer" or "fat viewset" anti-patterns.

### Where components live:
- **ViewSets/Views**: Always in `apis.py` (or `apis/rest.py`).
- **Serializers**: In `serializers.py` (preferred) or `apis.py`.
- **URLs**: Standard Django `urls.py` in the domain, pointing to the ViewSets in `apis.py`.

### The "Service-First" ViewSet Pattern
To maintain the architecture, **avoid** using `ModelViewSet` with the default `queryset` and `serializer_class` if it performs direct DB operations. Instead, override the methods to call your Services.

**Example `apis.py` with DRF:**
```python
from rest_framework import viewsets, response, status
from core.serializers import BookSerializer
from core.services import BookService

class BookViewSet(viewsets.ViewSet):
    def list(self, request):
        # Call service instead of Model.objects.all()
        books_data = BookService.get_all_books()
        return response.Response(books_data)

    def create(self, request):
        serializer = BookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Pass validated data to the service
        book = BookService.create_book(**serializer.validated_data)
        return response.Response(book, status=status.HTTP_201_CREATED)
```

### Serializers and Validation
- **Input Serializers**: Use them for initial data type validation (e.g., ensuring a field is an integer or email).
- **Output Serializers**: Use them to shape the data returned by your Services before it reaches the consumer.
- **Business Validation**: Logic like "Can this user borrow this book?" belongs in **`services.py`**, not in the serializer's `validate()` method.

### Why this way?
By forcing ViewSets to call Services, you ensure that if you ever need to perform the same action via a Management Command, a Celery Task, or a GraphQL Mutation, the business logic is reusable and centralized in `services.py`.

---

## 5. Applying to New Projects

1. **Scaffold**: Create a standard Django app.
2. **Delete**: (Optional) Remove `views.py` to enforce the pattern.
3. **Create**: Add `services.py`, `interfaces.py`, `apis.py`, and `serializers.py`.
4. **Implement**:
    - Define models in `models.py` (remember: no cross-app FKs).
    - Write business logic in `services.py`.
    - Expose functionality in `apis.py` (using ViewSets or APIViews).
    - Bridge to other apps in `interfaces.py`.
5. **Standardize**: Use keyword arguments and type hints for all functions in `apis`, `services`, and `interfaces`.
