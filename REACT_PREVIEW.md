# React workspace — local development

The React workspace is now the primary production interface, not the earlier limited prototype. All ten workspaces are implemented.

For production-style local execution, follow [README.md](README.md#setup-and-run). For frontend development, run the API from the repository root:

```bash
python -m pip install -r requirements-preview.txt
python -m uvicorn preview_api:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd webapp
npm install
npm run dev
```

Open http://127.0.0.1:5173. The Vite configuration proxies API requests to the local backend. Use a separate built-app run for Playwright validation as documented in the main README. No key is needed for deterministic findings; keep credentials server-side and use synthetic data only.
