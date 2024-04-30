import traceback
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time
import pymongo
import re
from datetime import datetime, timedelta


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
        collection = db.foundJobsSecondSet
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
        time_ago_posted = None
        skills = []
        job_link = None

        if lines[1].replace('.', '', 1).isdigit():
            offset = 1
        else:
            offset = 0

        for i in range(1 + offset, len(lines)):
            line = lines[i].strip()
            if line.startswith('$'):
                salary = line
            elif location is None:
                location = line
            elif job_name is None:
                job_name = line
            elif re.match(r'\d+[a-z]+', line):  # Matches "30d+", "2d", etc.
                time_ago_posted = line
            elif re.match(r'Skills:', line):  # Matches "Skills: ..." line
                skills.extend(line.split(':')[1].strip().split(','))
            else:
                description_lines.append(line)

            # Find the link in the job content
            if line.startswith('Job Link:'):
                job_link = line.split('Job Link:')[1].strip()

        description = '\n'.join(description_lines)

        if job_name is None and location is None:
            print("Job name and location not found. Skipping entry.")
            return None

        # Calculate posted date
        if time_ago_posted:
            posted_days = int(re.match(r'(\d+)', time_ago_posted).group(1))
            posted_date = datetime.now() - timedelta(days=posted_days)
            time_ago_posted = posted_date.strftime("%Y-%m-%d")

        job_data = {
            "job": location,
            "location": job_name,
            "company": company_name,
            "salary": salary,
            "description": description,
            "time_ago_posted": time_ago_posted,
            "skills": skills,
            "job_link": job_link
        }

        return job_data

    except Exception as error:
        traceback.print_exc()
        print("Error occurred while parsing job content.")
        return None


def searchJobName(name, location):
    # finding information we want
    try:

        # opening up glassdoor and searching for our jobs
        driver.get(website_url)
        time.sleep(3)  # we need a 12 second buffer between each new search at least to avoid exceeding rate limits per minute
        searchField = driver.find_element(By.XPATH, '//*[@id="searchBar-jobTitle"]')
        searchField.clear()
        searchField.send_keys(name)

        time.sleep(3)

        searchLocationField = driver.find_element(By.XPATH, '//*[@id="searchBar-location"]')
        searchLocationField.clear()
        searchLocationField.send_keys(location)

        searchField.send_keys(Keys.ENTER)

        time.sleep(3)
        '''
        jobFilterButton = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/button')
        jobFilterButton.click()

        positionTypeButton = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/div/div/div[12]/div[1]/button[1]')
        positionTypeButton.click()

        time.sleep(2)

        entryLevelButton = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/div/div/div[12]/div[2]/ul/li[3]/button')
        entryLevelButton.click()

        time.sleep(2)

        applyEntryLevelButton = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[3]/div[1]/div[1]/div/div/div[15]/button[2]')
        applyEntryLevelButton.click()

        time.sleep(5)
        '''

        salaryFilterButton = driver.find_element(By.XPATH, '//*[@id="app-navigation"]/div[3]/div[1]/div[2]/div[1]/button[1]')
        salaryFilterButton.click()
        time.sleep(1)

        # max salary input
        inputField = driver.find_element(By.XPATH, '//*[@id="maxSalaryInput"]')
        for _ in range(4):
            inputField.send_keys(Keys.BACKSPACE)
        inputField.send_keys("80")
        time.sleep(2)

        applyFilterButton = driver.find_element(By.XPATH, '//*[@id="app-navigation"]/div[3]/div[1]/div[2]/div[2]/div[4]/button')
        applyFilterButton.click()

        time.sleep(2)

        # open as many dynamically loaded job cards as possible (the loop)
        try:
            showMoreButton = driver.find_element(By.XPATH, '//*[@id="left-column"]/div[2]/div/button')
            showMoreButton.click()
            time.sleep(2)
            driver.execute_script("document.elementFromPoint(window.innerWidth - 1, window.innerHeight / 2).click();")
            time.sleep(2)
            for item in range(0, 12):  # each iteration in this loop is 30 jobs found
                showMoreButton = driver.find_element(By.XPATH, '//*[@id="left-column"]/div[2]/div/button')
                showMoreButton.click()
                time.sleep(1.5)
        except:
            print("error expanding job grab... perhaps not enough jobs in search")

        # grab all job cards in the ul
        jobListUl = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul')
        jobs = jobListUl.find_elements(By.TAG_NAME, 'li')

        # storing text we found
        job_texts = []
        for job in jobs:
            job_text = job.text
            try:
                job_link = job.find_element(By.XPATH, './/div/div/div[1]/div[1]/a[2]').get_attribute('href')
                job_text += f"\nJob Link: {job_link}"
            except:
                print()
            job_texts.append(job_text)

        return job_texts

    except Exception as error:
        traceback.print_exc()
        print("Error occurred while searching for job names.")
        return None


