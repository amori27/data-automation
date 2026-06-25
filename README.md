# Data Automation

[![CI/CD](https://github.com/amori27/data-automation/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/amori27/data-automation/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)(LICENSE)

> End-to-end data pipeline: extract from SQL/CSV, transform with Pandas, generate formatted Excel reports, and deliver via Email or Slack.

## Features

- CSV and SQL database extraction (SQLAlchemy)
- Pandas-based transformation and aggregation
- Professional Excel reports with styled headers (openpyxl)
- Automated delivery via SMTP email or Slack webhooks
- Sample dataset included for immediate testing

## Quick Start

```bash
pip install -r requirements.txt

# Run the pipeline on sample data
python -c "
from src.core.pipeline import run_pipeline
path = run_pipeline('data/sample/sales.csv')
print(f'Report: {path}')
"
```

## API

```bash
uvicorn src.main:app --reload
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"source": "csv", "source_path": "data/sample/sales.csv"}'
```

## License

MIT
