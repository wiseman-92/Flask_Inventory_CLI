# Flask_Inventory_CLI

## Run the inventory CRUD test UI

Start Flask in one terminal:

```bash
python3 backend/app.py
```

Start the React development server in another:

```bash
cd react_frontend
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`). The React app calls Flask at `http://127.0.0.1:5555` directly; Flask allows CORS requests from `localhost:5173` and `127.0.0.1:5173`.
