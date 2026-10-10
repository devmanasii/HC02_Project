
import os
from pathlib import Path
from supabase import create_client

env_path = Path(__file__).resolve().parent / ".env"

if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            os.environ.setdefault(
                name.strip(),
                value.strip().strip('"').strip("'")
            )

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not url or not key:
    raise SystemExit("Missing Supabase URL or publishable key in .env")

try:
    client = create_client(url, key)
    result = client.table("hospitals").select("id").limit(1).execute()
    print("Supabase connection successful!")
    print("Hospital rows returned:", len(result.data))
except Exception as error:
    print("Supabase request failed.")
    print(type(error).__name__, str(error))