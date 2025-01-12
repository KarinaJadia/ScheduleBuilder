# when user hits "calculate" button, calculates all possible schedules

import sqlite3
from selenium import webdriver
import re # getting a little lost in the sauce with regex
from selenium.webdriver.common.by import By
from itertools import product

DATABASE = "test.db"

def getSelected(): # gets the selected classes from the database
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    results = cursor.execute("SELECT ClassNum FROM SelectedClasses").fetchall()
    class_nums = [row[0].replace("\xa0", " ") for row in results]  # extract normalized class from each tuple
    connection.close()
    return class_nums

def getSections(selected_class): # gets the sections from a selected class
    url = "https://catalog.uconn.edu/course-search/?details&code=" + selected_class.replace(" ", "%20")
    print(f'getting data for {selected_class}')
    driver = webdriver.Chrome() # uconn just has to make this extra hard for me
    driver.get(url)
    driver.implicitly_wait(10)
    section_info = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/div[18]/div/div/div[1]').text
    driver.quit()

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

        for i in range(0, (len(section_lines) - 1), 5):
            crn = section_lines[i]
            section = section_lines[i + 1]
            type_ = section_lines[i + 2]
            meets = section_lines[i + 3]
            instructor = section_lines[i + 4]

            section_entry = {
                # "CRN": crn,
                "Section": section,
                "Meets": meets,
                "Instructor": instructor
            }

            if type_ == 'DIS':
                sections["Discussion"].append(section_entry)
            elif type_ == 'LEC':
                sections["Lecture"].append(section_entry)
            elif type_ == 'LAB':
                sections["Lab"].append(section_entry)
            else:
                sections["LSA"].append(section_entry)

    return sections

def parse_time(meeting_time): # parse meeting time into start and end times eg 'MW 10:10-11a'
    days, times = meeting_time.split()
    start, end = times.split('-')

    # handles the times
    if ":" not in start:
        start = start[0:-1] + ":00" + start[-1]
    if ":" not in end:
        end = end[0:-1] + ":00" + end[-1]

    # convert to 24-hour format
    def to_minutes(t):
        hour, minute = map(int, t[:-1].split(':'))
        if t[-1] == 'p' and hour != 12:  # convert PM to 24-hour
            hour += 12
        elif t[-1] == 'a' and hour == 12:  # convert 12 AM to 0
            hour = 0
        return hour * 60 + minute
    return days, to_minutes(start), to_minutes(end)

if __name__ == "__main__":

    selected_classes = getSelected()
    all_classes = []
    for i in selected_classes:
        sections = getSections(i)
        all_classes.append(sections)
        print(sections)