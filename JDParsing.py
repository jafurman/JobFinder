from pymongo import MongoClient
import traceback
import spacy
import matplotlib.pyplot as plt

badWords = ['experience', 'require', 'previous']
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

def preprocessText(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return tokens


def printJobs():
    try:
        db = connectDatabase()
        job_details_collection = db.jobDetails
        jobs = job_details_collection.find().limit(50)

        for job in jobs:
            jobDesc = job['full_description']
            tokens = preprocessText(jobDesc)
            print(tokens)
            print()

    except Exception as error:
        traceback.print_exc()
        print("Failed to retrieve jobs from the database.")

printJobs()