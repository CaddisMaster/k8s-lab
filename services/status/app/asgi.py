"""What uvicorn runs: the app, configured from the environment.

Kept apart from main.py so importing the routes (in tests) never touches /data.
"""

import logging
import os

from .main import Settings, create_app

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "info").upper())
app = create_app(Settings.from_env())
