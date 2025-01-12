DROP TABLE IF EXISTS Courses;
CREATE TABLE Courses (
    CourseName varchar(255), -- the course name, eg Accounting
    CourseCode varchar(255), -- the course code, eg ACCT
    PRIMARY KEY (CourseCode) -- makes sure each course name is unique
);

DROP TABLE IF EXISTS Classes;
CREATE TABLE Classes (
    ClassNum varchar(255), -- class name and number, eg ACCT 2001
    ClassCode varchar(255), -- class code, eg "ACCT"
    PRIMARY KEY (ClassNum), -- makes sure each course name is unique
    FOREIGN KEY (ClassCode) REFERENCES Courses(CourseCode) -- links to Courses table
);

DROP TABLE IF EXISTS SelectedClasses;
CREATE TABLE SelectedClasses (
    ClassNum varchar(255), -- class name and number, eg ACCT 2001
    FOREIGN KEY (ClassNum) REFERENCES Classes(ClassNum) -- links to Classes table
);