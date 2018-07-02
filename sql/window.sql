-- example calls
 call taxis_in_window(min_lat => 22.1, max_lat => 22.3, min_lon => 114.1, max_lon => 114.3, output_table => ?);
 call taxis_in_window(min_lat => 22.1, max_lat => 22.3, min_lon => 114.1, max_lon => 114.3, start_time => 50000, output_table => ?); 
 call taxis_in_window(min_lat => 22.1, max_lat => 22.3, min_lon => 114.1, max_lon => 114.3, start_time => 50000, end_time => 60000, output_table => ?);

drop type id_ts;
CREATE TYPE id_ts AS TABLE (
            id int,
            seconds int
);

drop procedure taxis_in_window;
create procedure taxis_in_window(min_lat float, max_lat float, min_lon float, max_lon float, start_time int default 0, end_time int default 86400, out output_table id_ts)
LANGUAGE SQLSCRIPT AS
 BEGIN 
 
 output_table = 
 select distinct id, seconds
 from "TUK3_TS_MJ"."SHENZHEN_SORTED"
 where lat >= min_lat
 and lat <= max_lat
 and lon >= min_lon
 and lon <= max_lon
 and seconds >= start_time
 and seconds <= end_time;
 
 end;
 
-- procedure working on ints 
drop  procedure taxis_in_window_ints;
create procedure taxis_in_window_ints(min_lat float, max_lat float, min_lon float, max_lon float, start_time int default 0, end_time int default 86400, out output_table id_ts)
LANGUAGE SQLSCRIPT AS
 BEGIN 

 output_table = 
 select distinct id, timehour * 3600 + timeminute * 60 + timesecond as seconds
 from "TUK3_TS_MJ"."SHENZHEN_INT"
 where (lat1 > to_int(:min_lat) or (lat1 = to_int(:min_lat) and lat2 >= to_int(mod(:min_lat, 1) * 10000)))
 and (lat1 < to_int(:max_lat) or (lat1 = to_int(:max_lat) and lat2 <= to_int(mod(:max_lat, 1) * 10000)))
 and (lon1 > to_int(:min_lon) or (lon1 = to_int(:min_lon) and lon2 >= to_int(mod(:min_lon, 1) * 10000)))
 and (lon1 < to_int(:max_lon) or (lon1 = to_int(:max_lon) and lon2 <= to_int(mod(:max_lon, 1) * 10000)))
 and (to_int(:end_time / 3600) > timehour
 or (to_int(:end_time / 3600) = timehour and mod(to_int(:end_time / 60), 60) > timeminute)
 or (to_int(:end_time / 3600) = timehour and mod(to_int(:end_time / 60), 60) = timeminute and mod(:end_time , 60) >= timesecond))
 and (to_int(:start_time / 3600) < timehour
 or (to_int(:start_time / 3600) = timehour and mod(to_int(:start_time / 60), 60) < timeminute)
 or (to_int(:start_time / 3600) = timehour and mod(to_int(:start_time / 60), 60) = timeminute and mod(:start_time , 60) <= timesecond));
 
 end;
