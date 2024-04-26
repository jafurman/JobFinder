import traceback
import pymongo
import spacy


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        # database connection is localhost client.[databaseName]
        db = client.JobListings
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


def tokenizeText(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return tokens



def iterate_job_descriptions():
    try:
        db = connectDataBase()
        if db is not None:
            job_details_collection = db.jobDetails
            for job in job_details_collection.find():
                full_description = job.get('full_description')
                if full_description:
                    tokenizedText = tokenizeText(full_description)
                    print(tokenizedText)
                else:
                    print("No full description available for job ID:", job['_id'])
    except Exception as error:
        traceback.print_exc()
        print("Error while printing job descriptions..")

iterate_job_descriptions()