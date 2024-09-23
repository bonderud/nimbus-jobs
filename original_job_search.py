visited_urls = set()

def filter_duplicate_jobs(jobs):
    """Filter out jobs already seen in previous searches."""
    global visited_urls
    filtered_jobs = []
    for job in jobs:
        job_url_hash = hashlib.md5(job['url'].encode()).hexdigest()
        if job_url_hash not in visited_urls:
            filtered_jobs.append(job)
            visited_urls.add(job_url_hash)
    return filtered_jobs

def limit_jobs(jobs, limit=5):
    """Limit the number of job results returned."""
    return jobs[:limit]

# Each scraping function should accept a dynamic set of criteria (search_term, location, etc.)
def search_wellfound(search_term, location, job_type):
    url = f"https://wellfound.com/role/l/{search_term}/united-states"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch Wellfound jobs. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []
    for job in soup.find_all('div', class_='job-listing'):
        try:
            title = job.find('h2', class_='title').text
            company = job.find('span', class_='company').text
            location = job.find('span', class_='location').text
            job_url = job.find('a', class_='job-link')['href']
            salary = "N/A"  # Modify to scrape salary info
            jobs.append({
                'title': title, 'company': company, 'location': location, 
                'url': f"https://wellfound.com{job_url}", 'salary': salary
            })
        except AttributeError:
            continue
    return jobs

# Reuse the same pattern for Indeed, LinkedIn, etc.
def search_indeed(search_term, location, job_type):
    # Dynamic URL based on search term, job type, location
    url = f"https://www.indeed.com/jobs?q={search_term}&l={location}&jt={job_type}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch Indeed jobs. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []
    for job in soup.find_all('div', class_='job_seen_beacon'):
        try:
            title = job.find('h2', class_='jobTitle').text
            company = job.find('span', class_='companyName').text
            location = job.find('div', class_='companyLocation').text
            job_url = job.find('a')['href']
            salary = "N/A"  # Modify to scrape salary info
            jobs.append({
                'title': title, 'company': company, 'location': location, 
                'url': f"https://www.indeed.com{job_url}", 'salary': salary
            })
        except AttributeError:
            continue
    return jobs

def search_ziprecruiter(search_term):
    url = f"https://www.ziprecruiter.com/jobs-search?search={search_term}&location=Remote+%28USA%29"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    job_listings = soup.find_all('article', class_='job_result')
    for job in job_listings:
        title = job.find('h2', class_='job_title').text.strip()
        company = job.find('a', class_='t_org_link').text.strip()
        location = job.find('p', class_='location').text.strip()
        job_url = job.find('a')['href']
        salary = job.find('span', class_='salary').text.strip() if job.find('span', class_='salary') else "N/A"

        job_data = {
            'title': title,
            'company': company,
            'location': location,
            'url': f"https://www.ziprecruiter.com{job_url}",
            'salary': salary
        }
        jobs.append(job_data)

    return jobs

def search_linkedin(search_term):
    url = f"https://www.linkedin.com/jobs/search?keywords={search_term}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    job_listings = soup.find_all('li', class_='result-card job-result-card')
    for job in job_listings:
        title = job.find('h3', class_='result-card__title').text.strip()
        company = job.find('h4', class_='result-card__subtitle').text.strip()
        location = job.find('span', class_='job-result-card__location').text.strip()
        job_url = job.find('a', class_='result-card__full-card-link')['href']
        salary = "N/A"  # LinkedIn job listings generally do not show salaries

        job_data = {
            'title': title,
            'company': company,
            'location': location,
            'url': job_url,
            'salary': salary
        }
        jobs.append(job_data)

    return jobs

def search_usajobs(search_term):
    url = f"https://www.usajobs.gov/search/results/?k={search_term}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    job_listings = soup.find_all('div', class_='usajobs-search-result--item')
    for job in job_listings:
        title = job.find('h2', class_='usajobs-search-result--item__title').text.strip()
        company = "USA Jobs"
        location = job.find('div', class_='usajobs-search-result--location').text.strip()
        job_url = f"https://www.usajobs.gov{job.find('a')['href']}"
        salary = job.find('span', class_='usajobs-search-result--salary').text.strip() if job.find('span', class_='usajobs-search-result--salary') else "N/A"

        job_data = {
            'title': title,
            'company': company,
            'location': location,
            'url': job_url,
            'salary': salary
        }
        jobs.append(job_data)

    return jobs


