
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

project_dir = Path(__file__).resolve().parent
load_dotenv(project_dir / ".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not url or not key:
    print("ERROR: Check SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in .env")
else:
    supabase = create_client(url, key)

    response = (
        supabase
        .table("monthly_attendance")
        .select("month,total_ae_attendances")
        .limit(5)
        .execute()
    )

    print("Supabase connection successful!")
    print("Attendance records:")
    for record in response.data:
        print(record)
