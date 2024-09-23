import requests
from bs4 import BeautifulSoup

def search_jobs(job_title, location):
    url = f"https://www.indeed.com/jobs?q={job_title}&l={location}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    for job_card in soup.find_all('div', class_='jobsearch-SerpJobCard'):
        title = job_card.find('h2', class_='title').text.strip()
        company = job_card.find('span', class_='company').text.strip()
        link = job_card.find('a', class_='jobtitle')['href']
        jobs.append({
            'title': title,
            'company': company,
            'link': f"https://www.indeed.com{link}"
        })

    return jobs

# Example usage:
# jobs = search_jobs('Software Engineer', 'New York')
# for job in jobs:
#     print(f"{job['title']} at {job['company']}")
#     print(job['link'])
