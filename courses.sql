-- sqlite3 test.db
-- .read courses.sql

DROP TABLE IF EXISTS Courses;
CREATE TABLE Courses (
    CourseName varchar(255), -- the course name, eg Accounting
    CourseCode varchar(255), -- the course code, eg ACCT
    PRIMARY KEY (CourseCode) -- makes sure each course name is unique
);

DROP TABLE IF EXISTS CourseNames;
CREATE TABLE CourseNames (
    CourseNum varchar(255), -- course name and number, eg ACCT 2001
    CourseCode varchar(255), -- course code, eg "ACCT"
    PRIMARY KEY (CourseNum), -- makes sure each course name is unique
    FOREIGN KEY (CourseCode) REFERENCES Courses(CourseCode) -- links to Courses table
);