---
name: magento-service-contracts
description: >
  Implement Magento 2 service contracts — repository interfaces, data
  interfaces, SearchCriteria, and the repository pattern. Use when building
  module APIs, data access layers, or integrating with Magento's Web API.
---

# Magento 2 Service Contracts & Repositories

## Before writing code

**Fetch live docs**:
1. Fetch `https://developer.adobe.com/commerce/php/development/components/web-api/services/` for service contract guide
2. Fetch `https://developer.adobe.com/commerce/php/development/components/searching-with-repositories/` for SearchCriteria patterns
3. Web-search `site:developer.adobe.com commerce php development components service-contracts` for additional reference

## Conceptual Architecture

### What Service Contracts Are

Service contracts are **PHP interfaces** that define a module's public API. They guarantee backward compatibility — implementations can change across versions without breaking consumers.

### Three Interface Categories

1. **Repository Interfaces** (`Api/SomeRepositoryInterface.php`)
   - `getById($id)` — retrieve single entity
   - `save(SomeInterface $entity)` — create or update
   - `delete(SomeInterface $entity)` — remove
   - `getList(SearchCriteriaInterface $criteria)` — filtered/sorted/paginated results

2. **Data Interfaces** (`Api/Data/SomeInterface.php`)
   - Define getters and setters for entity fields
   - `getId()`, `setId($id)`, `getName()`, `setName($name)`, etc.
   - Constants for field names: `const NAME = 'name';`

3. **SearchResults Interface** (`Api/Data/SomeSearchResultsInterface.php`)
   - Extends `Magento\Framework\Api\SearchResultsInterface`
   - Wraps `getItems()` / `setItems()` with typed returns

### SearchCriteria Pattern

Used for querying repositories with filters, sorting, and pagination:

- **SearchCriteriaBuilder** — fluent builder for criteria
- **FilterBuilder** — builds individual filter conditions
- **FilterGroupBuilder** — groups filters with AND/OR logic
- **SortOrderBuilder** — defines sort order
- **CollectionProcessorInterface** — applies criteria to collections

### Filter Logic

- Filters within a **FilterGroup** are OR'd together
- **FilterGroups** are AND'd together
- Condition types: `eq`, `neq`, `gt`, `gteq`, `lt`, `lteq`, `like`, `in`, `nin`, `notnull`, `null`, `from`, `to`

### Repository Implementation Pattern

The concrete repository class:
1. Injects: Model Factory, Resource Model, Collection Factory, SearchResultsFactory, CollectionProcessor
2. `getById()` — creates model via factory, loads via resource model
3. `save()` — calls resource model `save()`, handles exceptions
4. `delete()` — calls resource model `delete()`
5. `getList()` — creates collection, applies criteria via CollectionProcessor, wraps in SearchResults

### Service Contracts as Web API

When you define a service contract interface and map it in `webapi.xml`, the same code serves:
- REST API endpoints
- SOAP API endpoints
- Internal PHP calls

### Best Practices

- Always define data interfaces — don't expose models directly
- Use typed return types and parameter types on all interface methods
- Add `@api` annotation to indicate public API stability
- Use `SearchCriteriaBuilder` instead of raw collection filtering in service layer
- Throw specific exceptions: `NoSuchEntityException`, `CouldNotSaveException`, `CouldNotDeleteException`
- Map service contracts in `webapi.xml` for automatic REST/SOAP exposure

Fetch the service contracts and searching-with-repositories docs for exact interface signatures, exception classes, and CollectionProcessor usage before implementing.
