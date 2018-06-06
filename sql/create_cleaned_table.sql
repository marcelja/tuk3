drop table "TUK3_TS_MJ"."SHENZHEN_CLEAN" ;
create column table SHENZHEN_CLEAN like "TAXI"."SHENZHEN";

insert into "TUK3_TS_MJ"."SHENZHEN_CLEAN"(
select distinct * from "TAXI"."SHENZHEN"
where id not in ( select id from "TAXI"."SHENZHEN" group by id  having count(id) < 500)
and id not in ( 
    select id from (
        select id, count( occupancy) as c 
        from "TAXI"."SHENZHEN"
        where occupancy = 1 
        group by id , occupancy
        ) 
    where c < 120)
and lon < 116
and lon > 113
and lat > 22
and lat < 23.5);
