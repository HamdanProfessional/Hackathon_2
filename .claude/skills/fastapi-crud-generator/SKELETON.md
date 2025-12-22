# FastAPI CRUD Generator Skill

Generate complete CRUD operations for SQLModel models with FastAPI.

## When to Use This Skill

Use this skill when you need to:
- Create new database models with SQLModel
- Generate full CRUD API endpoints for a model
- Add database migrations for new tables
- Create Pydantic schemas for request/response validation

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `model_name` | string | Yes | Name of the model (e.g., "Task", "User") |
| `fields` | array | Yes | Array of field definitions |
| `relationships` | array | No | Optional relationships to other models |

## Field Definition

Each field should have:
```json
{
  "name": "title",
  "type": "string",
  "required": true,
  "index": true
}
```

Supported types: `string`, `integer`, `boolean`, `float`, `datetime`, `text`

## Generated Files

1. **Model**: `backend/app/models/{model_lower}.py`
2. **Schema**: `backend/app/schemas/{model_lower}_schema.py`
3. **Router**: `backend/app/api/routes/{model_lower}.py`
4. **Migration**: `backend/alembic/versions/{version}_{model_lower}.py`

## Example Usage

```
@skill fastapi-crud-generator
model_name: Task
fields:
  - name: title
    type: string
    required: true
  - name: description
    type: text
    required: false
  - name: completed
    type: boolean
    required: false
    default: false
  - name: priority
    type: string
    required: false
    default: "medium"
```

## Output

- Complete SQLModel with relationships
- Pydantic schemas (Create, Update, Response)
- FastAPI router with all CRUD endpoints
- Alembic migration script
- Type hints and docstrings

## Generated Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{resource}` | List all items |
| POST | `/api/{resource}` | Create new item |
| GET | `/api/{resource}/{id}` | Get single item |
| PUT | `/api/{resource}/{id}` | Update item |
| DELETE | `/api/{resource}/{id}` | Delete item |
