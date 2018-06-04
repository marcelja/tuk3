SET SCHEMA TUK3_TS_MJ;

WITH rows AS (SELECT ROW_NUMBER() OVER (ORDER BY id, timestamp) AS row, id, timestamp, lat, lon, occupancy FROM SHENZHEN)
SELECT r2.* FROM rows r1, rows r2 WHERE r1.occupancy = 0 AND r2.occupancy = 1 AND r1.row = r2.row - 1 AND r1.id = r2.id ORDER by r2.row

-- ca. 8 s (7,5 - 7,7)