import traceback
import spacy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
import time


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
            found_jobs_collection = db_source.foundJobsSecondSet
            for job in found_jobs_collection.find():
                job_link = job.get('job_link')
                if job_link:
                    driver = webdriver.Chrome()
                    driver.get(job_link)
                    try:
                        show_more_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/section/div[2]/div[2]/button'))
                        )
                        show_more_button.click()

                        time.sleep(4)

                        section_element = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.XPATH, '//*[@id="app-navigation"]/div[2]/div/div[1]/div/div[1]/div/section'))
                        )
                        full_job_description = section_element.text.strip()
                        job['full_description'] = full_job_description
                        db_source.jobDetails.insert_one(job)
                    except Exception as e:
                        print("Error processing job:", str(e))
                    finally:
                        driver.quit()  # Close the browser after processing the link
                else:
                    print("Job link not found for job ID:", job['_id'])
                    time.sleep(3)
    except Exception as error:
        traceback.print_exc()
        print("Error while opening unique job links..")


nlp = spacy.load("en_core_web_sm")
open_unique_job_links()