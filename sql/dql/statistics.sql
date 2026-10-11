-- The statistics of a period, one row per position (R5): seated and lying
-- are not the same measurement and are never averaged together.
-- A position with no reading in the period has no row.
-- Parameters: the first and the last instant, 'YYYY-MM-DD HH:MM:SS'.
SELECT p.position_id,
       p.description AS position,
       COUNT(*) AS readings,
       AVG(r.systolic_mmhg) AS systolic_mean,
       MIN(r.systolic_mmhg) AS systolic_min,
       MAX(r.systolic_mmhg) AS systolic_max,
       AVG(r.diastolic_mmhg) AS diastolic_mean,
       MIN(r.diastolic_mmhg) AS diastolic_min,
       MAX(r.diastolic_mmhg) AS diastolic_max,
       AVG(r.heart_rate_bpm) AS heart_rate_mean,
       MIN(r.heart_rate_bpm) AS heart_rate_min,
       MAX(r.heart_rate_bpm) AS heart_rate_max
  FROM readings AS r
  JOIN positions AS p ON p.position_id = r.position_id
 WHERE r.enable = 1
   AND r.recorded_at BETWEEN ? AND ?
 GROUP BY p.position_id, p.description
 ORDER BY p.position_id;
