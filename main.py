import traceback

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time
import pymongo


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        # database connection is localhost client.[databaseName]
        db = client.JobListings
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


def storeJobsInDB(jobs_list):
    try:
        db = connectDataBase()
        collection = db.foundJobs
        for job_content in jobs_list:
            job_data = parseJobContent(job_content)
            if job_data:
                collection.insert_one(job_data)
        print("Jobs stored successfully in the database.")
    except Exception as error:
        traceback.print_exc()
        print("Error occurred while storing jobs in the database.")


def parseJobContent(job_content):
    try:
        lines = job_content.split('\n')
        company_name = lines[0]
        job_name = None
        location = None
        salary = None
        description_lines = []
        if lines[1].replace('.', '', 1).isdigit():
            offset = 1
        else:
            offset = 0
        for i in range(1 + offset, len(lines)):
            if lines[i].startswith('$'):
                salary = lines[i]
                break
            elif location is None:
                location = lines[i]
            elif job_name is None:
                job_name = lines[i]
            else:
                description_lines.append(lines[i])
        description = '\n'.join(description_lines)
        if job_name is None and location is None:
            print("Job name and location not found. Skipping entry.")
            return None

        job_data = {
            "job": location,
            "location": job_name,
            "company": company_name,
            "salary": salary,
            "description": description
        }
        return job_data
    except Exception as error:
        traceback.print_exc()
        print("Error occurred while parsing job content.")
        return None


def searchJobName(name):
    driver.get(website_url)
    searchField = driver.find_element(By.XPATH, '//*[@id="searchBar-jobTitle"]')
    searchField.clear()
    searchField.send_keys(name)
    searchField.send_keys(Keys.ENTER)

    showMoreButton = driver.find_element(By.XPATH, '//*[@id="left-column"]/div[2]/div/button')
    showMoreButton.click()
    time.sleep(2)
    driver.execute_script("document.elementFromPoint(window.innerWidth - 1, window.innerHeight / 2).click();")
    time.sleep(2)
    for item in range(0, 4): # each iteration in this loop is 30 jobs found.. so 20 x 30 im getting 600 jobs here but also longer runtime
        showMoreButton = driver.find_element(By.XPATH, '//*[@id="left-column"]/div[2]/div/button')
        showMoreButton.click()
        time.sleep(4)


    jobListUl = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul')
    jobs = jobListUl.find_elements(By.TAG_NAME, 'li')

    job_texts = []

    for job in jobs:
        job_texts.append(job.text)

    return job_texts


# ____________________________________________________ Da Mein (Deftones reference) ____________________________________________________________

datab = connectDataBase()
website_url = "https://www.glassdoor.com/Job/index.htm"

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

jobs2 = searchJobName("Machine Learning Intern")
storeJobsInDB(jobs2)
for job in jobs2:
    print(job)


time.sleep(1000)

driver.quit()




# XPATH TO SHOW MORE BUTTON ON ALL JOBS ON PAGE: //*[@id="left-column"]/div[2]/div/button
# XPATH to joblist ul: /html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul
# XPATH TO FILTER BUTTON: //*[@id="app-navigation"]/div[3]/div[1]/div[1]/button
# job title path: //*[@id="jd-job-title-1009079577173"]
# job location path: //*[@id="app-navigation"]/div[3]/div[2]/div[2]/div/div[1]/header/div[1]/div
# show more job detials button path: //*[@id="app-navigation"]/div[3]/div[2]/div[2]/div/div[1]/section/div[2]/div[2]/button
# whole job desc path: //*[@id="app-navigation"]/div[3]/div[2]/div[2]/div/div[1]/section/div[2]