# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from api import jsonify
import os
import pickle

os.environ["PYTHONIOENCODING"] = "utf-8"

#credentials
username = ""
password = ""

def linkedInAuth():
    try:
        chrome_path = r"D:\Work\Selenium Scraper\chromedriver\chromedriver.exe"
        chrome_options = Options()
        # chrome_options.add_argument("--user-data-dir=selenium")
        driver = webdriver.Chrome(chrome_path, options=chrome_options)
        # chrome_options.add_argument("user-data-dir=selenium")
        driver.implicitly_wait(15)
        driver.get('https://www.linkedin.com/')
        email_field = driver.find_element_by_xpath("""/html/body/nav/section[2]/form/div[1]/div[1]/input""")
        email_field.send_keys(username)
        password_field = driver.find_element_by_xpath("""/html/body/nav/section[2]/form/div[1]/div[2]/input""")
        password_field.send_keys(password)
        password_field.send_keys(Keys.ENTER)
        pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
        time.sleep(30)
        driver.quit()
    except Except as e:
        print('Auth Error, message: \n')
        print(e)

def profileDataExtractor(link):
    chrome_path = r"D:\Work\Selenium Scraper\chromedriver\chromedriver.exe"
    chrome_options = Options()
    # chrome_options.add_argument("--user-data-dir=selenium")
    #
    # NOTE: TRY MANUAL LOADING OF COOKIES FOR HEADLESS SCRAPING
    #
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_path, options=chrome_options)
    # chrome_options.add_argument("user-data-dir=selenium")
    ###change this to variable for production for api call
    try:
        driver.get(link)
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            driver.add_cookie(cookie)
        driver.refresh()
    except NoSuchElementException:
        print('error')
        driver.quit()
        info = {}
        data = {}
        info["message"] = "url Error"
        info["data"] = data
        return jsonify(info)
    wait = WebDriverWait(driver, 20)
    try:
        print("explicit")
        wait.until(EC.presence_of_element_located((By.XPATH, '//*/ol')))
    except:
        print("sleeping 5 sec")
        time.sleep(5)
    #scroll down to fix ajax issue
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
    time.sleep(5)

    #to click show more skills
    try:
        element = driver.find_element_by_xpath('//*/span[3]/span/a')
        driver.execute_script("(arguments[0]).click();", element)
    except NoSuchElementException:
        pass
    try:
        buts = driver.find_element_by_tag_name('button.pv-profile-section__card-action-bar')
        driver.execute_script("(arguments[0]).click();", buts)
    except NoSuchElementException:
        pass

    full_name = xpath_extractor('//*/div[2]/div[2]/div[1]/ul[1]/li[1]', driver)
    region_and_country = xpath_extractor('//*/div[2]/div[2]/div[1]/ul[2]/li[1]', driver)
    headline = xpath_extractor('//*/div[2]/div[2]/div[1]/h2', driver)
    education = get_education(driver)
    highlighted = ""
    employment = get_employments(driver)
    language = ""
    try:
        description = str(driver.find_element_by_tag_name('span.lt-line-clamp__raw-line').text)
    except NoSuchElementException:
        description = ""
    try:
        photo_src = str(driver.find_element_by_tag_name('img.pv-top-card-section__photo').get_attribute("src"))
    except NoSuchElementException:
        photo_src = ""
    skills = get_skills(driver)

    info = {}
    data = {}
    data["full_name"] = full_name
    # print(data["full_name"])
    data["region_and_country"] = region_and_country
    # print(data["region_and_country"])
    data["headline"] = headline
    # print(["headline"])
    data["education"] = education
    # print(["education"])
    data["highlighted"] = highlighted
    # print(data["highlighted"])
    data["employment"] = employment
    # print(data["employment"])
    data["description"] = description
    # print(data["description"])
    data["photo_src"] = photo_src
    # print(data["photo_src"])
    data["skills"] = skills
    # print(data["skills"])
    info["message"] = "Success"
    info["data"] = data
    driver.quit()
    return jsonify(info)



def get_education(driver):
    education = []
    try:
        ul = driver.find_element_by_css_selector('#education-section')
        lis = ul.find_elements_by_tag_name("li")
        for li in lis:
            try:
                edu_uni = (str(li.find_element_by_tag_name("h3").text))
            except NoSuchElementException:
                edu_uni = ""
            try:
                edu_degree = str(li.find_element_by_xpath('//*/div[2]/div/p[1]').text)
            except NoSuchElementException:
                edu_degree = ""
            try:
                edu_field = str(li.find_element_by_xpath('//*/div[2]/div/p[2]').text)
            except NoSuchElementException:
                edu_field = ""
            try:
                edu_start = str(li.find_element_by_xpath('//*/div[2]/p/span[2]/time[1]').text)
            except NoSuchElementException:
                edu_start = ""
            try:
                edu_end = str(li.find_element_by_xpath('//*/div[2]/p/span[2]/time[2]').text)
            except NoSuchElementException:
                edu_end = ""
            try:
                edu_notes = str(li.find_element_by_tag_name('p.pv-entity__description').text)
            except NoSuchElementException:
                edu_notes = ""
            education.append({"edu_uni": edu_uni, "edu_degree": edu_degree, "edu_field": edu_field,"edu_start": edu_start, \
                "edu_end": edu_end, "edu_notes": edu_notes})
    except NoSuchElementException:
        pass
    return education


def xpath_extractor(xpaths, driver):
    try:
        data = ((driver.find_element_by_xpath(xpaths).text))
    except NoSuchElementException:
        data = ""
    return data

def get_employments(driver):
    employments = []
    try:
        ul = driver.find_element_by_css_selector('#experience-section')
        lis = ul.find_elements_by_tag_name("li")
        for li in lis:
            try:
                job_title = str(li.find_element_by_tag_name("h3").text)
            except NoSuchElementException:
                job_title = ""
            try:
                job_company = str(li.find_element_by_tag_name("p.pv-entity__secondary-title").text)
            except NoSuchElementException:
                job_company = ""
            try:
                date_employed = str(li.find_element_by_tag_name("h4.pv-entity__date-range").text)
            except NoSuchElementException:
                date_employed = ""
            try:
                employment_duration = str(li.find_element_by_tag_name("span.pv-entity__bullet-item-v2").text)
            except NoSuchElementException:
                employment_duration = ""
            try:
                job_description = str(li.find_element_by_tag_name("p.pv-entity__description").text)
            except NoSuchElementException:
                job_description = ""
            try:
                job_location = str(li.find_element_by_tag_name("h4.pv-entity__location").text)
            except NoSuchElementException:
                job_location = ""
            employments.append({"job_title": job_title, "job_company": job_company, "date_employed": date_employed, \
                "employment_duration": employment_duration, "job_description": job_description, "job_location": job_location})
    except NoSuchElementException:
        pass
    return employments

def get_skills(driver):
    skills = []
    try:
        ol = driver.find_element_by_xpath('//*/ol')
        lis = ol.find_elements_by_tag_name("span.pv-skill-category-entity__name-text.t-16.t-black.t-bold")
        for li in lis:
            skills.append({"skill": str(li.text)})
        time.sleep(2)
    except NoSuchElementException:
        pass
    try:
        ol_ = driver.find_element_by_css_selector('#skill-categories-expanded')
        lis_ = ol_.find_elements_by_tag_name("li") 
        for li in lis_:
            skills.append({"skill-more": str(li.find_element_by_tag_name("span.pv-skill-category-entity__name-text.t-16.t-black.t-bold").text)})
    except NoSuchElementException:
        pass
    return skills

