# Searches are a list of tuples (search_term, category)
# The categories are used in remotive.io
searches = [
    'sql',
    'database',
    'postgresql',
    'customer service',
    'customer support',
    'data analyst',
    'data engineer',
    'business analyst'
    ]

excluded_terms = [
    # 'Developer',
    'Software Engineer',
    'Full Stack',
    'Backend Engineer',
    'Frontend Engineer',
    'NodeJS',
    'Node Developer',
    'DevOps',
    'Ruby',
    'WordPress',
    'PhP'
    ]

# Number of days since the job was published
# Older jobs are dropped.
since = 10
