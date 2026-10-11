-- ---------------------------------------------------------------------------
-- project:  sphygmus
-- authors:  Giuseppe Costanzi (1966bc)
-- file:     sql/ddl/001_schema.sql
-- target:   SQLite 3.21.0 (no UPSERT, no window functions, no RETURNING)
-- ---------------------------------------------------------------------------
--
-- A home blood pressure diary for one person. The database *is* that person:
-- there is no patients table and no patient_id, so no query can forget to
-- filter on one. Whose diary it is lives in settings, for the report heading.
--
-- The dividing line of the whole design: a reading is stored exactly as the
-- device showed it, and nothing derived from it is stored at all. Means,
-- minima, maxima and the flag over the threshold are computed when they are
-- shown, so they can never disagree with the readings they come from.
--
-- Conventions (CONVENTIONS.md): plural table names, primary key
-- <singular>_id, units in column names, ISO 8601 text for dates, enable for
-- logical deletion on every table.
-- ---------------------------------------------------------------------------

PRAGMA foreign_keys = ON;

-- An integer of ours, not user input: the one statement with no placeholder.
PRAGMA user_version = 1;

-- Name/value pairs the program reads at startup. A threshold is data, not a
-- constant in the code: when the doctor gives another one, a row changes.
CREATE TABLE settings (
    setting_id  INTEGER PRIMARY KEY,
    code        TEXT    NOT NULL UNIQUE,
    value       TEXT,
    description TEXT,
    enable      INTEGER NOT NULL DEFAULT 1 CHECK (enable IN (0, 1))
);

-- Seated or lying down. A table and not free text, so the statistics can be
-- grouped by it and a typo cannot invent a third position.
CREATE TABLE positions (
    position_id INTEGER PRIMARY KEY,
    description TEXT    NOT NULL UNIQUE,
    enable      INTEGER NOT NULL DEFAULT 1 CHECK (enable IN (0, 1))
);

-- One row per reading, as the device showed it. Three readings taken one
-- after the other are three rows a minute apart: the timestamp, down to the
-- second, already says which belong together.
CREATE TABLE readings (
    reading_id     INTEGER PRIMARY KEY,
    position_id    INTEGER NOT NULL REFERENCES positions (position_id),
    recorded_at    TEXT    NOT NULL
                   CHECK (recorded_at LIKE '____-__-__ __:__:__'),
    systolic_mmhg  INTEGER NOT NULL CHECK (systolic_mmhg > 0),
    diastolic_mmhg INTEGER NOT NULL CHECK (diastolic_mmhg > 0),
    heart_rate_bpm INTEGER NOT NULL CHECK (heart_rate_bpm > 0),
    enable         INTEGER NOT NULL DEFAULT 1 CHECK (enable IN (0, 1)),
    CHECK (systolic_mmhg > diastolic_mmhg)
);

-- Two readings cannot share a second. Only among the enabled ones: a reading
-- typed wrong is disabled and typed again with the same date and time.
CREATE UNIQUE INDEX readings_recorded_at
    ON readings (recorded_at) WHERE enable = 1;

-- When each reading was typed in, disabled or enabled again. recorded_at
-- says when the pressure was measured; this says when the diary was written,
-- which is a different fact. Local time, as the readings are.
--
-- No copy of the values is kept, as audit tables usually do: the guards
-- below make a reading immutable, so its id is enough to know what it said.
CREATE TABLE audit_readings (
    audit_reading_id INTEGER PRIMARY KEY,
    reading_id       INTEGER NOT NULL REFERENCES readings (reading_id),
    operation        TEXT    NOT NULL
                     CHECK (operation IN ('INSERT', 'DISABLE', 'ENABLE')),
    log_time         TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX audit_readings_reading ON audit_readings (reading_id);

-- The guards. R6 written in the database itself, so that it holds for the
-- sqlite3 shell and for any script, not only for the program.

-- Nothing is deleted.
CREATE TRIGGER tr_readings_no_delete BEFORE DELETE ON readings
BEGIN
    SELECT RAISE(ABORT, 'readings are never deleted: set enable = 0');
END;

-- A reading is never changed: what the device showed, it showed. The only
-- column that may move is enable, so a correction is a disable and a new row.
CREATE TRIGGER tr_readings_no_update
    BEFORE UPDATE OF position_id, recorded_at, systolic_mmhg,
                     diastolic_mmhg, heart_rate_bpm
    ON readings
BEGIN
    SELECT RAISE(ABORT,
        'a reading is never changed: disable it and insert a new one');
END;

-- The trail.

CREATE TRIGGER tr_readings_insert AFTER INSERT ON readings
BEGIN
    INSERT INTO audit_readings (reading_id, operation)
    VALUES (NEW.reading_id, 'INSERT');
END;

-- Only a real change of state is written: setting enable to the value it
-- already has did nothing, and the trail says what happened.
CREATE TRIGGER tr_readings_enable AFTER UPDATE OF enable ON readings
    WHEN OLD.enable <> NEW.enable
BEGIN
    INSERT INTO audit_readings (reading_id, operation)
    VALUES (NEW.reading_id,
            CASE NEW.enable WHEN 0 THEN 'DISABLE' ELSE 'ENABLE' END);
END;
