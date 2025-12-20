"""Check environment variables loading."""
import os
print(f"Raw os.environ DATABASE_URL: {os.getenv('DATABASE_URL')}")

# Load dotenv
from dotenv import load_dotenv
load_dotenv()

print(f"After dotenv DATABASE_URL: {os.getenv('DATABASE_URL')}")

# Now import settings
from app.config import settings
print(f"Settings DATABASE_URL: {settings.DATABASE_URL}")