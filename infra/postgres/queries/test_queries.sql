/** 1. show all active poll targets **/

-- SELECT p.*, s.*
-- FROM poll_target p
-- INNER JOIN station s
-- ON p.station_id = s.id
-- WHERE is_active = TRUE

/** 2. Show the latest known board state for one station **/

-- SELECT pt.id AS poll_target_id, s.name AS station_name, s.eva_number AS station_eva_number, ssc.*, se.*
-- FROM poll_target pt
-- LEFT JOIN station s ON pt.station_id = s.id
-- LEFT JOIN service_state_current ssc ON EXISTS (
--     SELECT 1
--     FROM service_observation so
--     INNER JOIN poll_run pr ON pr.id = so.poll_run_id
--     WHERE so.service_id = ssc.service_id
--       AND pr.poll_target_id = pt.id
-- )
-- LEFT JOIN service se ON se.id = ssc.service_id
-- WHERE pt.is_active = TRUE;

/** 3. Find services where the current effective time differs from the planned time. **/

-- SELECT se.service_run_uid, se.display_name, se.category, se.number, so.planned_arrival, ssc.current_arrival, so.planned_departure, ssc.current_departure, ssc.current_arrival_platform, ssc.current_departure_platform
-- FROM service_state_current ssc
-- INNER JOIN service se ON se.id = ssc.service_id
-- INNER JOIN service_observation so ON so.service_id = ssc.service_id
-- WHERE so.poll_run_id = ssc.latest_poll_run_id
--   AND (
--     (so.planned_arrival IS NOT NULL AND ssc.current_arrival IS NOT NULL AND so.planned_arrival <> ssc.current_arrival)
--     OR
--     (so.planned_departure IS NOT NULL AND ssc.current_departure IS NOT NULL AND so.planned_departure <> ssc.current_departure)
--   );

/** 4. Show recent change events. **/

-- SELECT s.service_run_uid, s.display_name, s.category, s.number, e.event_time, e.event_type, e.old_value, e.new_value
-- FROM service_state_event e
-- INNER JOIN service s ON s.id = e.service_id
-- ORDER BY e.event_time DESC, e.id DESC;

/** 5. Show history for one service run. **/

-- SELECT s.service_run_uid, s.display_name, s.category, s.number, e.event_time, e.event_type, e.old_value, e.new_value
-- FROM service_state_event e
-- INNER JOIN service s ON s.id = e.service_id
-- WHERE s.service_run_uid = '-5045088658159597679-2605091556'
-- ORDER BY e.event_time ASC, e.id ASC;