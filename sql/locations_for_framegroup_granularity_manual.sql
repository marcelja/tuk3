select lat, lon, count(*) as weight from (
    select round(frame_format_15.ify + frame_format_15.pf0py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf0px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf1py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf1px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf2py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf2px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf3py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf3px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf4py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf4px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf5py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf5px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf6py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf6px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf7py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf7px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf8py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf8px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf9py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf9px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf9py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf9px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf10py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf10px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf11py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf11px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf12py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf12px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf13py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf13px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf14py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf14px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf15py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf15px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf16py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf16px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf17py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf17px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf18py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf18px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf19py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf19px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf20py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf20px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf21py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf21px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf22py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf22px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf23py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf23px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf24py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf24px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf25py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf25px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf26py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf26px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf27py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf27px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf28py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf28px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf29py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf29px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf30py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf30px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf31py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf31px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf32py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf32px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf33py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf33px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf34py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf34px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf35py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf35px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf36py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf36px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf37py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf37px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf38py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf38px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
    union all
    select round(frame_format_15.ify + frame_format_15.pf39py, 6) as lat, 
           round(frame_format_15.ifx + frame_format_15.pf39px, 6) as lon 
    from frame_format_15 
    where fgcid = 0
)
group by lat, lon;