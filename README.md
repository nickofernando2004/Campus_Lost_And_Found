# Campus Lost & Found + Claim Verification System

A modular command-line **Campus Lost & Found Management and Claim Verification System** built with **Python** and **SQLite**.

## Contributors
- **nickofernando2004** — Core database schema, SHA-256 authentication, found items catalog/search, claim verification workflow, CLI architecture, sample seeder, and unit test suite
- **mondiajames6-oss** — Administrative analytics summary and campus loss hotspot reporting (`src/reports.py`)

## Features
- **Role-Based Authentication (`src/auth.py`)**: SHA-256 password hashing supporting `student` and `admin` (Campus Security / OSA) privileges.
- **Relational SQLite Database (`src/database.py`)**: Three normalized tables (`users`, `found_items`, `claims`) with foreign-key enforcement.
- **Found Item Cataloging & Search (`src/items.py`)**: Log newly found items across campus, view unclaimed inventory, and filter by keyword, category, or location.
- **Ownership Claim Verification (`src/claims.py`)**: Students submit proof-of-ownership claims; admins verify claims, approve rightful owners, and automatically close competing claims.
- **Analytics & Hotspot Reporting (`src/reports.py`)**: Generates system-wide inventory/claim summaries and ranks top campus loss locations for admins.
- **Sample Seeder & Automated Tests (`seed.py`, `tests/test_system.py`)**: Populates realistic demo records and verifies the full end-to-end claim lifecycle via `unittest`.

## Project Structure
- `main.py` — Interactive CLI menu and user session controller
- `seed.py` — Sample database seeder for immediate testing
- `src/__init__.py` — Package initializer
- `src/database.py` — SQLite connection and 3-table schema setup
- `src/auth.py` — SHA-256 registration and role-based login
- `src/items.py` — Found item reporting, listing, and search
- `src/claims.py` — Claim submission and admin verification logic
- `src/reports.py` — Admin summary statistics and campus loss hotspots
- `tests/test_system.py` — Automated end-to-end unit test suite
- `.gitignore` — Excludes local SQLite DB and Python cache files
- `README.md` — Project documentation

## How to Run
1. *(Optional)* Populate sample data: `python3 seed.py`
2. Run automated tests: `python3 -m unittest discover -s tests -v`
3. Launch the application: `python3 main.py`
