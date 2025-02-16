DROP TABLE IF EXISTS Courses; -- records all courses for first dropdown
CREATE TABLE Courses (
    CourseName varchar(255), -- the course name, eg Accounting
    CourseCode varchar(255), -- the course code, eg ACCT
    PRIMARY KEY (CourseCode) -- makes sure each course name is unique
);

DROP TABLE IF EXISTS Classes; -- records all classes for second dropdown
CREATE TABLE Classes (
    ClassNum varchar(255), -- class name and number, eg ACCT 2001
    ClassCode varchar(255), -- class code, eg "ACCT"
    PRIMARY KEY (ClassNum), -- makes sure each class name is unique
    FOREIGN KEY (ClassCode) REFERENCES Courses(CourseCode) -- links to Courses table
);

DROP TABLE IF EXISTS SelectedClasses; -- records selected classes for computation
CREATE TABLE SelectedClasses (
    ClassNum varchar(255), -- class name and number, eg ACCT 2001
    PRIMARY KEY (ClassNum), -- makes sure each class name is unique
    FOREIGN KEY (ClassNum) REFERENCES Classes(ClassNum) -- links to classes table
);

DROP TABLE IF EXISTS Schedules;
CREATE TABLE Schedules (
    ScheduleID INT, -- each class in here should be linked to a schedule id
    ClassNum varchar(255), -- class name and number, eg ACCT 2001
    ClassType varchar(255), -- class type, eg lab
    ClassSection varchar(255), -- class section, eg 101L
    ClassTime varchar(255), -- class time, eg 'starts': ['W 680'], 'ends': ['W 730']
    Professor varchar(255), -- professor listed for class
);