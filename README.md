# Smart Resource Allocation System - Luxury Investment Planner

This is a full-stack project with:

- Frontend dashboard (tables, cards, charts)
- Python Flask backend (all DSA logic)
- JSON document database (persistent options + analysis history)

## DSA Algorithms

- `Greedy Fractional Knapsack`
- `Dynamic Programming 0/1 Knapsack`
- `Compare` mode for side-by-side method analysis

## Data Model

### Collection: `investment_options`
- `id` TEXT primary key
- `name` TEXT
- `cost` INTEGER
- `value` INTEGER
- `createdAt` TEXT

### Collection: `analysis_runs`
- `id` INTEGER primary key
- `runAt` TEXT
- `mode` TEXT
- `budget` INTEGER
- `optionCount` INTEGER
- `fractionalValue` REAL
- `dpValue` REAL
- `winner` TEXT
- `utilization` REAL
- `notes` TEXT

## Project Structure

- `app.py` -> Flask routes and API layer
- `backend/database.py` -> JSON database storage layer
- `backend/repository.py` -> database CRUD operations
- `backend/algorithms.py` -> fractional + DP implementations
- `backend/analysis_service.py` -> metrics, tables, chart payloads
- `backend/utils.py` -> parsing and format helpers
- `templates/index.html` -> dashboard template
- `static/styles.css` -> luxury UI theme
- `static/script.js` -> API-driven frontend and charts

## API Endpoints

- `GET /api/bootstrap` -> options + history
- `GET /api/options` -> all investment options
- `POST /api/options` -> add option
- `DELETE /api/options/<option_id>` -> delete option
- `POST /api/options/reset` -> restore sample options
- `POST /api/analyze` -> run analysis using DB options
- `GET /api/history` -> latest run logs

## Run Locally

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Start server:

```powershell
python app.py
```

3. Open:

- `http://127.0.0.1:5000`

## Dashboard Features

- Persistent database-backed option management
- KPI cards for coverage, potential, ROI, winner, overbook ratio
- Detailed tables for option ranking and method performance
- DSA trace tables (greedy step trace + DP selection trace)
- Pie charts, bar charts, radar chart, and DP value-curve line chart
- Allocation pie charts per method
- Analysis history log table

## Input Notes

Budget/cost/value parser supports:

- `50000`
- `10k`
- `2l`
- `1cr`
