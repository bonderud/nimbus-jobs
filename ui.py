import streamlit as st
import requests

st.title('Job Search Manager')
st.write('Enter your job search criteria:')

# Inputs for search criteria
search_term = st.text_input('Search Term (e.g., Data Scientist, Software Engineer)')
location = st.text_input('Location (e.g., City, State, Country)')
job_type = st.selectbox('Job Type', ('Onsite', 'Remote', 'Hybrid', 'Any'))
salary_min = st.text_input('Minimum Salary (optional)')
salary_max = st.text_input('Maximum Salary (optional)')
limit = st.slider('Number of Jobs to Return', 1, 20, 5)

# Iterate through the job listings and display the information
if st.button('Search Jobs'):
    try:
        response = requests.post("http://127.0.0.1:5000/search_jobs", json={
            'search_term': search_term,
            'location': location,
            'job_type': job_type,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'limit': limit
        })
        if response.status_code == 200:
            job_listings = response.json()
            st.write(f"Found {len(job_listings)} jobs:")
            for job in job_listings:
                title = job.get('title', 'N/A')
                company = job.get('company', 'N/A')
                location = job.get('location', 'N/A')
                salary = job.get('salary', 'N/A')
                job_link = job.get('job_link', 'N/A')
                
                st.write(f"{title} at {company} in {location}, Salary: {salary}")
                if job_link != "N/A":
                    st.write(f"[Job Link]({job_link})")
        else:
            st.error('Failed to retrieve job listings.')
    except requests.ConnectionError:
        st.error("Could not connect to the job search service.")



# Save profile with incomplete criteria
if st.button('Save Search Profile', key='save_profile'):
    if search_term or location or job_type:
        save_profile(search_term, location, job_type)
        st.success("Profile saved successfully!")
    else:
        st.error("Please enter at least one search criteria.")
