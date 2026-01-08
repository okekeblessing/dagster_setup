SELECT
    reg_number,
    student_id,
    lower(exam_type) AS exam_type,
    exam_year,
    lower(subject_name) AS subject_name,
    score,
    lower(grade) AS grade,
    center_id,
    lower(exam_center) AS exam_center
FROM {{ source('raw', 'examinations') }}
