with exams as (
    select e.student_id, e.score
    from {{ ref('stg_examinations') }} e
),
students as (
    select student_id, school_id
    from {{ ref('stg_students') }}
),
joined as (
    select s.school_id, e.score
    from exams e
    join students s on e.student_id = s.student_id
)

select
    sc.school_id AS student_id,
    sc.school_name,
    count(j.score) as num_exams,
    avg(j.score) as avg_score,
    sc.no_of_students,
    sc.no_of_teachers
from joined j
join {{ ref('stg_schools') }} sc on j.school_id = sc.school_id
group by sc.school_id, sc.school_name, sc.no_of_students, sc.no_of_teachers