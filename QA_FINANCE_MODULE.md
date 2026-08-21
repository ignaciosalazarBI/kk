# QA · Finance module

Checks before Beta release:

- `app.py` and `admin.py` compile on Python 3.12.
- Dependencies install and pass `pip check`.
- `.streamlit/secrets.toml` is not committed.
- No service-role key reference is committed.
- Finance page is reachable via `?start=finanzas` and sidebar.
- Finance demo uses fictional data only.
- Existing tracking remains enabled (`pantalla_finanzas`).
- Existing forms and navigation remain unchanged outside the new Finance module.