def get_fortune_500():
    url = "https://fortune.com/fortune500/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    companies = []
    # Adjust the selector according to the Fortune 500 page structure
    company_listings = soup.find_all('div', class_='company-listing')
    for company in company_listings:
        company_name = company.find('a').text
        companies.append(company_name)

    return companies

def search_company_careers(company_name):
    # Example logic: Web scrape the company's careers page
    company_url = f"https://www.{company_name}.com/careers"  # Adjust based on actual career page structures
    response = requests.get(company_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    job_listings = soup.find_all('div', class_='job-listing')
    for job in job_listings:
        title = job.find('h2', class_='job-title').text
        location = job.find('div', class_='job-location').text
        job_url = job.find('a')['href']
        salary = "N/A"  # Most company career pages don’t list salary
        job_type = "Onsite"  # Default to "Onsite", adjust based on actual job type
        
        job_data = {
            'title': title,
            'company': company_name,
            'location': location,
            'url': job_url,
            'salary': salary,
            'type': job_type
        }
        jobs.append(job_data)

    return jobs

# Keep a set of visited URLs to avoid duplicates across searches
visited_urls = set()

def limit_jobs(jobs, limit=5):
    """Limit the number of job results returned."""
    return jobs[:limit]

def filter_duplicate_jobs(jobs):
    """Filter out jobs that have already been seen in previous searches."""
    global visited_urls
    filtered_jobs = []
    
    for job in jobs:
        job_url_hash = hashlib.md5(job['url'].encode()).hexdigest()
        if job_url_hash not in visited_urls:
            filtered_jobs.append(job)
            visited_urls.add(job_url_hash)
    
    return filtered_jobs

# Master search function combining all job boards
def search_jobs(search_term, location=None, job_type=None, salary_min=None, salary_max=None, limit=5):
    all_jobs = []
    all_jobs.extend(search_wellfound(search_term))
    all_jobs.extend(search_indeed(search_term))
    all_jobs.extend(search_ziprecruiter(search_term))
    all_jobs.extend(search_linkedin(search_term))
    all_jobs.extend(search_usajobs(search_term))

    # Optionally filter jobs by salary or other criteria if provided
    filtered_jobs = []
    for job in all_jobs:
        if salary_min and job['salary'] != 'N/A' and int(job['salary']) < int(salary_min):
            continue
        if salary_max and job['salary'] != 'N/A' and int(job['salary']) > int(salary_max):
            continue
        filtered_jobs.append(job)

    # Limit the number of results returned
    return limit_jobs(filtered_jobs, limit)



def search_jobs_route():
    search_term = request.json.get('search_term')
    location = request.json.get('location')
    job_type = request.json.get('job_type')
    companies = request.json.get('companies', None)
    
    all_jobs = []

    if companies:
        for company in companies:
            all_jobs.extend(search_company_careers(company))
    else:
        fortune_500 = get_fortune_500()
        for company in fortune_500:
            all_jobs.extend(search_company_careers(company))

    return jsonify(all_jobs)

def create_profiles_db():
    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS profiles
                     (id INTEGER PRIMARY KEY,
                      search_term TEXT, 
                      location TEXT, 
                      job_type TEXT)''')
    conn.commit()
    conn.close()

def save_profile(search_term, location, job_type):
    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO profiles (search_term, location, job_type) 
                      VALUES (?, ?, ?)''', (search_term, location, job_type))
    conn.commit()
    conn.close()

def get_profiles():
    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM profiles')
    profiles = cursor.fetchall()
    conn.close()
    return profiles


def apply_to_job(job_url, resume_path):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)

    # Example: Navigate to job page and "apply" (simulate filling a form)
    driver.get(job_url)
    
    # Simulate filling in an application form (adjust selectors)
    driver.find_element(By.NAME, 'resume').send_keys(resume_path)
    driver.find_element(By.NAME, 'submit').click()

    driver.quit()
    return "Application submitted!"

def get_profiles():
    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM profiles')
    profiles = cursor.fetchall()
    conn.close()
    return profiles

def create_db():
    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications
                      (id INTEGER PRIMARY KEY, job_url TEXT, company_name TEXT, role TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def save_application(job_url, company_name, role, location, salary, job_type):
    unique_key = hashlib.md5(f"{role}{company_name}{location}".encode()).hexdigest()

    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO applications (job_url, company_name, role, location, salary, job_type, unique_key)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (job_url, company_name, role, location, salary, job_type, unique_key))
    conn.commit()
    conn.close()



def get_applications():
    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM applications')
    applications = cursor.fetchall()
    conn.close()
    return applications


search_wellfound("data-engineer")