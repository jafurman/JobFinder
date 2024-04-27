import traceback
import pymongo
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        db = client.JobListings
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


def preprocessText(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)


def resumeToString(fp):
    try:
        with open(fp, 'r') as file:
            resume_content = file.read()
        return resume_content
    except Exception as e:
        print(f"Error reading the resume file: {e}")
        return None


def iterate_job_descriptions():
    try:
        db = connectDataBase()
        if db is not None:
            job_details_collection = db.jobDetails
            for job in job_details_collection.find():
                full_description = job.get('full_description')
                if full_description:
                    yield {
                        'job_name': job.get('job'),
                        'company': job.get('company'),
                        'location': job.get('location'),
                        'salary': job.get('salary'),
                        'description': preprocessText(full_description),
                        'job_link': job.get('job_link')
                    }
                else:
                    print("No full description available for job ID:", job['_id'])
    except Exception as error:
        traceback.print_exc()
        print("Error while printing job descriptions..")


def compare_resume_to_job_descriptions(resume_tokens, job_descriptions, keywords_increase, keywords_decrease):
    try:
        tfidf_vectorizer = TfidfVectorizer()

        job_descriptions_tokens = [job['description'] for job in job_descriptions]
        job_descriptions_tfidf = tfidf_vectorizer.fit_transform(job_descriptions_tokens)
        resume_tfidf = tfidf_vectorizer.transform([resume_tokens])

        similarity_scores = cosine_similarity(resume_tfidf, job_descriptions_tfidf)
        sorted_indices = similarity_scores.argsort()[0][::-1]
        scores = similarity_scores[0, sorted_indices]
        sorted_job_descriptions = [job_descriptions[i] for i in sorted_indices]

        # Keyword matching
        for job in sorted_job_descriptions:
            description_tokens = job['description'].split()
            keyword_score_increase = sum(1 for keyword in keywords_increase if keyword in description_tokens)
            keyword_score_decrease = sum(1 for keyword in keywords_decrease if keyword in description_tokens)
            job['similarity_score'] = scores[sorted_job_descriptions.index(job)] + keyword_score_increase - keyword_score_decrease

        return sorted_job_descriptions
    except Exception as e:
        traceback.print_exc()
        print("Error while comparing resume to job descriptions.")

resume_fp = "resume.txt"
resume = resumeToString(resume_fp)
if resume:
    resume_tokens = preprocessText(resume)
    job_descriptions = list(iterate_job_descriptions())

    # Define keywords to increase and decrease similarity score
    keywords_increase = ["python", "machine learning", "API", "pandas", "sklearn", "unity", "HTML", "Adobe", "Photoshop", "Python", "analysis", "Mongo", "MongoDB", "ML", "machine", "leanring", "ai"]
    keywords_decrease = ["sales", "customer service", "currently", "enrolled", "C++", "c++", "masters", "Masters", "university", ""]

    sorted_job_descriptions = compare_resume_to_job_descriptions(
        resume_tokens, job_descriptions, keywords_increase, keywords_decrease)

    sorted_job_descriptions = sorted(sorted_job_descriptions, key=lambda x: x['similarity_score'], reverse=True)

    for job in sorted_job_descriptions:
        print("Job Details:")
        print(f"  Job Name: {job['job_name']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Salary: {job['salary']}")
        print(f"  Similarity Score: {job['similarity_score']}")
        print(f"  Job Link: {job['job_link']}")
        print()