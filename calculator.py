# when user hits "calculate" button, calculates all possible schedules

import requests
from bs4 import BeautifulSoup
import sqlite3
from selenium import webdriver
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
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        response = requests.get(url)
        response.raise_for_status()

        # parse html
        soup = BeautifulSoup(response.text, 'html.parser')
        # with open("response.txt", "w") as file:
        #     file.write(response.text)
        # print(response.text)

        grid = soup.find_all('a')  # Use the correct tag and class name

        # loop through each element and extract data
        for element in grid:
            if element.text.strip() and 'M' in element.text:  # only taking courses
                print(element.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    selected_classes = getSelected()
    print(selected_classes)
    for i in selected_classes:
        getTimes(i)
        break