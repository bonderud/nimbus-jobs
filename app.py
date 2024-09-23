from flask import Flask, render_template, request, jsonify
from job_search import search_jobs, save_application

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# Job search route
@app.route('/search_jobs', methods=['POST'])
def search_jobs_route():
    search_term = request.json.get('search_term')
    location = request.json.get('location', '')  # Handle default empty location
    job_type = request.json.get('job_type', 'Any')
    salary_min = request.json.get('salary_min', None)
    salary_max = request.json.get('salary_max', None)
    limit = request.json.get('limit', 5)  # Default limit to 5 jobs

    jobs = search_jobs(search_term, location, job_type, salary_min, salary_max, limit)
    return jsonify(jobs)

# Route for saving applications
@app.route('/save_application', methods=['POST'])
def save_application_route():
    data = request.json
    save_application(
        data['job_url'], 
        data['company_name'], 
        data['role'], 
        data['location'], 
        data['salary'], 
        data['job_type']
    )
    return jsonify({"message": "Application saved!"})

if __name__ == '__main__':
    app.run(debug=True)
