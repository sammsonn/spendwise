# SpendWise

A personal finance management application built with Django REST Framework and Vue 3. Track transactions, set budgets, monitor savings goals, and visualize spending patterns.

## Tech Stack

| Layer    | Technology                                              |
| -------- | ------------------------------------------------------- |
| Backend  | Python 3.12, Django 6.0.5, Django REST Framework, SimpleJWT |
| Frontend | Vue 3, TypeScript, Vite, Pinia, Chart.js                |
| Database | PostgreSQL 16                                           |
| AI       | Google Gemini 3.1 Flash Lite                                 |
| Infra    | Docker, Nginx, Gunicorn                                 |

## Features

- **Transaction Management** — Create, edit, delete, and search transactions with filtering by date, category, type, and amount range
- **Recurring Transactions** — Support for daily, weekly, monthly, and yearly recurrence
- **Categories** — User-defined categories with custom colors and icons, split by income and expense types
- **Budgets** — Monthly per-category spending limits with progress tracking
- **Savings Goals** — Set target amounts and deadlines, track progress with percentage indicators
- **Reports** — Monthly comparison reports with spending trends, top categories, and budget adherence
- **Dashboard** — Overview with balance summary, category breakdown pie chart, expense trend line chart, and goals widget
- **Data Visualization** — Interactive pie, bar, and line charts (Chart.js)
- **Import/Export** — CSV import and export, PDF report generation
- **Multi-Currency** — Configurable preferred currency per user
- **AI Auto-Categorization** — Automatically suggests a transaction category based on the description using Google Gemini
- **AI Financial Assistant** — Chat interface for asking questions about your spending, budgets, and goals with AI-powered answers based on your actual data
- **Dark Mode** — System-wide dark theme with per-user persistence
- **Authentication** — JWT-based auth with registration, login, and token refresh

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Task](https://taskfile.dev/installation/) (optional, for shorthand commands)

### Quick Start (Docker)

```bash
cp .env.example .env    # adjust values as needed
task up                 # or: docker compose up -d --build
```

The app will be available at [http://localhost](http://localhost). The backend runs migrations and loads currency fixtures automatically on startup.

### Local Development

**Backend:**

```bash
task backend:install        # create venv and install dependencies
task seed                   # run migrations + load currency fixtures
task backend:superuser      # create an admin account
task backend:run            # start Django dev server on :8000
```

**Frontend:**

```bash
task frontend:install       # npm ci
task frontend:dev           # start Vite dev server on :5173
```

Or run both at once:

```bash
task dev
```

### Environment Variables

| Variable               | Default                       | Description                  |
| ---------------------- | ----------------------------- | ---------------------------- |
| `SECRET_KEY`           | (insecure dev key)            | Django secret key            |
| `DEBUG`                | `False`                       | Django debug mode            |
| `ALLOWED_HOSTS`        | `localhost,127.0.0.1`         | Comma-separated allowed hosts |
| `DB_NAME`              | `spendwise`                   | PostgreSQL database name     |
| `DB_USER`              | `spendwise`                   | PostgreSQL user              |
| `DB_PASSWORD`          | `spendwise123`                | PostgreSQL password          |
| `CORS_ALLOWED_ORIGINS` | `http://localhost`            | Comma-separated CORS origins |
| `GEMINI_API_KEY`       | (none)                        | Google Gemini API key for AI features |

## Project Structure

```
├── backend/
│   ├── config/             # Django settings, root URLs, WSGI
│   ├── transactions/       # Core app: models, views, serializers, fixtures
│   ├── budgets/            # Budget tracking app
│   ├── goals/              # Savings goals app
│   ├── ai_assistant/       # AI features: Gemini integration, categorize & chat
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/          # Page components (Dashboard, Transactions, etc.)
│   │   ├── components/     # Shared components (AppLayout, Charts)
│   │   ├── stores/         # Pinia state management
│   │   ├── api.ts          # Axios instance with JWT interceptors
│   │   └── router/         # Vue Router configuration
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── Taskfile.yml
└── .env.example
```

## API Endpoints

| Endpoint                      | Methods         | Description                    |
| ----------------------------- | --------------- | ------------------------------ |
| `/api/auth/register/`         | POST            | User registration              |
| `/api/auth/login/`            | POST            | Obtain JWT token pair          |
| `/api/auth/refresh/`          | POST            | Refresh access token           |
| `/api/auth/profile/`          | GET, PUT, PATCH | User profile and preferences   |
| `/api/transactions/`          | CRUD            | Transaction management         |
| `/api/transactions/import-csv/` | POST          | Import transactions from CSV   |
| `/api/transactions/export-csv/` | GET           | Export transactions as CSV     |
| `/api/transactions/export-pdf/` | GET           | Export transactions as PDF     |
| `/api/categories/`            | CRUD            | Category management            |
| `/api/budgets/`               | CRUD            | Budget management              |
| `/api/goals/`                 | CRUD            | Savings goals management       |
| `/api/currencies/`            | GET             | Available currencies           |
| `/api/stats/summary/`         | GET             | Income/expense/balance summary |
| `/api/stats/by-category/`     | GET             | Spending breakdown by category |
| `/api/stats/balance-trend/`   | GET             | 6-month cumulative balance     |
| `/api/stats/monthly-report/`  | GET             | Month-over-month comparison    |
| `/api/ai/categorize/`         | POST            | AI-powered category suggestion |
| `/api/ai/chat/`               | POST            | AI financial assistant chat    |

## Available Tasks

```
task up                  # Start all services with Docker Compose
task down                # Stop all Docker services
task logs                # Tail Docker logs
task restart             # Restart all Docker services
task dev                 # Start backend + frontend dev servers
task install             # Install all dependencies
task seed                # Run migrations and load fixtures
task lint                # Run Django checks + TypeScript type checking
```
