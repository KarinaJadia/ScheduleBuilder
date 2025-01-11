package main

import (
	"database/sql"
	"html/template"
	"log"
	"encoding/json"
	"net/http"

	_ "modernc.org/sqlite"
)

type Courses struct {
	CourseName string
	CourseCode string
}

type Classes struct {
	ClassNum string
	ClassCode string
}

// handler function for HTML page
func handler(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "index.html")
}

func main() {
	// SQLite database connection
	db, err := sql.Open("sqlite", "test.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// compile HTML template
	tmpl := template.Must(template.ParseFiles("index.html"))
	
	// handler to fetch data and display it
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		rows, err := db.Query("SELECT CourseName, CourseCode FROM Courses")
		if err != nil {
			http.Error(w, "Database query error: " + err.Error(), http.StatusInternalServerError)
			return
		}
		defer rows.Close()
		
		var courses []Courses
		for rows.Next() {
			var d Courses
			if err := rows.Scan(&d.CourseName, &d.CourseCode); err != nil {
				http.Error(w, "Database scan error: " + err.Error(), http.StatusInternalServerError)
				return
			}
			courses = append(courses, d)
		}

		rows, err = db.Query("SELECT ClassNum, ClassCode FROM Classes")
		if err != nil {
			http.Error(w, "Database query error: " + err.Error(), http.StatusInternalServerError)
			return
		}
		defer rows.Close()
		
		var classes []Classes
		for rows.Next() {
			var d Classes
			if err := rows.Scan(&d.ClassNum, &d.ClassCode); err != nil {
				http.Error(w, "Database scan error: " + err.Error(), http.StatusInternalServerError)
				return
			}
			classes = append(classes, d)
		}

		data := struct {
			Courses []Courses
			Classes []Classes
		}{
			Courses:  courses,
			Classes: classes,
		}	

		if err := tmpl.Execute(w, data); err != nil {
			http.Error(w, "Template execution error: "+ err.Error(), http.StatusInternalServerError)
			return
		}
	})

	// create server
	log.Println("opening website on http://localhost:8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}