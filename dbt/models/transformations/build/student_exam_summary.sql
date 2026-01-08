with exams as (
    select student_id, score
    from {{ ref('stg_examinations') }}
)

select
    student_id,
    count(score) as total_exams,
    avg(score) as avg_score
from exams
group by student_id