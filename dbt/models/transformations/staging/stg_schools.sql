SELECT
    school_id,
    lower(school_name) AS school_name,
    lower(state) AS state,
    lower(lga) AS lga,
    lower(school_address) AS school_address,
    lower(school_type) AS school_type,
    lower(institution_level) AS institution_level,
    no_of_students,
    no_of_teachers,
    contact_info
FROM {{ source('raw', 'schools') }}
