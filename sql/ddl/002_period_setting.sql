-- ---------------------------------------------------------------------------
-- project:  sphygmus
-- authors:  Giuseppe Costanzi (1966bc)
-- file:     sql/ddl/002_period_setting.sql
-- target:   SQLite 3.21.0
-- ---------------------------------------------------------------------------
--
-- Schema 2: the period shown when the program starts is a setting, and no
-- longer a number in the code.
--
-- A migration runs on every diary, the new ones included: a diary is built
-- by 001 and the master data, then by every migration in order, so a new
-- diary and an old one brought up to date are the same by construction.
-- One transaction: it is applied whole, or not at all.
-- ---------------------------------------------------------------------------

BEGIN;

INSERT INTO settings (code, value, description, enable) VALUES
    ('period_days', '30',
     'The period shown at start: from this many days ago to today', 1);

PRAGMA user_version = 2;

COMMIT;
