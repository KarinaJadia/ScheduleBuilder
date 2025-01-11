# extracts list of classes and writes them to file

import requests
from bs4 import BeautifulSoup
import re # getting a little lost in the sauce with regex

def courseNames(url): # gets the course names
    courses = []
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
                if link.text.strip() in courses: # for some reason it duplicates so 
                    break
                courses.append(link.text.strip())

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    # this section is for saving the course codes
    with open('course_codes.txt', 'w') as file: # writes the course codes to a file
        for course in courses:
            match = re.search(r'\((.*?)\)', course)
            if match:
                code = match.group(1)
                codes.append(code)
                file.write(f'{code}\n') # todo: save to sql file
    
    return codes

def codes(url): # gets the individual courses in each school
    codes = courseNames(url)
    for code in codes:
        url = 'https://catalog.uconn.edu/undergraduate/courses/' + code.lower() + '/' # only works in lowercase
        print(f'doing {code}')
        file = open("courses.txt", "w")
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
                    file.write(f'{name}\n') # todo: save to sql file

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    codes('https://catalog.uconn.edu/undergraduate/courses/#coursestext')