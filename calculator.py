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
    driver.implicitly_wait(10)
    section_info = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/div[18]/div/div/div[1]').text
    print(section_info)

if __name__ == "__main__":
    selected_classes = getSelected()
    print(selected_classes)
    for i in selected_classes:
        getTimes(i)
        break