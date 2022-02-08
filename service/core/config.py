from starlette.datastructures import CommaSeparatedStrings
import os

ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))
API = "/api"
PROJECT_NAME = "neuralearn-face-api"