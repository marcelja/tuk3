select sum(distance) as sum_distance,id from
(
select t1.id, new ST_POINT(t1.lon, t1.lat).st_srid(4326).st_transform(4326).st_distance(  new ST_POINT(t2.lon, t2.lat).st_srid(4326).st_transform(4326)   ) as distance from 
(select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean
-- where id = 22223
order by seconds) t1,
(select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean 
-- where id = 22223
order by seconds) t2
where t1.row_num = t2.row_num-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
) group by id order by sum_distance desc
