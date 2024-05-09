import pymongo
import spacy

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["JobListings"]
collection = db["JobDetails"]

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Query the JobDetails collection and process full_description field
for job_listing in collection.find({}, {"full_description": 1}):
    full_description = job_listing.get("full_description", "")
    
    # Process the full_description using spaCy
    doc = nlp(full_description.lower())

    # Extract important information
    qualifications = [entity.text for entity in doc.ents if entity.label_ == "QUALIFICATION"]
    required_skills = [entity.text for entity in doc.ents if entity.label_ == "REQUIRED_SKILL"]
    skills = [entity.text for entity in doc.ents if entity.label_ == "SKILL"]
    experience = [entity.text for entity in doc.ents if entity.label_ == "EXPERIENCE"]
    abilities = [entity.text for entity in doc.ents if entity.label_ == "ABILITY"]

    # Present the extracted information for each job listing
    print("Job Title:", job_listing.get("job"))
    print("Qualifications:", qualifications)
    print("Required Skills:", required_skills)
    print("Skills:", skills)
    print("Experience:", experience)
    print("Abilities:", abilities)
    print("\n")