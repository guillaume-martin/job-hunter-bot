# Searches are a list of tuples (search_term, category)
# The categories are used in remotive.io
searches = [
    'sql',
    'database',
    'postgresql',
    'customer',
    'data analyst',
    'data engineer',
    'business analyst'
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
since = 7
