set schema tuk3_ts_mj;
drop procedure profit_frame;

create procedure profit_frame()
LANGUAGE SQLSCRIPT AS
BEGIN

 
DECLARE i,j tinyINT;
declare query nvarchar(1000);
declare query2 nvarchar(1000);

declare old_point_x float;
declare old_point_y float;
declare current_point_helper float;
declare current_occupancy_helper tinyint;
declare prev_occupancy_helper tinyint;
declare sum_distance int = 0;
declare sum_seconds int = 0;
declare num_rides int = 0;

declare cursor ids for select distinct tid from "TUK3_TS_MJ"."FRAME_FORMAT_15" ;


Create global TEMPORARY TABLE helper123 (id int, distance float, totaltime int, num_rides int);

for id_row as ids DO  
    declare cursor fgs for select distinct fgcid from "TUK3_TS_MJ"."FRAME_FORMAT_15" where tid =  id_row.tid order by fgcid;
    for fg as fgs DO 
        for i in 0 .. 39 DO
    
        execute immediate 'select PF'||i||'PX
                           from "TUK3_TS_MJ"."FRAME_FORMAT_15" 
                           where fgcid = '||fg.fgcid||'
                           and tid = '||id_row.tid||';' into current_point_helper;
    
        execute immediate 'select occupancy'||i||'
                           from "TUK3_TS_MJ"."FRAME_FORMAT_15" 
                           where fgcid = '||fg.fgcid||'
                           and tid = '||id_row.tid||';' into current_occupancy_helper;
                           
		if fg.fgcid = 0 and :i = 0 then
	    	continue;
	    end if;
	    
	    if :i = 0 then
	    	execute immediate 'select occupancy39
	                       from "TUK3_TS_MJ"."FRAME_FORMAT_15" 
	                       where fgcid = '||fg.fgcid - 1||'
	                       and tid = '||id_row.tid||';' into prev_occupancy_helper;
	    else
		    execute immediate 'select occupancy'||i-1||'
		                       from "TUK3_TS_MJ"."FRAME_FORMAT_15" 
		                       where fgcid = '||fg.fgcid||'
		                       and tid = '||id_row.tid||';' into prev_occupancy_helper;
		end if;
       
        if :current_point_helper is NULL then
            continue;
        end if;
    
        if :current_occupancy_helper = 0 then
            old_point_x = null;
            continue;
        end if;
        
        if :current_point_helper is not NULL and :current_occupancy_helper = 1 and old_point_x is not null then
            query = 'select new ST_POINT(ifx + PF'||i||'PX, ify + PF'||i||'PY).st_srid(4326).st_transform(4326)
                        .st_distance(new ST_POINT('||:old_point_x||', '||:old_point_y||').st_srid(4326).st_transform(4326)) + '||:sum_distance||'
                     from "TUK3_TS_MJ"."FRAME_FORMAT_15" 
            
                     where tid = '||id_row.tid||' 
                     and fgcid = '||fg.fgcid||'';
        
            execute immediate query  into sum_distance;
            
            query2 = 'select 15 + '||:sum_seconds||' from dummy';
	        execute immediate query2 into sum_seconds;
        end if;
            
        if :current_point_helper is not NULL and :current_occupancy_helper = 1 then
            execute immediate 'select ify + PF'||i||'PY
                               from "TUK3_TS_MJ"."FRAME_FORMAT_15"  
                               where tid = '||id_row.tid||' 
                               and fgcid = '||fg.fgcid||'' into old_point_y;
    
            execute immediate 'select ifx + PF'||i||'PX
                               from "TUK3_TS_MJ"."FRAME_FORMAT_15"  
                               where tid = '||id_row.tid||' 
                               and fgcid = '||fg.fgcid||'' into old_point_x;
            continue;
        end if;
    
        end for;
    end for;
    
    insert into helper123 values (id_row.tid, :sum_distance, :sum_seconds, :num_rides);
end for;

select * from helper123 order by distance desc;

end;