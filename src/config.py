# Searches are a list of tuples (search_term, category)
# The categories are used in remotive.io
searches = [
    ('sql', 'Data'),
    ('database', 'Data'),
    ('database', 'DevOps/Sysadmin'),
    ('postgresql', 'Data'),
    ('', 'Customer Service'),
    ('data analyst', 'Data'),
    ('data analyst', 'Business'),
    ('data engineer', 'Data'),
    ('business analyst', 'Data')
    ]

excluded_terms = [
    'Developer',
    'Software Engineer',
    'Full Stack Engineer',
    'Back End Engineer',
    'Backend Engineer',
    'Front End Engineer',
    'Frontend Engineer',
    'Front-End Engineer',
    'Node JS',
    'NodeJS'
    ]

# Number of days since the job was published
# Older jobs are dropped.
since = 1
