# Run Manual

## Prerequisites
- Python 3.9+
- MongoDB running on localhost:27017

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run Migrations (for Auth):
   ```bash
   python3 manage.py migrate
   ```

## Running
1. Start Django Server:
   ```bash
   python3 manage.py runserver
   ```
2. Open Browser: `http://127.0.0.1:8000/`

## Offline Demo
1. Disconnect Internet.
2. Open `http://127.0.0.1:8000/offline/` (or auto-redirect).
3. Click "Start Offline Demo".
