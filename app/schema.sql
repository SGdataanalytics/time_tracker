-- Database schema for the time_tracker application (Phase 1).
--
-- Only the fields needed for manual structured entry are populated in
-- Phase 1. `original_text` and `input_source` already exist so the table
-- does not need to be redesigned once Phase 2 (natural-language input)
-- and later voice input are added.
--
-- IMPORTANT: this uses CREATE TABLE IF NOT EXISTS, not DROP TABLE, so that
-- running initialization again (e.g. on every app startup) never destroys
-- existing user data. Destructive resets must be a separate, deliberate
-- action, not part of normal initialization.

CREATE TABLE IF NOT EXISTS time_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT NOT NULL,            -- normalized date, e.g. '2026-10-08'
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    category TEXT NOT NULL,
    subcategory TEXT,                    -- optional (not every category needs one)
    description TEXT,                    -- optional free text; an entry does not require a description
    start_time TEXT,                     -- optional, secondary to duration_minutes
    end_time TEXT,                       -- optional, secondary to duration_minutes
    original_text TEXT,                  -- raw free text, if any (Phase 2+)
    input_source TEXT NOT NULL DEFAULT 'text' CHECK (input_source IN ('text', 'voice')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT                      -- set explicitly by the UPDATE query, NULL until first edit
);

