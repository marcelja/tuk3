CREATE FUNCTION get_timeframe_from_seconds (seconds int) RETURNS frame int

LANGUAGE SQLSCRIPT AS

BEGIN

 select to_int(seconds / 600) into frame from dummy;

END;

drop procedure changepoints_for_point_format;

create procedure changepoints_for_point_format(in framebegin int, in framelength smallint, in granularity tinyint, in pointtype char, out output_table TUK3_TS_MJ.changepointstype)
LANGUAGE SQLSCRIPT AS
 BEGIN 
      
if :pointtype = '>' then 
    output_table = 
    select round(t1.lat, granularity) as lat,
           round(t1.lon, granularity) as lon,
           count(*) as weight
    from 
        (select id, lat, lon, occupancy, rid
        from shenzhen_sorted
        where seconds >= framebegin
        and seconds < framebegin + framelength
        order by seconds) t1,
        (select id, lat, lon, occupancy, rid
        from shenzhen_sorted 
        where seconds >= framebegin
        and seconds < framebegin + framelength
        order by seconds) t2
    where t1.rid = t2.rid-1
    and t1.occupancy=1
    and t2.occupancy=0
    
    and t1.id=t2.id
    group by round(t1.lat, granularity), round(t1.lon, granularity);

else
    output_table =
    select round(t1.lat, granularity) as lat,
           round(t1.lon, granularity) as lon,
           count(*) as weight
    from 
        (select id, lat, lon, occupancy, rid
        from shenzhen_sorted
        where seconds >= framebegin
        and seconds < framebegin + framelength
        order by seconds) t1,
        (select id, lat, lon, occupancy, rid
        from shenzhen_sorted
        where seconds >= framebegin
        and seconds < framebegin + framelength
        order by seconds) t2
    where t1.rid = t2.rid-1
    and t1.occupancy=0
    and t2.occupancy=1
    and t1.id=t2.id
    group by round(t1.lat, granularity), round(t1.lon, granularity);
end if;
end;

-- call changepoints_for_point_format(50000, 600, 6, '>', ?);
