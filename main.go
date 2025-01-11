package main

import (
	"database/sql"
	"html/template"
	"log"
	"net/http"

	_ "modernc.org/sqlite"
)

type Courses struct {
	CourseName string
	CourseCode string
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
		
		var data []Courses
		for rows.Next() {
			var d Courses
			if err := rows.Scan(&d.CourseName, &d.CourseCode); err != nil {
				http.Error(w, "Database scan error", http.StatusInternalServerError)
				return
			}
			data = append(data, d)
		}

		if err := tmpl.Execute(w, data); err != nil {
			http.Error(w, "Template execution error", http.StatusInternalServerError)
			return
		}
	})

	// create server
	log.Println("opening website on http://localhost:8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}