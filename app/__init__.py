"""
Application factory for the time_tracker Flask app.

A "factory function" (`create_app`) builds and configures the Flask app,
rather than creating it as a bare module-level object. This is a standard
Flask pattern and keeps configuration (like the database path) explicit
and easy to override later, e.g. for automated tests.

Per the fixed Phase 1 architecture decisions in PROJECT.md, routes are
registered directly on the `app` object — Flask Blueprints are not used
in Phase 1.
"""

import os

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration. `instance_path` points at the instance/
    # folder next to this package, which is git-ignored and intended for
    # environment-specific, non-source files such as the SQLite database.
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "time_tracker.sqlite"),
    )

    if test_config is not None:
        # Allow tests to override configuration (e.g. use a separate
        # test database file) without touching real application data.
        app.config.from_mapping(test_config)

    db.init_app(app)

    # Make sure the database schema exists before the app serves requests.
    # init_db() is safe to call every time: schema.sql uses
    # CREATE TABLE IF NOT EXISTS, so existing data is never destroyed.
    with app.app_context():
        db.init_db()

    # Routes are registered directly on the app object (see module
    # docstring above) rather than through a Blueprint.
    from . import routes

    routes.init_app(app)

    return app

