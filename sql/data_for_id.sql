drop type id_infos;
create type id_infos as table (lon float(7), lat float(7), fgcid int, frame int);


drop  procedure data_for_id;
    create procedure data_for_id(in id int , out OUTPUT_TABLE "TUK3_TS_MJ"."ID_INFOS" )
LANGUAGE SQLSCRIPT AS
 BEGIN 
  
    
helper = select
timestamp,
    lon,
    lat,
    hour(timestamp) * 6 + to_int(minute(timestamp)/10) as FGCID,
    get_timeframe(timestamp) as frame
    from "TAXI"."SHENZHEN"
    where id = :id
    order by timestamp;
    
        
helper2 = select min(timestamp) as ts, frame
from (
select
timestamp,
    lon,
    lat,
    hour(timestamp) * 6 + to_int(minute(timestamp)/10) as FGCID,
    get_timeframe(timestamp) as frame
    from "TAXI"."SHENZHEN"
    where id = :id
    order by timestamp

    )
    group by fgcid, frame
    order by ts;

OUTPUT_TABLE = select lon, lat, FGCID, :helper.frame from :helper, :helper2 where :helper.timestamp = :helper2.ts order by :helper2.ts;
end;


drop FUNCTION get_timeframe;

CREATE FUNCTION get_timeframe (ts timestamp) RETURNS frame int
LANGUAGE SQLSCRIPT AS

BEGIN
 select mod(minute(ts), 10) * 4 + to_int(second(ts) / 15) into frame from dummy;
END;


-- OLD

drop procedure data_for_id;

create procedure data_for_id(in id int , out OUTPUT_TABLE "TUK3_TS_MJ"."ID_INFOS" )
LANGUAGE SQLSCRIPT AS
 BEGIN 
  
OUTPUT_TABLE = select
    lon,
    lat,
    hour(timestamp) as FGCID,
    get_timeframe(timestamp) as frame
    from "TAXI"."SHENZHEN"
    where id = :id
    order by timestamp;

 END;

drop FUNCTION get_timeframe;

CREATE FUNCTION get_timeframe (ts timestamp) RETURNS frame int

LANGUAGE SQLSCRIPT AS

BEGIN

 select to_int((minute(ts) * 10 + second(ts))/30) into frame from dummy;

END;
