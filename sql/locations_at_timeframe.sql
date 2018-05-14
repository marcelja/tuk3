drop type latlon;
create type latlon as table (lat float(9), lon float(9));

drop procedure locations_at_timeframe;
create procedure locations_at_timeframe(in fgcidin int, in colnumber int, out output_table latlon)
LANGUAGE SQLSCRIPT AS
 BEGIN 

declare lon, lat nvarchar(5);

CREATE LOCAL TEMPORARY TABLE #TEMPTABLE (lat float(9), lon float(9));

select CONCAT('PF', CONCAT(colnumber, 'PX')) into lon from dummy;
select CONCAT('PF', CONCAT(colnumber, 'PY')) into lat from dummy;

EXECUTE immediate 'insert into #TEMPTABLE( select FRAMEFORMAT2.'||:lat||' + ify as lat, FRAMEFORMAT2.'||:lon||' + ifx as lon from "TUK3_TS_MJ"."FRAMEFORMAT2" 
where fgcid = '||:fgcidin||' and FRAMEFORMAT2.'||:lat||' is not NULL)';

output_table = select * from #TEMPTABLE;
DROP TABLE #TEMPTABLE;

end;
