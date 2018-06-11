drop type id_infos_speed;
create type id_infos_speed as table (lon float(7), lat float(7), fgcid int, frame int, occupancy tinyint, speed tinyint);

drop procedure data_for_id_speed_occupancy_ts_min;
create procedure data_for_id_speed_occupancy_ts_min(in id int , in frame_duration int, in points_per_frame_group int, out OUTPUT_TABLE id_infos_speed )
LANGUAGE SQLSCRIPT AS
 BEGIN 
  
    
helper = select
timestamp,
    lon,
    lat,
    to_int((hour(timestamp)*60+minute(timestamp))*60/(:frame_duration * :points_per_frame_group)) as FGCID,
    to_int(mod((hour(timestamp)*60+minute(timestamp))*60,(:frame_duration * :points_per_frame_group)) / :frame_duration) as frame, 
    occupancy,
    speed
    from "SHENZHEN"
    where id = :id
    order by timestamp;
    
        
helper2 = select min(timestamp) as ts, frame
from (
select
timestamp,
    lon,
    lat,
    to_int((hour(timestamp)*60+minute(timestamp))*60/(:frame_duration * :points_per_frame_group)) as FGCID,
    to_int(mod((hour(timestamp)*60+minute(timestamp))*60,(:frame_duration * :points_per_frame_group)) / :frame_duration) as frame
    from "SHENZHEN"
    where id = :id
    order by timestamp

    )
    group by fgcid, frame
    order by ts;

OUTPUT_TABLE = select lon, lat, FGCID, :helper.frame, occupancy, speed from :helper, :helper2 where :helper.timestamp = :helper2.ts order by :helper2.ts;
end;


---------------- AVERAGE LON AND LAT -------------------


drop procedure data_for_id_speed_occupancy_ts_avg;
create procedure data_for_id_speed_occupancy_ts_avg(in id int , in frame_duration int, in points_per_frame_group int, out OUTPUT_TABLE id_infos_speed )
LANGUAGE SQLSCRIPT AS
 BEGIN 
  
    
helper = select
timestamp,
    lon,
    lat,
    to_int((hour(timestamp)*60+minute(timestamp))*60/(:frame_duration * :points_per_frame_group)) as FGCID,
    to_int(mod((hour(timestamp)*60+minute(timestamp))*60,(:frame_duration * :points_per_frame_group)) / :frame_duration) as frame,
    occupancy,
    speed
    from "SHENZHEN"
    where id = :id
    order by timestamp;
    
        
helper2 = select min(timestamp) as ts, avg(lon) as lon, avg(lat) as lat, frame
from (
select
timestamp,
    lon,
    lat,
    to_int((hour(timestamp)*60+minute(timestamp))*60/(:frame_duration * :points_per_frame_group)) as FGCID,
    to_int(mod((hour(timestamp)*60+minute(timestamp))*60,(:frame_duration * :points_per_frame_group)) / :frame_duration) as frame
    from "SHENZHEN"
    where id = :id
    order by timestamp

    )
    group by fgcid, frame
    order by ts;

OUTPUT_TABLE = select :helper2.lon, :helper2.lat, FGCID, :helper.frame, occupancy, speed from :helper, :helper2 where :helper.timestamp = :helper2.ts order by :helper2.ts;
end;
