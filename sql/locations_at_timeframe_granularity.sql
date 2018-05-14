drop type latlonweight;
create type latlonweight as table (lat float(9), lon float(9), weight smallint);

drop procedure locations_at_timeframe_granularity;
create procedure locations_at_timeframe_granularity(in fgcidin int, in colnumber int, in granularity int, out output_table latlonweight)
LANGUAGE SQLSCRIPT AS
BEGIN 

declare lon, lat nvarchar(7);

CREATE LOCAL TEMPORARY TABLE #TEMPTABLE1 (lat float(9), lon float(9), weight smallint);

select CONCAT('PF', CONCAT(colnumber, 'PX')) into lon from dummy;
select CONCAT('PF', CONCAT(colnumber, 'PY')) into lat from dummy;

EXECUTE immediate 'insert into #TEMPTABLE1(
                        select lat, lon, count(*) as weight from (
                            select round(FRAMEFORMAT2.'||:lat||' + ify, '||:granularity||') as lat,
                                   round(FRAMEFORMAT2.'||:lon||' + ifx, '||:granularity||') as lon 
                            from "TUK3_TS_MJ"."FRAMEFORMAT2" 
                            where fgcid = '||:fgcidin||'
                            and FRAMEFORMAT2.'||:lat||' is not NULL)
                        group by lat, lon)';

output_table = select * from #TEMPTABLE1;
DROP TABLE #TEMPTABLE1;

end;
