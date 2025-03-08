import sys
import argparse
from backend.fastapi.core.config import get_settings
import os

default_host = "0.0.0.0" if "RAILWAY_ENVIRONMENT" in sys.argv or "PORT" in os.environ else "127.0.0.1"
default_mode = "prod" if "RAILWAY_ENVIRONMENT" in sys.argv or "PORT" in os.environ else "dev"

# Set up the argument parser
parser = argparse.ArgumentParser()

parser.add_argument("--mode", choices=["dev", "prod"], default=default_mode, help="Set the running mode")
parser.add_argument("--host", type=str, default=default_host, help="Set the host")

# Determine if running under pytest
is_testing = "pytest" in sys.argv[0]

# Only parse arguments if not running Alembic
if not is_testing and 'alembic' not in sys.argv[0]:
    # Parse arguments only when running the app, not when Alembic is being run
    args = parser.parse_args()
else:
    # Provide mock arguments when running Alembic (or during testing)
    args = argparse.Namespace(mode="dev", host="127.0.0.1")

# Initialize and update settings
settings = get_settings(args.mode)

# Save updated settings for import in other modules
global_settings = settings
