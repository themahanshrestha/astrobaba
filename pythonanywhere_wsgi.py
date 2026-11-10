# Paste the body of this file into PythonAnywhere's WSGI configuration file (Web tab),
# replacing everything in it, and change YOURUSERNAME. See DEPLOY.md, Option C.
import sys

PROJECT = "/home/YOURUSERNAME/astrobaba"
if PROJECT not in sys.path:
    sys.path.insert(0, PROJECT)

from a2wsgi import ASGIMiddleware  # noqa: E402
from api.main import app  # noqa: E402

application = ASGIMiddleware(app)   # PythonAnywhere runs WSGI; this adapts the FastAPI (ASGI) app