# ____________________________________________________ Mein (Deftones reference) ____________________________________________________________

datab = connectDataBase()
website_url = "https://www.glassdoor.com/Job/index.htm"

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)



jobs1 = searchJobName("Software Engineering Intern", "United States")
jobs2 = searchJobName("Entry-Level QA Tester", "United States")
jobs3 = searchJobName("Junior Python Developer", "United States")
jobs4 = searchJobName("Web Developer - Entry Level", "United States")
jobs5 = searchJobName("Software Engineering Associate Entry Level", "United States")
jobs6 = searchJobName("Junior Data Analyst", "United States")

'''
# Los Angeles
jobs7 = searchJobName("IT Intern Entry Level", "Los Angeles")
jobs8 = searchJobName("QA Test Intern Entry Level", "Los Angeles")
jobs9 = searchJobName("Data Analyst Intern Entry Level", "Los Angeles")
jobs10 = searchJobName("Game Design Intern Entry Level", "Los Angeles")

# Washington
jobs11 = searchJobName("IT Intern Entry Level", "Washington")
jobs12 = searchJobName("QA Test Intern Entry Level", "Washington")
jobs13 = searchJobName("Data Analyst Intern Entry Level", "Washington")
jobs14 = searchJobName("Game Design Intern Entry Level", "Washington")

# Remote
jobs15 = searchJobName("2D Game Designer Entry Level", "Remote")
jobs16 = searchJobName("Python Intern Entry Level", "Remote")
jobs17 = searchJobName("QA Test Intern Entry Level", "Remote")
'''

storeList = jobs1 + jobs2 + jobs3 + jobs4 + jobs5 + jobs6
# storeList = jobs7 + jobs8 + jobs9 + jobs10 + jobs11 + jobs12 + jobs13 + jobs14 + jobs15 + jobs16 + jobs17
storeJobsInDB(storeList)


time.sleep(500)

driver.quit()

# XPATH TO SHOW MORE BUTTON ON ALL JOBS ON PAGE: //*[@id="left-column"]/div[2]/div/button
# XPATH to joblist ul: /html/body/div[3]/div[1]/div[3]/div[2]/div[1]/div[2]/ul
# XPATH TO FILTER BUTTON: //*[@id="app-navigation"]/div[3]/div[1]/div[1]/button
# job title path: //*[@id="jd-job-title-1009079577173"]
# job location path: //*[@id="app-navigation"]/div[3]/div[2]/div[2]/div/div[1]/header/div[1]/div
# show more job detials button path: //*[@id="app-navigation"]/div[3]/div[2]/div[2]/div/div[1]/section/div[2]/div[2]/button
# whole job desc path: //*[@id="app-navigation"]/div[3]/div[2]/div[2]/div/div[1]/section/div[2]


# for my own testing:
# PATH TO LINK FROM LI:: //*[@id="left-column"]/div[2]/ul/li[1]/div/div/div[1]/div[1]/a[2]
# PATH TO LINK FROM LI:: //*[@id="left-column"]/div[2]/ul/li[2]/div/div/div[1]/div[1]/a[2]
# PATH TO ALL CONTENT IN JOB LISTING: //*[@id="app-navigation"]/div[3]/div[2]/div[2]/div/div[1]/section/div[2]/div[1]


# x path min: //*[@id="app-navigation"]/div[3]/div[1]/div[2]/div[2]/div[3]/input[1]
# x path max: //*[@id="app-navigation"]/div[3]/div[1]/div[2]/div[2]/div[3]/input[2]