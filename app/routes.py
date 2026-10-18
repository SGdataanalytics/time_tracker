"""
Routes for the time_tracker application.

Per the fixed Phase 1 architecture decisions in PROJECT.md, routes are
registered directly on the Flask `app` object via `init_app(app)` —
Flask Blueprints are not used in Phase 1.

Three pages exist in Phase 1:
- GET  /            -> list all time entries
- GET  /new         -> show the "add entry" form
- POST /new         -> validate and insert a new entry
- GET  /edit/<id>   -> show the "edit entry" form, pre-filled
- POST /edit/<id>   -> validate and update an existing entry

Validation is deliberately simple, explicit Python (no form library),
in keeping with the project's "prefer simple, understandable code" and
"deterministic logic over frameworks" principles.
"""

from datetime import datetime

from flask import abort, flash, redirect, render_template, request, url_for

from . import categories, db


def validate_entry_form(form):
    """Validate submitted entry-form fields.

    Returns a tuple (data, errors):
    - data: dict of cleaned values, suitable for passing to
      db.add_entry() / db.update_entry() (duration_minutes is an int;
      everything else is a string or None).
    - errors: list of human-readable error messages. Empty if valid.
    """
    errors = []

    entry_date = (form.get("entry_date") or "").strip()
    duration_raw = (form.get("duration_minutes") or "").strip()
    category = (form.get("category") or "").strip()
    subcategory = (form.get("subcategory") or "").strip()
    description = (form.get("description") or "").strip()
    start_time = (form.get("start_time") or "").strip()
    end_time = (form.get("end_time") or "").strip()

    # entry_date: required, must be a real calendar date in YYYY-MM-DD form.
    if not entry_date:
        errors.append("Date is required.")
    else:
        try:
            datetime.strptime(entry_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Date must be a valid date (YYYY-MM-DD).")

    # duration_minutes: required, must be a positive whole number.
    duration_minutes = None
    if not duration_raw:
        errors.append("Duration (minutes) is required.")
    else:
        try:
            duration_minutes = int(duration_raw)
            if duration_minutes <= 0:
                errors.append("Duration (minutes) must be greater than 0.")
        except ValueError:
            errors.append("Duration (minutes) must be a whole number.")

    # category: required, must be one of the known categories.
    if not category:
        errors.append("Category is required.")
    elif category not in categories.get_categories():
        errors.append("Unknown category selected.")

    # subcategory: optional, but if given must belong to the chosen category.
    if subcategory and category in categories.get_categories():
        if subcategory not in categories.get_subcategories(category):
            errors.append("Unknown subcategory selected for this category.")

    # description: optional free text; an entry does not require one.

    data = {
        "entry_date": entry_date,
        "duration_minutes": duration_minutes,
        "category": category,
        "subcategory": subcategory or None,
        "description": description or None,
        "start_time": start_time or None,
        "end_time": end_time or None,
    }
    return data, errors


def index():
    """List all time entries, most recent first."""
    entries = db.get_all_entries()
    return render_template("index.html", entries=entries)


def _categories_map():
    """Build {category: [subcategories]} from the public categories API.

    Used by the entry form template to drive client-side subcategory
    filtering, without the template or routes depending on the internal
    shape of app/categories.py.
    """
    return {
        category: categories.get_subcategories(category)
        for category in categories.get_categories()
    }


def new_entry():
    """Show the add-entry form (GET) or create a new entry (POST)."""
    if request.method == "POST":
        data, errors = validate_entry_form(request.form)

        if errors:
            for message in errors:
                flash(message)
            return render_template(
                "entry_form.html",
                categories=categories.get_categories(),
                categories_map=_categories_map(),
                entry=data,
                form_action=url_for("new_entry"),
                heading="Add time entry",
            )

        db.add_entry(
            entry_date=data["entry_date"],
            duration_minutes=data["duration_minutes"],
            category=data["category"],
            subcategory=data["subcategory"],
            description=data["description"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )
        flash("Entry added.")
        return redirect(url_for("index"))

    return render_template(
        "entry_form.html",
        categories=categories.get_categories(),
        categories_map=_categories_map(),
        entry=None,
        form_action=url_for("new_entry"),
        heading="Add time entry",
    )



def edit_entry(entry_id):
    """Show the edit-entry form (GET) or update an existing entry (POST)."""
    existing = db.get_entry(entry_id)
    if existing is None:
        abort(404)

    if request.method == "POST":
        data, errors = validate_entry_form(request.form)

        if errors:
            for message in errors:
                flash(message)
            # Keep the id so the template can still build the correct
            # form action, and show what the user just typed.
            data["id"] = entry_id
            return render_template(
                "entry_form.html",
                categories=categories.get_categories(),
                categories_map=_categories_map(),
                entry=data,
                form_action=url_for("edit_entry", entry_id=entry_id),
                heading="Edit time entry",
            )

        db.update_entry(
            entry_id=entry_id,
            entry_date=data["entry_date"],
            duration_minutes=data["duration_minutes"],
            category=data["category"],
            subcategory=data["subcategory"],
            description=data["description"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )
        flash("Entry updated.")
        return redirect(url_for("index"))

    return render_template(
        "entry_form.html",
        categories=categories.get_categories(),
        categories_map=_categories_map(),
        entry=existing,
        form_action=url_for("edit_entry", entry_id=entry_id),
        heading="Edit time entry",
    )


def init_app(app):
    """Register all routes directly on the Flask app (no Blueprints)."""
    app.add_url_rule("/", view_func=index, methods=["GET"])
    app.add_url_rule("/new", view_func=new_entry, methods=["GET", "POST"])
    app.add_url_rule(
        "/edit/<int:entry_id>", view_func=edit_entry, methods=["GET", "POST"]
    )


