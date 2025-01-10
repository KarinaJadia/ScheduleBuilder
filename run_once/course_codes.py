# extracts list of classes and writes them to file

import requests
from bs4 import BeautifulSoup
import re # getting a little lost in the sauce with regex

if __name__ == "__main__":
    url = 'https://catalog.uconn.edu/undergraduate/courses/#coursestext' # courses url
    courses = []

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
                file.write(f'{code}\n')

    # print(courses)