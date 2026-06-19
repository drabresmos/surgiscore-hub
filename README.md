# SurgiScore Hub v3.1

Streamlit surgical scoring platform for general surgery trainees.

## Deploy on Streamlit Cloud
- Upload all files to GitHub repository.
- Main file path: `app.py`
- Requirements are in `requirements.txt`.

## Note
SQLite storage works inside the app environment, but Streamlit Cloud storage can reset after redeploy/reboot. For production use, migrate to Supabase/PostgreSQL.
