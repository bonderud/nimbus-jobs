from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sqlite3
import hashlib
import time

# To avoid scraping duplicate jobs
visited_urls = set()

# Initialize Selenium WebDriver with headless option
def initialize_chromedriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver

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

def limit_jobs(jobs, limit=5):
    """Limit the number of job results returned."""
    return jobs[:limit]

# Wellfound search function using Selenium
def search_wellfound(search_term, location, job_type):
    driver = initialize_chromedriver()
    url = f"https://wellfound.com/role/l/{search_term}/united-states"
    driver.get(url)
    time.sleep(2)  # Give the page time to load

    jobs = []
    try:
        listings = driver.find_elements(By.CLASS_NAME, 'job-listing')
        for listing in listings:
            try:
                title = listing.find_element(By.CLASS_NAME, 'title').text
                company = listing.find_element(By.CLASS_NAME, 'company').text
                location = listing.find_element(By.CLASS_NAME, 'location').text
                job_url = listing.find_element(By.TAG_NAME, 'a').get_attribute('href')
                salary = "N/A"  # Adjust salary scraping logic if present

                jobs.append({
                    'title': title, 
                    'company': company, 
                    'location': location, 
                    'url': job_url, 
                    'salary': salary
                })
            except Exception as e:
                print(f"Error parsing job listing on Wellfound: {e}")
    finally:
        driver.quit()

    return jobs

def search_indeed(search_term, location=None, job_type=None):
    driver = initialize_chromedriver()
    url = f"https://www.indeed.com/jobs?q={search_term}&l={location}&jt={job_type}"
    driver.get(url)

    jobs = []
    try:
        # Wait for job listings to load dynamically
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'job_seen_beacon')))
        
        listings = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')
        for index, listing in enumerate(listings):
            try:
                # Extract job title
                title = listing.find_element(By.CSS_SELECTOR, 'h2.jobTitle').text
                print(f"Job {index + 1}: Title found - {title}")

                # Extract company name (use multiple strategies to handle missing company name cases)
                try:
                    company = listing.find_element(By.CSS_SELECTOR, 'span.companyName').text
                    print(f"Job {index + 1}: Company found - {company}")
                except NoSuchElementException:
                    try:
                        company = listing.find_element(By.CSS_SELECTOR, 'span.company').text
                        print(f"Job {index + 1}: Company found (fallback) - {company}")
                    except NoSuchElementException:
                        company = "N/A"
                        print(f"Job {index + 1}: Company not found")

                # Extract location (use fallback if the location is missing)
                try:
                    location = listing.find_element(By.CSS_SELECTOR, 'div.companyLocation').text
                    print(f"Job {index + 1}: Location found - {location}")
                except NoSuchElementException:
                    location = "N/A"
                    print(f"Job {index + 1}: Location not found")

                # Extract job URL
                job_url = listing.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                print(f"Job {index + 1}: URL found - {job_url}")

                # Extract salary, if available (handle missing salary gracefully)
                try:
                    salary = listing.find_element(By.CSS_SELECTOR, 'span.salary-snippet').text
                    print(f"Job {index + 1}: Salary found - {salary}")
                except NoSuchElementException:
                    salary = "N/A"
                    print(f"Job {index + 1}: Salary not found")

                # Extract job type (e.g., full-time, part-time), if available
                try:
                    job_type = listing.find_element(By.CSS_SELECTOR, 'span.jobsearch-JobMetadataHeader-item').text
                    print(f"Job {index + 1}: Job type found - {job_type}")
                except NoSuchElementException:
                    job_type = "N/A"
                    print(f"Job {index + 1}: Job type not found")

                # Collect job data
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'url': job_url,
                    'salary': salary,
                    'job_type': job_type
                })
            except Exception as e:
                print(f"Error parsing job listing {index + 1}: {e}")
    except Exception as e:
        print(f"Error retrieving Indeed jobs: {e}")
    finally:
        driver.quit()

    return jobs

# Test the updated Indeed scraping function
if __name__ == "__main__":
    jobs = search_indeed("aerospace engineer", "Remote", "fulltime")
    print(jobs)



