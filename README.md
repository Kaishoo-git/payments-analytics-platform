Client
  ↓
FastAPI Route
  ↓
Fraud Service
  ↓
Repository Layer
  ↓
PostgreSQL



# [Project Name]

> [Topic/Purpose etc.]

## Overview

[blah blah blah]

---

## [Miro Flowchart]

[insert here]



---

## Dashboard Pages [if needed]

| Page | Description |
|------|-------------|
| **Home** | Project overview, transfer rules reference, and team directory |


---

## Project Structure
```
psychic-octo-bassoon/
├── alembic/
│   ├── versions/                    # [add comment here]
│   ├── env.py                       # [add comment here]
│   ├── README.md
│   └── script.py.mako               # [add comment here]
├── app/                             
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── kafka/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── __init__.py
│   └── main.py
├── scripts/
│   ├── __init__.py
│   ├── post_transactions.py
│   ├── postgres_to_snowflake.py
│   ├── run_consumer.py
│   └── seed_data.py
├── tests/                            
│   ├── conftest.py
│   └── test_fraud_service.py
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── LICENSE
├── pytest.ini
├── README.md
└── requirements.txt
```

## Data Dependencies

The `data/` folder is not fully committed to this repository. Large CSV files must be sourced separately. The following files are required to run the app:

| File | Required By | Notes |
|------|-------------|-------|
| `trf_time_distribution.csv` | page1 | Transfer time by age group and hour |
| `trf_region_pair.csv` | page1 | Transfer volume by origin-destination pair and hour |
| `singapore_planning_areas.geojson` | page1, page2 | Singapore planning area boundaries |
| `singapore_map.geojson` | page1 | Singapore base map for frontend rendering |
| `final_delays.csv` | page2 | Delay simulation results by spec, patron, region, hour of day, and hour and region combination |
| `final_cleaned_delay_sim_results.csv` | page2 | Auto-generated from above on final_delays.csv on startup |
| `welfare_marginal.csv` | page3 | Marginal welfare results by patron and spec |
| `welfare_results.csv` | page3 | Welfare results |
| `welfare_results_regional.csv` | page3 | Regional welfare results |
| `spec_info.csv` | page3 | Model specification descriptions |
---

To regenerate the CSVs from scratch, run the notebooks in `models/` in the order described in `models/README.md`.


## Setup & Running

**1. Install Docker**

Ensure [Docker](https://docs.docker.com/desktop/setup/install/windows-install/) has been installed locally.

**2. Clone the Repository**
```bash
git clone https://github.com/Kaishoo-git/psychic-octo-bassoon.git
cd psychic-octo-bassoon
```

**3. Create `.env` File**

Create a `.env` file consisting of the following details:
```
# Postgres container
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# App config
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=

# Snowflake
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_ACCOUNT=

SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
```

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

**5. Open Docker Container and Run the App**
```bash
docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

**6. Populate the Data (in a Separate Terminal)**
```bash
python -m scripts.run_consumer
python -m scripts.seed_data
python -m scripts.post_transactions
```

[any additional text]
