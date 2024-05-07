# Optimize imports
import traceback
import pymongo
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define constants
RESUME_FILE_PATH = "resume.txt"
KEYWORDS_INCREASE = ["python", "machine learning", "API", "pandas", "sklearn", "unity", "HTML", "Adobe", "Photoshop",
                     "Python", "MongoDB", "ML", "ai", "noSQL", "California", "Washington"]
KEYWORDS_DECREASE = ["sales", "enrolled", "C++", "c++", "masters", "Masters", "node", "pursing", "MS", "PhD", "M.S"]
SKILL_WEIGHT = 2



# Function to connect to the database
def connect_to_database():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        return client.JobListings
    except Exception as e:
        traceback.print_exc()
        print("Failed to connect to the database.")
        return None


# Function to preprocess text
def preprocess_text(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)


# Function to read resume file
def read_resume(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading the resume file: {e}")
        return None


# Function to iterate over job descriptions
def iterate_job_descriptions(db):
    try:
        job_details_collection = db.jobDetails
        for job in job_details_collection.find():
            full_description = job.get('full_description')
            if full_description:
                yield {
                    'job_name': job.get('job'),
                    'company': job.get('company'),
                    'location': job.get('location'),
                    'salary': job.get('salary'),
                    'description': preprocess_text(full_description),
                    'job_link': job.get('job_link'),
                    'skills': job.get('skills', [])  # Add skills list here
                }
            else:
                print("No full description available for job ID:", job.get('_id'))
    except Exception as e:
        traceback.print_exc()
        print("Error while iterating job descriptions.")


# Function to compare resume to job descriptions
def compare_resume_to_job_descriptions(resume_tokens, job_descriptions):
    try:
        tfidf_vectorizer = TfidfVectorizer()

        job_skills_tokens = [" ".join(job['skills']) for job in job_descriptions]
        job_skills_tfidf = tfidf_vectorizer.fit_transform(job_skills_tokens)

        job_descriptions_tokens = [job['description'] for job in job_descriptions]
        job_descriptions_tfidf = tfidf_vectorizer.transform(job_descriptions_tokens)

        resume_tfidf = tfidf_vectorizer.transform([resume_tokens])

        similarity_scores = cosine_similarity(resume_tfidf, job_descriptions_tfidf)
        sorted_indices = similarity_scores.argsort()[0][::-1]
        scores = similarity_scores[0, sorted_indices]
        sorted_job_descriptions = [job_descriptions[i] for i in sorted_indices]

        skills_similarity_scores = cosine_similarity(resume_tfidf, job_skills_tfidf)

        for job, skill_similarity in zip(sorted_job_descriptions, skills_similarity_scores[0]):
            description_tokens = job['description'].split()
            keyword_score_increase = sum(1 for keyword in KEYWORDS_INCREASE if keyword in description_tokens)
            keyword_score_decrease = sum(1 for keyword in KEYWORDS_DECREASE if keyword in description_tokens)

            scaled_skill_similarity = skill_similarity * SKILL_WEIGHT
            job['similarity_score'] = scores[sorted_job_descriptions.index(
                job)] + scaled_skill_similarity + keyword_score_increase - keyword_score_decrease

        return sorted_job_descriptions
    except Exception as e:
        traceback.print_exc()
        print("Error while comparing resume to job descriptions.")


if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        resume = read_resume(RESUME_FILE_PATH)
        if resume:
            resume_tokens = preprocess_text(resume)
            job_descriptions = list(iterate_job_descriptions(db))
            sorted_job_descriptions = compare_resume_to_job_descriptions(resume_tokens, job_descriptions)
            sorted_job_descriptions = sorted(sorted_job_descriptions, key=lambda x: x['similarity_score'], reverse=False)
            written_jobs = set()
            with open('jobs.txt', 'w') as f:
                for job in sorted_job_descriptions:
                    if job['job_name'] not in written_jobs:
                        f.write(f"Job Name: {job['job_name']}\n")
                        f.write(f"  Similarity Score: {job['similarity_score']}\n")
                        f.write(f"  Salary: {job['salary']}\n")
                        f.write(f"  Location: {job['location']}\n")
                        f.write(f"  Company: {job['company']}\n")
                        f.write(f"  Job Link: {job['job_link']}\n")
                        f.write("Important Skills:\n")
                        for skill in job['skills']:
                            f.write(f"    - {skill}\n")
                        f.write("\n")
                        written_jobs.add(job['job_name'])
            counter = 0
            for job in sorted_job_descriptions:
                if job['job_name'] not in written_jobs:
                    counter += 1
                    print(f"Job Entry Placement: {counter}")
                    print(f"  Job Name: {job['job_name']}")
                    print(f"  Similarity Score: {job['similarity_score']}")
                    print(f"  Salary: {job['salary']}")
                    print(f"  Location: {job['location']}")
                    print(f"  Company: {job['company']}")
                    print(f"  Job Link: {job['job_link']}")
                    print("Important Skills:")
                    for skill in job['skills']:
                        print(f"    - {skill}")
                    print()
