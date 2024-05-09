from pymongo import MongoClient
import traceback
import spacy
import re
from pprint import pprint

def connectDatabase():
    try:
        # Connect to the MongoDB server
        client = MongoClient('mongodb://localhost:27017/')

        # Select the database
        db = client['JobListings']  # Replace 'JobListings' with your actual database name
        return db

    except Exception as error:
        traceback.print_exc()
        print("Failed to connect to the database.")
        return None

def preprocess_text(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return "\n".join(sentences)

def extract_information(job_desc):
    qualifications_keywords = ["qualification", "degree", "certification"]
    requirements_keywords = ["requirement", "experience", "require", "must"]
    skills_keywords = ["skill", "knowledge", "expertise"]
    experience_keywords = ["years of experience", "entry level", "skilled", "experience", "pursing", "work experience"]

    preprocessed_desc = preprocess_text(job_desc)

    qualifications = []
    requirements = []
    skills = []
    experience_level = []

    sentences = preprocessed_desc.split("\n")
    for sentence in sentences:
        for keyword in qualifications_keywords:
            if keyword in sentence:
                qualifications.append(sentence.strip())
                break
        for keyword in requirements_keywords:
            if keyword in sentence:
                requirements.append(sentence.strip())
                break
        for keyword in skills_keywords:
            if keyword in sentence:
                skills.append(sentence.strip())
                break
        for keyword in experience_keywords:
            if keyword in sentence:
                experience_level.append(sentence.strip())
                break

    # Remove duplicate entries
    qualifications = list(set(qualifications))
    requirements = list(set(requirements))
    skills = list(set(skills))
    experience_level = list(set(experience_level))

    # Combine all relevant information into a single paragraph
    relevant_information = []
    if qualifications:
        relevant_information.append("".join(qualifications))
    if requirements:
        relevant_information.append("".join(requirements))
    if skills:
        relevant_information.append("".join(skills))
    if experience_level:
        relevant_information.append("".join(experience_level))

    # Insert newline after every 100 characters
    relevant_info_text = "\n".join(relevant_information)
    relevant_info_with_newlines = "\n".join([relevant_info_text[i:i+100] for i in range(0, len(relevant_info_text), 100)])

    return relevant_info_with_newlines

def print_jobs():
    try:
        db = connectDatabase()
        job_details_collection = db.jobDetails
        complete_listings_collection = db.completeListings

        jobs = job_details_collection.find().limit(2000)

        for job in jobs:
            job_desc = job['full_description']
            url = job['job_link']
            title = job['job']
            location = job['location']
            company = job['company']
            salary = job['salary']
            skills = job['skills']
            full_desc = job['full_description']
            timeAgo = job['time_ago_posted']

            information = extract_information(job_desc)

            print(f"URL: {url}")
            print(f"Job Title: {title}")
            print(f"Location: {location}")
            print(f"Salary: {salary}")
            print(f"Company: {company}")
            print(f"Skills: {skills}")
            print(f"Full Des: {full_desc}")
            print(f"Relev Info:")
            pprint(information, indent=4)

            print()

            new_entry = {
                'job': title,
                'job_url': url,
                'location': location,
                'company': company,
                'salary': salary,
                'description': job_desc,
                'skills': skills,
                'full_description': full_desc,
                'new_information': information,
                'time_ago_posted': timeAgo
            }
            complete_listings_collection.insert_one(new_entry)
            print("New entry added successfully.")

    except Exception as error:
        traceback.print_exc()
        print("Failed to retrieve jobs from the database.")

print_jobs()

