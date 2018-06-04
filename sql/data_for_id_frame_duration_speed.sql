drop type id_infos_speed;
create type id_infos_speed as table (lon float(7), lat float(7), fgcid int, frame int, occupancy tinyint, speed tinyint);


drop  procedure data_for_id_speed_occupancy;
    create procedure data_for_id_speed_occupancy(in id int, in frame_duration int, in points_per_frame_group int, out OUTPUT_TABLE "TUK3_TS_MJ"."ID_INFOS_SPEED")
LANGUAGE SQLSCRIPT AS
 BEGIN 
  
    
helper = select
seconds,
    lon,
    lat,
    to_int(seconds/(:frame_duration * :points_per_frame_group)) as FGCID,
    to_int(mod(seconds,(:frame_duration * :points_per_frame_group)) / :frame_duration) as frame,
    occupancy,
    speed
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

OUTPUT_TABLE = select lon, lat, FGCID, :helper.frame, occupancy, speed from :helper, :helper2 where :helper.seconds = :helper2.seconds order by :helper2.seconds;
end;


---------------- AVERAGE LON AND LAT -------------------


drop type id_infos_speed;
create type id_infos_speed as table (lon float(7), lat float(7), fgcid int, frame int, occupancy tinyint, speed tinyint);


drop  procedure data_for_id_speed_occupancy;
    create procedure data_for_id_speed_occupancy(in id int, in frame_duration int, in points_per_frame_group int, out OUTPUT_TABLE "TUK3_TS_MJ"."ID_INFOS_SPEED")
LANGUAGE SQLSCRIPT AS
 BEGIN 
  
    
helper = select
seconds,
    lon,
    lat,
    to_int(seconds/(:frame_duration * :points_per_frame_group)) as FGCID,
    to_int(mod(seconds,(:frame_duration * :points_per_frame_group)) / :frame_duration) as frame,
    occupancy,
    speed
    from "SHENZHEN"
    where id = :id
    order by seconds;
    
        
helper2 = select min(seconds) as seconds, avg(lon) as lon, avg(lat) as lat, frame
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

OUTPUT_TABLE = select :helper2.lon, :helper2.lat, FGCID, :helper.frame, occupancy, speed from :helper, :helper2 where :helper.seconds = :helper2.seconds order by :helper2.seconds;
end;
