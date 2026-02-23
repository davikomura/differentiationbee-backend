# API Contract for Frontend

## Error payload (standardized)

All errors now use this shape:

```json
{
  "ok": false,
  "error": {
    "code": "http_400",
    "message": "Human readable message",
    "details": {}
  },
  "path": "/route/path"
}
```

Validation errors (`422`) use:

```json
{
  "ok": false,
  "error": {
    "code": "validation_error",
    "message": "Invalid request payload or parameters",
    "details": []
  },
  "path": "/route/path"
}
```

## Success payload strategy

Current API keeps endpoint-specific success responses (no global envelope) to avoid breaking existing clients.

Frontend guidance:
- Handle success with endpoint-specific typing from OpenAPI.
- Handle errors globally using the standardized error payload above.

## OpenAPI lock

Locked schema file: `openapi.lock.json`

To refresh lock after backend changes:

```bash
python -m app.scripts.export_openapi_lock
```
