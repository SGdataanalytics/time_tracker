"""
Category and subcategory definitions for time entries.

This is the single place in the application where categories and their
subcategories are defined. Keeping them here (instead of scattered across
templates or routes) makes it easy to change the category list later
without touching the rest of the application.

The final category/subcategory list is not decided yet. This starting list
is intentionally simple and can be edited freely as the app evolves.
"""

CATEGORIES = {
    "Development": [
        "time_tracker",
        "Other projects",
    ],
    "Research / Learning": [
        "AI / Local models",
        "Coding / Technical learning",
        "Industry research",
        "Other",
    ],
    "Networking / Communication": [
        "LinkedIn",
        "Email",
        "Calls",
        "Other",
    ],
    "Administration": [
        "Invoicing",
        "Documentation",
        "Other",
    ],
    "Business Development": [
        "Sales",
        "Outreach",
        "Proposals",
        "Other",
    ],
    "Planning": [
        "Weekly planning",
        "Project planning",
        "Other",
    ],
    "Meetings": [
        "Client",
        "Internal",
        "Other",
    ],
    "Education / Certification": [
        "Azure",
        "Other certification",
    ],
    "Other": [
        "Other",
    ],
}


def get_categories():
    """Return the list of available category names, in definition order."""
    return list(CATEGORIES.keys())


def get_subcategories(category):
    """Return the list of subcategories for a given category.

    Returns an empty list if the category is unknown, so callers can
    handle unexpected input gracefully.
    """
    return CATEGORIES.get(category, [])