# ZipRecruiter search function using Selenium
def search_ziprecruiter(search_term):
    driver = initialize_chromedriver()
    url = f"https://www.ziprecruiter.com/jobs-search?search={search_term}&location=Remote+%28USA%29"
    driver.get(url)
    time.sleep(2)

    jobs = []
    try:
        listings = driver.find_elements(By.CLASS_NAME, 'job_result')
        for listing in listings:
            try:
                title = listing.find_element(By.CLASS_NAME, 'job_title').text.strip()
                company = listing.find_element(By.CLASS_NAME, 't_org_link').text.strip()
                location = listing.find_element(By.CLASS_NAME, 'location').text.strip()
                job_url = listing.find_element(By.TAG_NAME, 'a').get_attribute('href')
                salary = "N/A"

                jobs.append({
                    'title': title, 
                    'company': company, 
                    'location': location, 
                    'url': job_url, 
                    'salary': salary
                })
            except Exception as e:
                print(f"Error parsing job listing on ZipRecruiter: {e}")
    finally:
        driver.quit()

    return jobs

# LinkedIn search function using Selenium
def search_linkedin(search_term):
    driver = initialize_chromedriver()
    url = f"https://www.linkedin.com/jobs/search?keywords={search_term}"
    driver.get(url)
    time.sleep(2)

    jobs = []
    try:
        listings = driver.find_elements(By.CLASS_NAME, 'result-card')
        for listing in listings:
            try:
                title = listing.find_element(By.CLASS_NAME, 'result-card__title').text.strip()
                company = listing.find_element(By.CLASS_NAME, 'result-card__subtitle').text.strip()
                location = listing.find_element(By.CLASS_NAME, 'job-result-card__location').text.strip()
                job_url = listing.find_element(By.TAG_NAME, 'a').get_attribute('href')
                salary = "N/A"

                jobs.append({
                    'title': title, 
                    'company': company, 
                    'location': location, 
                    'url': job_url, 
                    'salary': salary
                })
            except Exception as e:
                print(f"Error parsing job listing on LinkedIn: {e}")
    finally:
        driver.quit()

    return jobs

# USAJobs search function using Selenium
def search_usajobs(search_term):
    driver = initialize_chromedriver()
    url = f"https://www.usajobs.gov/search/results/?k={search_term}"
    driver.get(url)
    time.sleep(2)

    jobs = []
    try:
        listings = driver.find_elements(By.CLASS_NAME, 'usajobs-search-result--item')
        for listing in listings:
            try:
                title = listing.find_element(By.CLASS_NAME, 'usajobs-search-result--item__title').text.strip()
                company = "USA Jobs"
                location = listing.find_element(By.CLASS_NAME, 'usajobs-search-result--location').text.strip()
                job_url = listing.find_element(By.TAG_NAME, 'a').get_attribute('href')
                salary = "N/A"

                jobs.append({
                    'title': title, 
                    'company': company, 
                    'location': location, 
                    'url': job_url, 
                    'salary': salary
                })
            except Exception as e:
                print(f"Error parsing job listing on USAJobs: {e}")
    finally:
        driver.quit()

    return jobs

# Master search function combining all job boards
def search_jobs(search_term, location=None, job_type=None, salary_min=None, salary_max=None, limit=5):
    all_jobs = []
    all_jobs.extend(search_wellfound(search_term, location, job_type))
    all_jobs.extend(search_indeed(search_term, location, job_type))
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

    # Remove duplicates and limit the results
    filtered_jobs = filter_duplicate_jobs(filtered_jobs)
    return limit_jobs(filtered_jobs, limit)

# Save job application
def save_application(job_url, company_name, role, location, salary, job_type):
    unique_key = hashlib.md5(f"{role}{company_name}{location}".encode()).hexdigest()

    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO applications (job_url, company_name, role, location, salary, job_type, unique_key)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (job_url, company_name, role, location, salary, job_type, unique_key))
    conn.commit()
    conn.close()

# Create database for applications
def create_db():
    conn = sqlite3.connect('applications.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications
                      (id INTEGER PRIMARY KEY, job_url TEXT, company_name TEXT, role TEXT, location TEXT, salary TEXT, job_type TEXT, status TEXT)''')
    conn.commit()
    conn.close()
