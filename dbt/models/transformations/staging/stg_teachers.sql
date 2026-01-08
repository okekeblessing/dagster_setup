select
    teacher_id,
    lower(title) AS title,
    lower(first_name) AS first_name,
    lower(last_name) AS last_name,
    toDate(date_of_birth) AS date_of_birth,
    age,
    lower(teacher_email) AS teacher_email,
    teacher_phone_no,
    school_id,
    lower(subject_taught) AS subject_taught,
    trained_teacher,
    lower(education_level) AS education_level,
    years_of_experience
from {{ source('raw', 'teachers') }}
