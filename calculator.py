# when user hits "calculate" button, calculates all possible schedules

import requests
from bs4 import BeautifulSoup
import sqlite3
from selenium import webdriver
import re # getting a little lost in the sauce with regex
from selenium.webdriver.common.by import By

DATABASE = "test.db"

def getSelected(): # gets the selected classes from the database
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    results = cursor.execute("SELECT ClassNum FROM SelectedClasses").fetchall()
    class_nums = [row[0].replace("\xa0", " ") for row in results]  # extract normalized class from each tuple
    connection.close()
    return class_nums

def getTimes(selected_class):
    url = "https://catalog.uconn.edu/course-search/?details&code=" + selected_class.replace(" ", "%20")
    print(url)
    driver = webdriver.Chrome() # uconn just has to make this extra hard for me
    driver.get(url)
    driver.implicitly_wait(10)
    section_info = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/div[18]/div/div/div[1]').text

    # split the section info into lines
    section_lines = section_info.split("\n")[1:]

    # dictionary to store all the sections of a class
    sections = {
        "Class": selected_class,
        "Lecture":[], # must be paired with discussion or lab
        "Discussion":[],
        "Lab":[],
        "LSA":[] # means it is standalone, no need to take lab/discussion/lecture
    }
    
    # parses data
    for i in range(0,(len(section_lines)-1),5):
        crn = section_lines[i]
        section = section_lines[i+1]
        type_ = section_lines[i+2]
        meets = section_lines[i+3]
        instructor = section_lines[i+4]

        if type_ == 'DIS':
            sections['Discussion'].append({
                "Section": section,
                "Meets": meets,
                "Instructor": instructor
            })
        elif type_ == 'LEC':
            sections['Lecture'].append({
                "Section": section,
                "Meets": meets,
                "Instructor": instructor
            })
        elif type_ == 'LAB':
            sections['Lab'].append({
                "Section": section,
                "Meets": meets,
                "Instructor": instructor
            })
        else:
            sections['LSA'].append({
                "Section": section,
                "Meets": meets,
                "Instructor": instructor
            })
    
    print(sections)
    return sections

if __name__ == "__main__":
    selected_classes = getSelected()
    # print(selected_classes)
    for i in selected_classes:
        getTimes(i)