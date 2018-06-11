CREATE TYPE TUK3_TS_MJ.CHANGEPOINTSTYPE AS TABLE (
            lat real, lon real, weight smallint
);

create procedure TUK3_TS_MJ.changepoints_for_framegroup(in fgcidin int, in granularity int, in pointtype char, out output_table TUK3_TS_MJ.changepointstype)
LANGUAGE SQLSCRIPT AS
 BEGIN 

declare i int;

CREATE LOCAL TEMPORARY TABLE #TEMPTABLE1 (lat float(9), lon float(9));

IF :fgcidin > 0 THEN
	EXECUTE IMMEDIATE  'INSERT INTO #TEMPTABLE1 (
							SELECT round(ffs1.pf0py + ffs1.ify, '||:granularity||') AS lat, 
						           round(ffs1.pf0px + ffs1.ifx, '||:granularity||') AS lon 
						    FROM tuk3_ts_mj.frame_format_15_avg ffs1, tuk3_ts_mj.frame_format_15_avg ffs2
						    WHERE ffs1.occupancy0 '||:pointtype||' ffs2.occupancy39 
						        AND ffs1.fgcid = '||:fgcidin||'
						        AND ffs2.fgcid = '||:fgcidin - 1||'
						        AND ffs1.tid = ffs2.tid
						        AND ffs1.pf0px IS NOT null
						        AND ffs2.pf39px IS NOT null
						)';
END IF;

FOR i IN 1..39 DO
	EXECUTE IMMEDIATE  'INSERT INTO #TEMPTABLE1(
							SELECT round(pf'||:i||'py + ify, '||:granularity||') AS lat, 
						            round(pf'||:i||'px + ifx, '||:granularity||') AS lon 
							FROM tuk3_ts_mj.frame_format_15_avg 
							WHERE occupancy'||:i||' '||:pointtype||' occupancy'||:i - 1||' AND fgcid = '||:fgcidin||'
					    )';
END FOR;
	        
output_table = select lat, lon, count(*) as weight from #TEMPTABLE1 group by lat, lon;

DROP TABLE #TEMPTABLE1;

END;