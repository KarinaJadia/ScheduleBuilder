step one: initialize database using sqlite in the terminal like so:

    sqlite3 test.db
    .read courses.sql

step two: run course_codes.py to populate the database

step three: navigate to main.go and start the website in the terminal like so:

    go run main.go

step four: search and add classes you want to take

step five: run calculator.py to populate scheds.txt

step six: run calc_dbfier.py to send scheds.txt stuff to database

step seven: tbd...