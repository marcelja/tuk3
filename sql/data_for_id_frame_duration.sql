drop type id_infos;
create type id_infos as table (lon float(7), lat float(7), fgcid int, frame int);


drop  procedure data_for_id;
    create procedure data_for_id(in id int, in frame_duration int, in points_per_frame_group int, out OUTPUT_TABLE "TUK3_TS_MJ"."ID_INFOS")
LANGUAGE SQLSCRIPT AS
 BEGIN 
  
    
helper = select
seconds,
    lon,
    lat,
    to_int(seconds/(:frame_duration * :points_per_frame_group)) as FGCID,
    to_int(mod(seconds,(:frame_duration * :points_per_frame_group)) / :frame_duration) as frame
    from "SHENZHEN"
    where id = :id
    order by seconds;
    
        
helper2 = select min(seconds) as seconds, frame
from (
select
seconds,
    lon,
    lat,
    to_int(seconds/(:frame_duration * :points_per_frame_group)) as FGCID,
    to_int(mod(seconds,(:frame_duration * :points_per_frame_group)) / :frame_duration) as frame
    from "SHENZHEN"
    where id = :id
    order by seconds

    )
    group by fgcid, frame
    order by seconds;

OUTPUT_TABLE = select lon, lat, FGCID, :helper.frame from :helper, :helper2 where :helper.seconds = :helper2.seconds order by :helper2.seconds;
end;
