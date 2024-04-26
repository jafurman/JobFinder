import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pymongo


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        # Establish connection to source and destination collections
        db_source = client.JobListings
        db_destination = client.NewJobListings
        return db_source, db_destination
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


def open_unique_job_links():
    try:
        db_source, db_destination = connectDataBase()
        if db_source is not None and db_destination is not None:
            found_jobs_collection = db_source.foundJobs
            for job in found_jobs_collection.find():
                job_link = job.get('job_link')
                job_name = job.get('job_name')
                if job_link:
                    driver = webdriver.Chrome()
                    driver.get(job_link)
                    try:
                        showMoreButton = driver.find_element(By.XPATH, '//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/section/div[2]/div[2]/button')
                        showMoreButton.click()
                        time.sleep(20)
                        sectionElement = driver.find_element(By.XPATH, '//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/section')
                        fullJobDescription = sectionElement.text.strip()
                        print(fullJobDescription)
                        # Add the new text description to the existing job entry
                        job['full_description'] = fullJobDescription
                        # Insert the modified job entry into the new collection
                        db_destination.foundJobs.insert_one(job)
                    except:
                        print("Empty listing")
                        time.sleep(20)
                    driver.quit()  # Close the browser after processing the link
                else:
                    print("Job link not found for job ID:", job['_id'])
    except Exception as error:
        traceback.print_exc()
        print("Error while opening unique job links..")


open_unique_job_links()