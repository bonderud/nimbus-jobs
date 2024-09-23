import openai
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Initialize SpaCy NLP model and Sentence Transformer for vector embeddings
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Initialize OpenAI API as a fallback
openai.api_key = 'your-openai-api-key'

# Refined function to scrape job postings from company career pages
def scrape_jobs_from_company_site(company_url):
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    jobs = []
    try:
        driver.get(company_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'job')]")))
        
        # Refine the job element targeting logic
        job_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'job')]")

        for job_element in job_elements:
            job_title = job_element.text
            job_link = job_element.get_attribute('href')
            
            # Filter out unwanted links (e.g., legal notices or pagination links)
            if job_title and "results" not in job_link and "search" not in job_link and "saved" not in job_link:
                jobs.append({
                    "description": job_title,
                    "job_link": job_link
                })
    except WebDriverException as e:
        print(f"Error accessing {company_url}: {e}")
    finally:
        driver.quit()

    return jobs

# Function to parse resume for key details (skills, titles)
def parse_resume(resume_text):
    doc = nlp(resume_text)
    skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
    titles = [ent.text for ent in doc.ents if ent.label_ == "JOB_TITLE"]
    return {"skills": skills, "titles": titles}

# Parse job descriptions for key details (skills, titles)
def parse_job_description(job_desc):
    doc = nlp(job_desc)
    required_skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
    job_title = [ent.text for ent in doc.ents if ent.label_ == "JOB_TITLE"]
    return {"skills": required_skills, "title": job_title}

# Calculate cosine similarity between resume and job description
def calculate_similarity(resume_data, job_data):
    resume_vector = embedder.encode(" ".join(resume_data["skills"] + resume_data["titles"]))
    job_vector = embedder.encode(" ".join(job_data["skills"] + job_data["title"]))
    
    similarity_score = cosine_similarity([resume_vector], [job_vector])
    
    return round(similarity_score[0][0] * 100, 2)

# Main search function based on resume
def search_jobs_based_on_resume(resume_text, limit=5):
    resume_data = parse_resume(resume_text)
    all_jobs = []

    fortune_500_careers_urls = [
        "https://careers.google.com/",
        "https://jobs.apple.com/en-us/search",
        "https://www.microsoft.com/en-us/careers",
        "https://careers.amazon.com/",
        "https://www.jpmorganchase.com/about/careers",
    ]

    # Scrape Fortune 500 companies' career pages
    for company_url in fortune_500_careers_urls:
        try:
            jobs = scrape_jobs_from_company_site(company_url)
            
            for job in jobs[:limit]:
                job_data = parse_job_description(job['description'])
                strength_rating = calculate_similarity(resume_data, job_data)
                job['strength_rating'] = strength_rating
                all_jobs.append(job)
        except Exception as e:
            print(f"Failed to scrape {company_url}: {e}")
            continue  # Move to the next company
    
    return all_jobs

# Function to print formatted jobs
def print_formatted_jobs(jobs):
    for i, job in enumerate(jobs):
        print(f"\nJob {i + 1}:")
        print(f"Description: {job.get('description', 'N/A')}")
        print(f"Job Link: {job.get('job_link', 'N/A')}")
        print(f"Strength Rating: {job.get('strength_rating', 'N/A')}")
        print("-" * 40)

# Example resume text
resume_text = """
Michael F Bonderud, Data Analyst at C.H. Robinson, experienced with Python, T-SQL, AI/ML, dashboard creation, 
cloud technologies, and data analytics. Proficient in tools like Power BI, SSRS, and Git. 
Led machine learning projects and built tools using advanced analytics.
"""

# Run the job search based on resume
if __name__ == "__main__":
    jobs = search_jobs_based_on_resume(resume_text, limit=5)
    print_formatted_jobs(jobs)
