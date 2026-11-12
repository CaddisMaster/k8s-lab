"""What uvicorn runs: the app, configured from the environment, with the checking loop on.

Kept apart from main.py so importing the routes (in tests) never touches /data or starts a loop.
"""

import logging
import os

from .main import Settings, create_app

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "info").upper())
app = create_app(Settings.from_env())
