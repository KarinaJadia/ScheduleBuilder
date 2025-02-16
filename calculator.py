# when user hits "calculate" button, calculates all possible schedules

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import itertools

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

def generate_class_options(class_data):
    options = []
    # Process each Lecture in the class
    for lecture in class_data.get('Lecture', []):
        links = lecture.get('Links', [])
        # Group links by their Type (e.g., LAB, DIS)
        type_groups = {}
        for link in links:
            link_type = link.get('Type', '')
            if link_type not in type_groups:
                type_groups[link_type] = []
            type_groups[link_type].append(link)
        # Generate combinations for each type group
        groups = list(type_groups.values())
        if not groups:  # No linked components
            options.append([lecture])
        else:
            # Generate Cartesian product of all groups
            for combo in itertools.product(*groups):
                option = [lecture] + list(combo)
                options.append(option)
    # Process each LSA in the class
    for lsa in class_data.get('LSA', []):
        options.append([lsa])
    return options

def generate_all_schedules(all_classes_data):
    # Generate options for each class
    all_class_options = []
    for class_data in all_classes_data:
        class_options = generate_class_options(class_data)
        all_class_options.append(class_options)
    
    # Generate all possible combinations across classes
    all_schedules = []
    for schedule_combination in itertools.product(*all_class_options):
        # Flatten the combination into a single list of components
        components = []
        for option in schedule_combination:
            components.extend(option)
        
        # Check for time conflicts between all pairs of components
        conflict_found = False
        for i in range(len(components)):
            for j in range(i + 1, len(components)):
                section1 = components[i]
                section2 = components[j]
                # Extract meeting times for each section
                meeting1 = section1.get('Meets', {})
                meeting2 = section2.get('Meets', {})
                # Check for conflicts using your time_conflicts function
                if time_conflicts(meeting1, meeting2):
                    conflict_found = True
                    break
            if conflict_found:
                break
        
        # If no conflicts, add the schedule to the list
        if not conflict_found:
            all_schedules.append(components)
    
    return all_schedules

if __name__ == "__main__":

    selected_classes = getSelected()
    for i in selected_classes:
        sections = getSections(i)
        all_classes.append(sections)
        print(sections)
        
    schedules = generate_all_schedules(all_classes)
    # print(schedules)
    with open('scheds.txt', 'w') as f:
        for i in schedules:
            # Join the list of strings into a single string
            f.write("".join([f"{line}\n" for line in i]))
            f.write('\n')  # Add an extra newline between schedules
    print('done!')
    
    # x = generate_schedules(all_classes)
    # for i in x:
    #     print(i)
    #     print()