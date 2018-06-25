select sum_table.id, sum_distance*2.4/1000+(sum_seconds*0.1*48/3600)+11*num_rides as profit, sum_distance*2.4/1000 as profit_distance, sum_seconds*0.1*48/3600 as profit_waiting, 11*num_rides as profit_taxi_start from

----- calculate sum of distances and sum of seconds for each id
(
    select sum(distance) as sum_distance,sum(scnds) as sum_seconds,id from
    (
    select t1.id, t2.seconds-t1.seconds as scnds, new ST_POINT(t1.lon, t1.lat).st_srid(4326).st_transform(4326).st_distance(  new ST_POINT(t2.lon, t2.lat).st_srid(4326).st_transform(4326)   ) as distance from 
    (select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean
    -- where id = 22223
    order by seconds) t1,
    (select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean 
    -- where id = 22223
    order by seconds) t2
    where t1.row_num = t2.row_num-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
    ) group by id order by sum_distance desc
) sum_table,

----- calculate number of rides
(
    select t1.id, count(t1.id) as num_rides from 
    (select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean
    -- where id = 22223
    order by seconds) t1,
    (select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean 
    -- where id = 22223
    order by seconds) t2
    where t1.row_num = t2.row_num-1 and t1.occupancy=1 and t2.occupancy=0 and t1.id=t2.id
    group by t1.id
) num_rides
where sum_table.id=num_rides.id
order by id


-- a bit more performance

select sum_table.id, sum_distance*2.4/1000+(sum_seconds*0.1*48/3600)+11*num_rides as profit, sum_distance*2.4/1000 as profit_distance, sum_seconds*0.1*48/3600 as profit_waiting, 11*num_rides as profit_taxi_start from

----- calculate sum of distances and sum of seconds for each id
(
    select sum(distance) as sum_distance,sum(scnds) as sum_seconds,id from
    (
    select t1.id, t2.seconds-t1.seconds as scnds, new ST_POINT(t1.lon, t1.lat).st_srid(4326).st_transform(4326).st_distance(  new ST_POINT(t2.lon, t2.lat).st_srid(4326).st_transform(4326)   ) as distance from 
    (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
    -- where id = 22223
    order by seconds) t1,
    (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
    -- where id = 22223
    order by seconds) t2
    where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
    ) group by id order by sum_distance desc
) sum_table,

----- calculate number of rides
(
    select t1.id, count(t1.id) as num_rides from 
    (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
    -- where id = 22223
    order by seconds) t1,
    (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
    -- where id = 22223
    order by seconds) t2
    where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=0 and t1.id=t2.id
    group by t1.id
) num_rides
where sum_table.id=num_rides.id

-- slightly more performant :)
-- used haversine formula. See example here: https://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
select sum_table.id, sum_distance*2.4/1000+(sum_seconds*0.1*48/3600)+11*num_rides as profit, sum_distance*2.4/1000 as profit_distance, sum_seconds*0.1*48/3600 as profit_waiting, 11*num_rides as profit_taxi_start from

----- calculate sum of distances and sum of seconds for each id
(
    select sum(distance) as sum_distance,sum(scnds) as sum_seconds,id from
    (
    select t1.id, t2.seconds-t1.seconds as scnds, 1000 * 6371 * 2 * asin(sqrt(power(sin((t2.lat * 3.14159265 / 180 - t1.lat * 3.14159265 / 180)/2),2) + cos(t1.lat * 3.14159265 / 180) * cos(t2.lat * 3.14159265 / 180) * power(sin((t2.lon * 3.14159265 / 180 - t1.lon * 3.14159265 / 180)/2),2))) as distance from 
    (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
    -- where id = 22223
    order by seconds) t1,
    (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
    -- where id = 22223
    order by seconds) t2
    where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
    ) group by id order by sum_distance desc
) sum_table,

----- calculate number of rides
(
    select t1.id, count(t1.id) as num_rides from 
    (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
    -- where id = 22223
    order by seconds) t1,
    (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
    -- where id = 22223
    order by seconds) t2
    where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=0 and t1.id=t2.id
    group by t1.id
) num_rides
where sum_table.id=num_rides.id
