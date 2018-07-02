CREATE TYPE TUK3_TS_MJ.framegroup_locations_granularity_type AS TABLE (
            lat real, lon real, weight int
);

create procedure TUK3_TS_MJ.locations_for_framegroup_granularity(in fgcidin int, in granularity int, out output_table TUK3_TS_MJ.framegroup_locations_granularity_type)
LANGUAGE SQLSCRIPT AS
 BEGIN 

declare i int;

CREATE LOCAL TEMPORARY TABLE #TEMPTABLE1 (lat float(9), lon float(9));

FOR i IN 0..39 DO
	EXECUTE IMMEDIATE  'INSERT INTO #TEMPTABLE1(
							SELECT round(pf'||:i||'py + ify, '||:granularity||') AS lat, 
						            round(pf'||:i||'px + ifx, '||:granularity||') AS lon 
							FROM tuk3_ts_mj.frame_format_15 
							WHERE fgcid = '||:fgcidin||'
					    )';
END FOR;
	        
output_table = select lat, lon, count(*) as weight from #TEMPTABLE1 group by lat, lon;

DROP TABLE #TEMPTABLE1;

END;