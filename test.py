from dotenv import load_dotenv
load_dotenv()
import os

print(os.getenv("TMDB_API_KEY"))