import sqlite3
import json

DATABASE = "test.db"

if __name__ == "__main__":

    schedule = 0
    start = 0
    stop = 0
    with open('scheds.txt', 'r') as file:
        for i, line in enumerate(file):
            
            if 'schedule' in line:
                schedule = int(line[9:])
                start = i + 2
                if i > 2:
                    stop = i - 2

            if i > 5000:
                break