# extracts list of classes and writes them to database

import requests
from bs4 import BeautifulSoup
import re # getting a little lost in the sauce with regex
import sqlite3

DATABASE = "test.db"

def courseNames(url): # gets the course names
    courses = [] # stores the course name and code in this format: Accounting (ACCT)
    codes = []

    # this section is for reading the webpage and extracting the names
    try:
        response = requests.get(url)
        response.raise_for_status()

        # parse html
        soup = BeautifulSoup(response.text, 'html.parser')

        # extract the course codes
        course_links = soup.find_all('a')  # find all anchor tags
        for link in course_links:
            if link.text.strip() and '(' in link.text:  # only taking courses
                course_name = link.text.strip()
                course_name = course_name.replace("(RH)", "").strip()  # remove '(RH)' and clean up any extra spaces
                if course_name in courses:  # avoid duplicates
                    break
                courses.append(course_name)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    # this section is for saving the course codes
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    for course in courses:
        name, code = '',''
        match = re.search(r'\((.*?)\)', course) # gets everything in the ()
        if match:
            code = match.group(1)
            codes.append(code)

        match = re.match(r'^(.*?)\s*\(', course)  # gets everything before the (
        if match:
            name = match.group(1).strip() 

        cursor.execute("INSERT OR REPLACE INTO Courses (CourseName, CourseCode) VALUES (?, ?)", [name, code])
    
    connection.commit()
    connection.close()

    print('successfully populated courses table')

    return codes

def codes(url): # gets the individual courses in each school
    codes = courseNames(url)
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    for code in codes:
        url = 'https://catalog.uconn.edu/undergraduate/courses/' + code.lower() + '/' # only works in lowercase
        print(f'doing {code}')

        try:
            
            response = requests.get(url)
            response.raise_for_status()

            # parse html
            soup = BeautifulSoup(response.text, 'html.parser')

            # extract the individual courses
            course_links = soup.find_all('a')  # find all anchor tags
            for link in course_links:
                if code in link.text.strip() and re.search(r'\d', link.text.strip()):  # only taking courses with numbers
                    name = link.text.strip()
                    code = ''

                    match = re.match(r'^(.*?)(?=\d)', name) # gets the letters before the code
                    if match:
                        code = match.group(1).strip()

                    cursor.execute("INSERT OR REPLACE INTO Classes (ClassNum, ClassCode) VALUES (?, ?)", [name, code])

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    connection.commit()
    connection.close()

    print('successfully populated classes table')

if __name__ == "__main__":
    codes('https://catalog.uconn.edu/undergraduate/courses/#coursestext')