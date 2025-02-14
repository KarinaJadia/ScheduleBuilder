# when user hits "calculate" button, calculates all possible schedules

import sqlite3
from selenium import webdriver
import re # getting a little lost in the sauce with regex
from selenium.webdriver.common.by import By
from itertools import product

DATABASE = "test.db"
all_classes = []

def getSelected(): 
    '''gets the selected classes from the database'''
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    results = cursor.execute("SELECT ClassNum FROM SelectedClasses").fetchall()
    class_nums = [row[0].replace("\xa0", " ") for row in results]  # extract normalized class from each tuple
    connection.close()
    return class_nums

def getSections(selected_class): 
    '''gets the sections from a selected class'''
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
            "Meets": parse_time(meets),
            "Instructor": instructor,
            "Links": {}
        }

        if type_ == 'LEC':
            section_entry["Type"] = "Lecture"
            section_entry["Links"] = link_sections(section_entry["CRN"])
            sections["Lecture"].append(section_entry)
        else:
            section_entry["Type"] = "LSA"
            sections["LSA"].append(section_entry)

    return sections

def link_sections(crn):
    '''links discussions and labs to lectures'''
    # all_classes[]
    url = "https://catalog.uconn.edu/course-search/?details&crn=" + crn

    driver = webdriver.Chrome() # uconn just has to make this extra hard for me
    driver.get(url)
    driver.implicitly_wait(10)
    section_info = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/div[13]/div/div/div').text
    driver.quit()

    # split the section info into lines
    secs = []
    section_lines = section_info.split("\n")[1:]
    # print(section_lines)
    # clearing up list because they did such a fuckass job with the data
    filters = ['CRN:','Section #:', 'Type:', 'Meets:', 'Instructor:']
    for f in filters:
        while f in section_lines:
            section_lines.remove(f)

    for i in range(0, len(section_lines), 5):
        crn = section_lines[i]
        section = section_lines[i+1]
        type_ = section_lines[i+2]
        meet_time_raw = section_lines[i+3]
        meets = parse_time(meet_time_raw)
        professors = section_lines[i+4]

        section_entry = {
            "CRN": crn,
            "Section": section,
            "Type": type_,
            "Meets": meets,
            "Instructor": professors
        }
        secs.append(section_entry)
    # print(secs)
    return secs

def to_minutes(t): # helper for parse_time
        hour, minute = map(int, t[:-1].split(':'))
        if t[-1] == 'p' and hour != 12:  # convert PM to 24-hour
            hour += 12
        elif t[-1] == 'a' and hour == 12:  # convert 12 AM to 0
            hour = 0
        return hour * 60 + minute

def parse_time(meeting_time): # parse meeting time into start and end times eg 'MW 10:10-11a'
    meeting_times = []

    if meeting_time == 'Does Not Meet':
        return False
    
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

        start, end = str(to_minutes(start)+5), str(to_minutes(end)+5) # +5 for buffer

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

    return tots # returns in format {'starts': [M 100, W 100], 'ends': {M 200, W 200} or False

def time_conflicts(section1, section2): # check if two sections conflict based on meeting times (takes meeting times)
    """
    takes 2 section meeting times, returns false if no conflicts and true if conflicts
    make sure to only pass meeting times, so like sections['class']['meeting'] for both
    """
    if not section1 or not section2: # if one section does not meet
        return False # no conflicts
    
    for s1st in section1['starts']:
        s1st = s1st.split() # so it should become ['M', 200]
        s1st[1] = int(s1st[1])
        for i, s2en in enumerate(section2['ends']):
            s2en = s2en.split() # so it should become ['M', 200]
            s2en[1] = int(s2en[1])
            if s1st[0] == s2en[0] and s1st[1] < s2en[1]:
                s2st = section2['starts'][i].split()
                s2st[1] = int(s2st[1])
                if s1st[1] > s2st[1]:
                    return True # conflicts
                
    section2, section1 = section1, section2 # i'm lazy
    for s1st in section1['starts']:
        s1st = s1st.split() # so it should become ['M', 200]
        s1st[1] = int(s1st[1])
        for i, s2en in enumerate(section2['ends']):
            s2en = s2en.split() # so it should become ['M', 200]
            s2en[1] = int(s2en[1])
            if s1st[0] == s2en[0] and s1st[1] < s2en[1]:
                s2st = section2['starts'][i].split()
                s2st[1] = int(s2st[1])
                if s1st[1] > s2st[1]:
                    return True # conflicts

    return False # no conflicts

def is_valid_combination(class_schedule):
    """
    validate a class schedule:
    - ensure Lecture is paired with Lab/Discussion if required
    - allow standalone classes (LSA) but not mixed with Lecture or Lab/Discussion.
    - check for time conflicts within the class.
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
    generates all possible schedules given classes, then passes all possibilities to is_valid_cobination
    """
    print('starting validation')

    for c in classes:
        print(c)
        # print(c['Lecture'] + c['Lab'] + c['Discussion'])
        # print(c['LSA'])

    # all_combinations = product(*[class_sections["Lecture"] + class_sections["Lab"] + class_sections["Discussion"] + class_sections["LSA"] for class_sections in classes])

    # valid_schedules = []
    # i = 1
    # for combination in all_combinations:
    #     if i%100 == 0:
    #         print(f'testing...{i}')
    #     i+=1
    #     if is_valid_combination(combination):
    #         # check for overall time conflicts between classes
    #         print('checking a schedule...')
    #         if not any(time_conflicts(s1, s2) for i, s1 in enumerate(combination) for s2 in combination[i+1:]):
    #             valid_schedules.append(combination)
    #             print('successful schedule added!')
    # return valid_schedules

if __name__ == "__main__":

    selected_classes = getSelected()
    for i in selected_classes:
        sections = getSections(i)
        all_classes.append(sections)
        # print(sections)
        
    generate_schedules(all_classes)
    # print(all_classes)

    # x = generate_schedules(all_classes)
    # for i in x:
    #     print(i)
    #     print()