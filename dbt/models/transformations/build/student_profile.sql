select
    s.student_id,
    concat(s.first_name, ' ', s.last_name) as full_name,
    sc.school_name,
    p.total_exams,
    p.avg_score,
    case 
        when p.avg_score >= 70 then 'Excellent'
        when p.avg_score >= 50 then 'Average'
        else 'Poor'
    end as performance_band
from {{ ref('stg_students') }} s
left join {{ ref('student_exam_summary') }} p on s.student_id = p.student_id
left join {{ ref('stg_schools') }} sc on s.school_id = sc.school_id