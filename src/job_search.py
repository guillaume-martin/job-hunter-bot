""" Searches jobs offers on a selection of web sites
"""
# -*- coding: utf-8 -*-
from datetime import datetime

import remotive
import wwr

SEARCHES = [
    # ('sql', 'Data'),
    ('database', 'Data'),
    # ('database', 'DevOps/Sysadmin'),
    # ('postgresql', 'Data'),
    # ('', 'Customer Service'),
    # ('data analyst', 'Data'),
    # ('data analyst', 'Business'),
    # ('data engineer', 'Data'),
    # ('business analyst', 'Data')
    ]

EXCLUDE_TERMS = [
    'Developer',
    'Software Engineer',
    'Full Stack Engineer',
    'Back End Engineer'
    ]

# Number of days since the job was published
# Older jobs are dropped.
SINCE = 1

def find_jobs(searches):
    """ Find jobs from search terms on multiple web sites
        The jobs are stored in a list of dictionary.
        Each dictionary is a job post:
        {
            "company": "Acme, Inc.",
            "title": "Director of Engineering",
            "url": "https://remotive.io/dir-engineer",
            "date_published": "2020-11-12"
        }
    """
    jobs = []
    for term, category in searches:

        # get jobs from Remotive
        print("Searching Remotive jobs...")
        jobs += remotive.get_jobs(term, category)

        # get jobs from wwr
        print("Searching We Work Remotely jobs...")
        jobs += wwr.get_jobs(term)

    return jobs


def save_jobs(jobs):
    
    output = "company,title,date,url\n"
    for job in jobs:
        output += '"' + job['company'] + '",'
        output += '"' + job['title'] + '",'
        output += '"' + job['date_published'] + '",'
        output += '"' + job['url'] + '"\n'
    
    # print(output)
    with open('../output/jobs.csv', 'w') as file:
        file.write(output)
        
def print_jobs(jobs):
    
    html = '<div>'
    
    for job in jobs:
        html +=  (
            "<p>"
            f"<a href='{job['url']}'>{job['title']}</a>&nbsp@&nbsp"
            f"{job['company']}&nbsp"
            f"({job['date_published']})"
            "</p>"
            )
    
    html += '</div>'
        
    # print(html)
    with open('../output/jobs.html', 'w') as file:
        file.write(html)
        
    
def main():
    # Extract jobs from web sites and save them in a list
    jobs = find_jobs(SEARCHES)

    # Remove duplicates
    print("Removing duplicates...")
    single_jobs = []
    for job in jobs:
        if job not in single_jobs:
            single_jobs.append(job)
    print(f"Removed {len(jobs) - len(single_jobs)} jobs.")
            
    # Remove older posts
    print("Removing older jobs...")
    before = len(single_jobs)
    for index, job in enumerate(single_jobs):
        date_published = datetime.strptime(job['date_published'], '%Y-%m-%d')
        days_since_published = (datetime.now() - date_published).days
        
        if days_since_published > SINCE:
            single_jobs.remove(job)
            print(job in single_jobs)
            
    print(f"Removed {before - len(single_jobs)} jobs")
    
    # Remove unwanted jobs
    for job in single_jobs:
        for exclude in EXCLUDE_TERMS:
            if exclude in job['title']:
                single_jobs.remove(job)
    
    # save_jobs(single_jobs)
    # print("Jobs saved.")
    
    print_jobs(single_jobs)
    
if __name__ == '__main__':
    main()
