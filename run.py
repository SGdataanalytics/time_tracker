"""
Development entry point for the time_tracker Flask app.

Run with:
    .venv/bin/python run.py

This starts Flask's built-in development server. It is intended for local
development only, not for production deployment.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Binds to localhost only (127.0.0.1, the default), so the dev server
    # is not reachable from other devices/network. Per PROJECT.md's
    # security and deployment direction, any change to how this server is
    # exposed on the network is a separate, explicit decision and is not
    # made here. debug=True enables auto-reload and detailed error pages
    # during development only.
    app.run(port=5000, debug=True)

