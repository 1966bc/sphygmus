-- ---------------------------------------------------------------------------
-- project:  sphygmus
-- authors:  Giuseppe Costanzi (1966bc)
-- file:     sql/dml/001_master_data.sql
-- ---------------------------------------------------------------------------
--
-- What an empty diary needs before the first reading. No person is named
-- here: patient_name is filled in from the program, on the machine where the
-- diary is kept.
-- ---------------------------------------------------------------------------

INSERT INTO positions (position_id, description, enable) VALUES
    (1, 'seated', 1),
    (2, 'lying', 1);

-- The thresholds for blood pressure measured at home, from the ESH 2021
-- position paper on home monitoring (Parati et al., J Hypertens 2021; free
-- text at PMC9904446, Box 16): a home mean of 135/85 mmHg or more corresponds
-- to 140/90 in the surgery. A reading
-- is flagged when either value reaches its threshold. A flag, not a verdict.
INSERT INTO settings (setting_id, code, value, description, enable) VALUES
    (1, 'patient_name', '', 'Name printed at the head of the report', 1),
    (2, 'systolic_threshold_mmhg', '135',
        'Systolic at or above this is flagged (ESH 2021, home)', 1),
    (3, 'diastolic_threshold_mmhg', '85',
        'Diastolic at or above this is flagged (ESH 2021, home)', 1);
