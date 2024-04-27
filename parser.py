import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pymongo


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        # Establish connection to source collection
        db_source = client.JobListings
        # Return only the source database, as we're not creating a new database
        return db_source
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully..")


def open_unique_job_links():
    try:
        db_source = connectDataBase()
        if db_source is not None:
            found_jobs_collection = db_source.foundJobs
            for job in found_jobs_collection.find():
                job_link = job.get('job_link')
                if job_link:
                    driver = webdriver.Chrome()
                    driver.get(job_link)
                    try:
                        showMoreButton = driver.find_element(By.XPATH, '//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/section/div[2]/div[2]/button')
                        showMoreButton.click()
                        time.sleep(2.5)
                        sectionElement = driver.find_element(By.XPATH, '//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/section')
                        fullJobDescription = sectionElement.text.strip()
                        print(fullJobDescription)
                        job['full_description'] = fullJobDescription
                        db_source.jobDetails.insert_one(job)
                    except:
                        print("Empty listing")
                        time.sleep(1.5)
                    driver.quit()  # Close the browser after processing the link
                else:
                    print("Job link not found for job ID:", job['_id'])
    except Exception as error:
        traceback.print_exc()
        print("Error while opening unique job links..")


open_unique_job_links()