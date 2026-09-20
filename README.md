# IPC Desk

A Flask + SQLite reference catalog for Indian Penal Code sections. It includes a searchable directory, section detail pages, a browser form for adding articles, and JSON endpoints.

## Run locally

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open `http://<your-computer-ip>:5000` in a browser from another device on the same network. The SQLite database is created at `instance/ipc.db` on first run.

## Free hosting on Render

1. Create a free account at Render and connect the GitHub repository.
2. Choose **New > Blueprint** and select this repository.
3. Render will read `render.yaml` and create the free `indianlawdetails` web service.

The free service sleeps when idle. The included SQLite database is suitable for a demo, but Render's local filesystem is not durable, so use managed PostgreSQL before treating added articles as permanent production data.

Set the Render environment variable `ADMIN_PASSWORD` to the editor password. Only username `bmandiya308` with that password can open the add-article page or create articles through `POST /api/articles`; browsing and search remain public.

## API

- `GET /api/articles` lists sections.
- `GET /api/articles?q=theft` searches section code, title, or chapter.
- `POST /api/articles` accepts JSON with `section_code`, `title`, `chapter`, `text`, `punishment`, and `details`.

The included entries are a starter catalog of commonly referenced IPC sections. Add the remaining sections through the editor or API as the authoritative source material is reviewed. This application is a research aid, not legal advice; verify current legislation, amendments, and case law.