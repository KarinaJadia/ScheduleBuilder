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

        section_entry = {
            "Class": selected_class,
            "CRN": crn,
            "Section": section,
            "Type": None,  # Will be updated below
            "Meets": meets,
            "Instructor": instructor
        }

        if type_ == 'DIS':
            section_entry["Type"] = "Discussion"
            sections["Discussion"].append(section_entry)
        elif type_ == 'LEC':
            section_entry["Type"] = "Lecture"
            sections["Lecture"].append(section_entry)
        elif type_ == 'LAB':
            section_entry["Type"] = "Lab"
            sections["Lab"].append(section_entry)
        else:
            section_entry["Type"] = "LSA"
            sections["LSA"].append(section_entry)

    return sections

def to_minutes(t):
        hour, minute = map(int, t[:-1].split(':'))
        if t[-1] == 'p' and hour != 12:  # convert PM to 24-hour
            hour += 12
        elif t[-1] == 'a' and hour == 12:  # convert 12 AM to 0
            hour = 0
        return hour * 60 + minute

def parse_time(meeting_time): # parse meeting time into start and end times eg 'MW 10:10-11a'
    meeting_times = []
    if ';' in meeting_time:
        meeting_times = meeting_time.split(';')
    else:
        meeting_times.append(meeting_time)

    tots = {
        "starts": [],
        "ends": []
    }
    for meeting_time in meeting_times:

        days, times = meeting_time.split()
        start, end = times.split('-')

        # handles improper formats
        if 'a' not in start and 'p' not in start:
            start = start + end[-1]
        if ":" not in start:
            start = start[0:-1] + ":00" + start[-1]
        if ":" not in end:
            end = end[0:-1] + ":00" + end[-1]

        start, end = str(to_minutes(start)), str(to_minutes(end))

        # makes T and Th proper
        days_split = list(days)
        if 'h' in days_split:
            x = days_split.index('h')
            del days_split[x]
            days_split[x-1] = 'Th'
        
        # creates a dictionary with all starts and all ends
        for d in days_split:
            tots['starts'].append(d + ' ' + start)
            tots['ends'].append(d + ' ' + end)

    return tots

def time_conflicts(section1, section2): # check if two sections conflict based on meeting times

    if section1['Meets'] == 'Does Not Meet' or section2['Meets'] == 'Does Not Meet':
        return False
    
    s1 = parse_time(section1['Meets'])
    s2 = parse_time(section2['Meets'])

    print(s1,'\n', s2)
    for start1, end1 in zip(s1['starts'], s1['ends']):
        day1, time1_start = start1.split()
        _, time1_end = end1.split()
        time1_start = int(time1_start)
        time1_end = int(time1_end)

        for start2, end2 in zip(s2['starts'], s2['ends']):
            day2, time2_start = start2.split()
            _, time2_end = end2.split()
            time2_start = int(time2_start)
            time2_end = int(time2_end)

            # Check if the days overlap
            if day1 == day2:
                # Check if the times overlap
                if not (time1_end <= time2_start or time2_end <= time1_start):
                    return True  # Conflict found
    return False  # No conflicts

def is_valid_combination(class_schedule):
    """
    Validate a class schedule:
    - Ensure Lecture is paired with Lab/Discussion if required.
    - Allow standalone classes (LSA) but not mixed with Lecture or Lab/Discussion.
    - Check for time conflicts within the class.
    """
    lectures = [sec for sec in class_schedule if sec["Type"] == "Lecture"]
    labs = [sec for sec in class_schedule if sec["Type"] in {"Lab", "Discussion"}]
    lsa = [sec for sec in class_schedule if sec["Type"] == "LSA"]

    # LSA validation
    if lsa:
        # Valid if only LSAs are present and no Lectures or Labs/Discussions
        return len(lectures) == 0 and len(labs) == 0

    # Lecture + Lab/Discussion validation
    if lectures and labs:
        # Check if any Lecture and Lab/Discussion pairing is valid
        for lecture in lectures:
            for lab in labs:
                if not time_conflicts(lecture, lab):
                    return True  # Valid pairing

    # If neither condition is met, the combination is invalid
    return False

def generate_schedules(classes):
    """
    Generate all possible schedules given classes.
    - Each class must meet the Lecture+Lab/Discussion or LSA condition.
    - No time conflicts between sections.
    """
    print('starting validation')
    all_combinations = product(*[class_sections["Lecture"] + class_sections["Lab"] + class_sections["Discussion"] + class_sections["LSA"] for class_sections in classes])

    valid_schedules = []
    i = 1
    for combination in all_combinations:
        if i%100 == 0:
            print(f'testing...{i}')
        i+=1
        if is_valid_combination(combination):
            # check for overall time conflicts between classes
            print('checking a schedule...')
            if not any(time_conflicts(s1, s2) for i, s1 in enumerate(combination) for s2 in combination[i+1:]):
                valid_schedules.append(combination)
                print('successful schedule added!')
    return valid_schedules

if __name__ == "__main__":

    # print(parse_time('MW 10:10-11a'))
    # print(parse_time('TTh 11a-12:40p'))
    # print(parse_time('MWF 1-2:40p'))
    # print(parse_time('TTh 11a-1p'))
    # print(parse_time('MW 9-9:45a; F 9:05-10:45a'))
    # print(parse_time('TTh 11a-1p; F 9:05-10:45a'))
    
    selected_classes = getSelected()
    all_classes = []
    for i in selected_classes:
        sections = getSections(i)
        all_classes.append(sections)
        # print(sections)

    x = generate_schedules(all_classes)
    for i in x:
        print(i)
        print()