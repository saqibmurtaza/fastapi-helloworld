from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret, default="postgresql://neondb_owner:pmin7cHsMU4P@ep-autumn-darkness-a1pxi086.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")

TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)