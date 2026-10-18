"""
Database access for the time_tracker application.

Storage technology: SQLite, via Python's built-in `sqlite3` module.
No ORM is used — see "Phase 1 architecture decisions" in PROJECT.md.

Why SQLite for v0.1:
- It ships with Python, so no new dependency is required.
- Unlike a flat JSON/CSV file, it does not require rewriting the whole
  file to add or edit a single entry.
- It naturally supports the aggregate queries (totals per category, per
  week, etc.) planned for the Phase 4 statistics feature, without having
  to redesign storage later.

Where the database file lives:
- Flask's "instance folder" (`app.instance_path`, i.e. an `instance/`
  directory next to this package) is used to store the actual
  `time_tracker.sqlite` file. This folder is for environment-specific,
  non-source data and is already excluded in `.gitignore`, so personal
  time-tracking data is never committed to Git.

How this module is used:
- `init_app(app)` registers the connection teardown and the `init-db`
  CLI command with the Flask app.
- `get_db()` returns a SQLite connection for the current request,
  reusing it if already opened (via Flask's `g` request context).
"""

import sqlite3
from pathlib import Path

import click
from flask import current_app, g


def get_db():
    """Return a SQLite connection for the current request.

    Flask's `g` object is a per-request storage area. Reusing the
    connection from `g` means we open at most one connection per request,
    even if multiple functions need database access during that request.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        # Rows behave like dicts (e.g. row["entry_date"]) instead of plain
        # tuples, which makes templates and route code easier to read.
        g.db.row_factory = sqlite3.Row
        # Enforce foreign key constraints (not used yet, but safe default).
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request, if open."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Create the database schema from schema.sql, if it does not exist yet.

    schema.sql uses `CREATE TABLE IF NOT EXISTS`, so calling this again
    (e.g. on every app startup) is safe and never deletes existing user
    data. A separate, deliberate action would be required to reset data,
    and no such action is provided in Phase 1.
    """
    db = get_db()

    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r") as f:
        db.executescript(f.read())


@click.command("init-db")
def init_db_command():
    """Flask CLI command: `flask --app app init-db`."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Wire this module into the Flask app (called from create_app)."""
    # Make sure the instance folder (where the .sqlite file lives) exists.
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Close the DB connection automatically when a request ends.
    app.teardown_appcontext(close_db)
    # Add `flask --app app init-db` as a setup command.
    app.cli.add_command(init_db_command)


# --- Query helpers used by routes.py -------------------------------------
#
# Keeping these small, specific functions here (instead of writing raw SQL
# in routes.py) keeps routes.py focused on request/response handling.


def get_all_entries():
    """Return all time entries, most recent entry_date first."""
    db = get_db()
    return db.execute(
        "SELECT * FROM time_entries ORDER BY entry_date DESC, id DESC"
    ).fetchall()


def get_entry(entry_id):
    """Return a single time entry by id, or None if it doesn't exist."""
    db = get_db()
    return db.execute(
        "SELECT * FROM time_entries WHERE id = ?", (entry_id,)
    ).fetchone()


def add_entry(
    entry_date,
    duration_minutes,
    category,
    subcategory,
    description,
    start_time=None,
    end_time=None,
):
    """Insert a new time entry and return its new id.

    `start_time` and `end_time` are optional and secondary to
    `duration_minutes`, per the Phase 1 data model decision.
    """
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO time_entries (
            entry_date, duration_minutes, category, subcategory,
            description, start_time, end_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entry_date,
            duration_minutes,
            category,
            subcategory,
            description,
            start_time,
            end_time,
        ),
    )
    db.commit()
    return cursor.lastrowid


def update_entry(
    entry_id,
    entry_date,
    duration_minutes,
    category,
    subcategory,
    description,
    start_time=None,
    end_time=None,
):
    """Update an existing time entry in place.

    `updated_at` is set explicitly here (to the current UTC timestamp)
    rather than via a database trigger, so the Python code stays the
    single, visible place where this behaviour is defined.
    """
    db = get_db()
    db.execute(
        """
        UPDATE time_entries
        SET entry_date = ?,
            duration_minutes = ?,
            category = ?,
            subcategory = ?,
            description = ?,
            start_time = ?,
            end_time = ?,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (
            entry_date,
            duration_minutes,
            category,
            subcategory,
            description,
            start_time,
            end_time,
            entry_id,
        ),
    )
    db.commit()

