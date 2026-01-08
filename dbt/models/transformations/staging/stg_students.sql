SELECT
    student_id,
    lower(first_name) AS first_name,
    lower(last_name) AS last_name,
    lower(gender) AS gender,
    date_of_birth,
    age,
    lower(state_of_origin) AS state_of_origin,
    lower(state_of_residence) AS state_of_residence,
    lower(student_email) AS student_email,
    student_phone_no,
    school_id,
    lower(parent_name) AS parent_name,
    parent_phone_no,
    lower(parent_email) AS parent_email,
    lower(parent_address) AS parent_address,
    NIN
FROM {{ source('raw', 'students') }}
