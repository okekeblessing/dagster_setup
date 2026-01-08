with exams as (
    select student_id, subject_name, score
    from {{ ref('stg_examinations') }}
)

select
    t.teacher_id,
    t.first_name,
    t.last_name,
    t.school_id,
    t.subject_taught,
    avg(e.score) as avg_student_score
from {{ ref('stg_teachers') }} t
left join exams e on e.subject_name = t.subject_taught
group by t.teacher_id, t.first_name, t.last_name, t.school_id, t.subject_taught
