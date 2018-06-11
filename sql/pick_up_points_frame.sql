SET SCHEMA TUK3_TS_MJ;

-- if frame != 0
SELECT lat, lon, count(*) AS weight 
FROM (
	SELECT round(pf1py + ify, 6) AS lat, 
            round(pf1px + ifx, 6) AS lon 
	FROM frame_format_speed 
	WHERE occupancy1 > occupancy0 AND fgcid = 0
) 
GROUP BY lat, lon
-- ca 11 ms

-- if frame == 0
SELECT lat, lon, count(*) AS weight 
	FROM (
	    SELECT round(ffs1.pf0py + ffs1.ify, 6) AS lat, 
	        round(ffs1.pf0px + ffs1.ifx, 6) AS lon 
	    FROM frame_format_speed ffs1, frame_format_speed ffs2
	    WHERE ffs1.occupancy0 > ffs2.occupancy39 
	        AND ffs1.fgcid = 2
	        AND ffs2.fgcid = 1
	        AND ffs1.tid = ffs2.tid
	        AND ffs1.pf0px IS NOT null
	        AND ffs2.pf39px IS NOT null
	) 
GROUP BY lat, lon
-- ca. 25 ms