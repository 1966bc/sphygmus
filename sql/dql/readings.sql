-- The readings of a period, the latest first, with the name of the position.
-- Parameters: the first and the last instant, 'YYYY-MM-DD HH:MM:SS'; then
-- the lowest and the highest enable to show: 1 and 1 for the readings in
-- the diary, 0 and 0 for those taken out of it (R6), 0 and 1 for both.
SELECT r.reading_id,
       r.recorded_at,
       r.position_id,
       p.description AS position,
       r.systolic_mmhg,
       r.diastolic_mmhg,
       r.heart_rate_bpm,
       r.enable
  FROM readings AS r
  JOIN positions AS p ON p.position_id = r.position_id
 WHERE r.recorded_at BETWEEN ? AND ?
   AND r.enable BETWEEN ? AND ?
 ORDER BY r.recorded_at DESC, r.enable DESC;
