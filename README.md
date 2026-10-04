# Flask Inventory App

A small inventory application with a Flask JSON API, command-line product search, and a React interface for testing inventory CRUD operations. Inventory data is stored in `backend/db.json`. Product lookups use the Open Food Facts API.

## Requirements

- Python with Flask and Requests installed
- Node.js and npm (for the React interface)

## Run the app

Start the Flask API from the project root:

```bash
python3 backend/app.py
```

The API runs at `http://127.0.0.1:5555`. Its inventory routes support listing and retrieving items (`GET`), creating (`POST`), updating (`PATCH`), and deleting (`DELETE`).

To run the React interface, open another terminal:

```bash
cd react_frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The React app connects directly to Flask; the backend allows CORS from the local Vite origins.

## Run tests

From the project root:

```bash
python3 -m pytest
```
