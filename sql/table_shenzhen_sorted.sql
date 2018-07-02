create column table shenzhen_sorted  as (select *, ROW_NUMBER() OVER ( order by  id, seconds) as rid from  "TUK3_TS_MJ"."SHENZHEN_CLEAN" order by id, seconds);
ALTER TABLE shenzhen_sorted ADD PRIMARY KEY (rid);
