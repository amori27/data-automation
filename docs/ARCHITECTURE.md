# Data Automation — Architecture

## Overview

Extract data from SQL DBs / CSV files, transform with Pandas, and generate formatted Excel reports with automated delivery via Email or Slack.

## Stack

| Layer | Technology |
|---|---|
| Extraction | SQLAlchemy + Pandas read_csv |
| Transformation | Pandas |
| Report Generation | openpyxl + Jinja2 |
| Scheduling | APScheduler |
| Delivery | SMTP (Email) / Slack Webhook |

## Data Flow

```
SQL DB ──┐
         ├──> Pandas ──> Transform ──> Jinja2 Template ──> Excel Report ──> Email/Slack
CSV ─────┘
```
