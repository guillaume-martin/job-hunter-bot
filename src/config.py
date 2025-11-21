# Searches are a list of tuples (search_term, category)
# The categories are used in remotive.io
searches = [
    # "database",
    # "dba",
    # "postgresql",
    # "sql",
    "python",
    # "aws",
    # "data analyst",
    # "data engineer",
    # "backend engineer",
    # "cloud data engineer",
    # "cloud engineer",
    # "database engineer",
    # "database administrator",
    # "database manager",
    # "etl developer",
    # "devops engineer",
    # "data manager",
    # "analytics engineer",
    # "data software engineer",
    # "data architect",
    # "dataops"
]

sites = [
    # "104",
    "remoteok",
    # "remotive",
    # "trulyremote"
]

# Number of days since the job was published
# Older jobs are dropped.
since = 2

# AI settings
api_url = "https://openrouter.ai/api/v1/chat/completions"
api_url = "https://api.mistral.ai/v1/chat/completions"
model = "mistral-small-latest"
# model = "mistralai/mistral-7b-instruct:free"
# model = "mistralai/mistral-small-24b-instruct-2501:free"
# model = "openai/gpt-oss-20b:free"
temperature = 0.7
timeout = 60
prompt_file = "src/data/prompt.txt"
resume_file = "src/data/resume.txt"
apply_threshold = 50    # Minimum job `match_score` (0-100) required to select a job for application.