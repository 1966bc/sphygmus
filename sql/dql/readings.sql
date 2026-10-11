-- The readings of a period, the latest first, with the name of the position.
-- Parameters: the first and the last instant, 'YYYY-MM-DD HH:MM:SS'.
SELECT r.reading_id,
       r.recorded_at,
       r.position_id,
       p.description AS position,
       r.systolic_mmhg,
       r.diastolic_mmhg,
       r.heart_rate_bpm
  FROM readings AS r
  JOIN positions AS p ON p.position_id = r.position_id
 WHERE r.enable = 1
   AND r.recorded_at BETWEEN ? AND ?
 ORDER BY r.recorded_at DESC;
