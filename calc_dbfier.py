import sqlite3
import json
from contextlib import closing

DATABASE = "test.db"

def parse_meets(meets_data):
    """convert meets data to a readable time string"""
    if isinstance(meets_data, bool) and not meets_data:
        return None  # handle 'Meets': false case
    
    time_slots = []
    for start, end in zip(meets_data['starts'], meets_data['ends']):
        # split day and time components
        start_day, start_time = start.split()
        end_day, end_time = end.split()
        
        # convert 3-digit time to proper format (e.g., 755 → 7:55 AM)
        def format_time(time_str):
            hour = int(time_str[:-2]) if len(time_str) > 2 else int(time_str[0])
            mins = time_str[-2:]
            period = "AM" if hour < 12 else "PM"
            if hour > 12: hour -= 12
            return f"{hour}:{mins} {period}"
        
        # create time range string
        time_slots.append(f"{start_day} {format_time(start_time)}-{format_time(end_time)}")
    
    return ', '.join(time_slots)

def process_schedules():
    # connect to SQLite database
    with closing(sqlite3.connect(DATABASE)) as conn:
        cursor = conn.cursor()
        
        # create table
        cursor.execute('''DROP TABLE IF EXISTS Schedules''')
        cursor.execute('''
            CREATE TABLE Schedules (
                ScheduleID INT,
                ClassNum TEXT,
                ClassType TEXT,
                ClassSection TEXT,
                ClassTime TEXT,
                Professor TEXT
            )
        ''')
        
        # process schedules
        current_schedule = None
        compound_str = ''
        
        with open('scheds.txt', 'r') as file:
            for line in file:
                if line.startswith('schedule '):
                    if current_schedule is not None:
                        process_schedule(current_schedule, compound_str, cursor)
                        compound_str = ''
                    current_schedule = int(line.strip().split()[1])
                else:
                    compound_str += line
            # process last schedule
            if current_schedule is not None:
                process_schedule(current_schedule, compound_str, cursor)
        
        conn.commit()

def process_schedule(schedule_id, compound_str, cursor):
    """process one schedule's data and insert into database"""
    classes = []
    decoder = json.JSONDecoder()
    pos = 0
    
    while pos < len(compound_str):
        # Skip whitespace
        while pos < len(compound_str) and compound_str[pos].isspace():
            pos += 1
        if pos >= len(compound_str):
            break
        
        try:
            obj, idx = decoder.raw_decode(compound_str[pos:])
            classes.append(obj)
            pos += idx
        except json.JSONDecodeError:
            break
    
    # prepare data for insertion
    insert_data = []
    for cls in classes:
        # handles class number (split "PHYS 1501Q LAB" to "PHYS 1501Q")
        class_num = ' '.join(cls['Class'].split()[:2]) if ' ' in cls['Class'] else cls['Class']
        
        insert_data.append((
            schedule_id,
            class_num,
            cls.get('Type', 'N/A'),
            cls.get('Section', 'N/A'),
            parse_meets(cls['Meets']) if 'Meets' in cls else None,
            cls.get('Instructor', 'TBA')
        ))
    
    # insert
    cursor.executemany('''
        INSERT INTO Schedules 
        (ScheduleID, ClassNum, ClassType, ClassSection, ClassTime, Professor)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', insert_data)

if __name__ == "__main__":
    process_schedules()
    print("schedules successfully saved to database!")