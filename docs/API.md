# API Reference

## `POST /run`

Trigger a report generation run.

**Request:**
```json
{
  "source": "csv",
  "source_path": "data/sample/sales.csv",
  "template": "monthly_report",
  "deliver_to": "email"
}
```

## `GET /reports`

List generated reports.
