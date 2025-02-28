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
	CourseName string `json:"CourseName"`
	CourseCode string `json:"CourseCode"`
}

type Classes struct {
	ClassNum string `json:"ClassNum"`
	ClassCode string `json:"ClassCode"`
}

type SelectedClasses struct {
	ClassNum string `json:"ClassNum"`
}

type Schedule struct {
    ScheduleID   int    `json:"ScheduleID"`
    ClassNum     string `json:"ClassNum"`
    ClassType    string `json:"ClassType"`
    ClassSection string `json:"ClassSection"`
    ClassTime    sql.NullString `json:"ClassTime"`
    Professor    string `json:"Professor"`
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

		rows, err = db.Query("SELECT ClassNum FROM SelectedClasses")
		if err != nil {
			http.Error(w, "Database query error: "+err.Error(), http.StatusInternalServerError)
			return
		}
		defer rows.Close()
	
		var selectedClasses []SelectedClasses
		for rows.Next() {
			var d SelectedClasses
			if err := rows.Scan(&d.ClassNum); err != nil {
				http.Error(w, "Database scan error: "+err.Error(), http.StatusInternalServerError)
				return
			}
			selectedClasses = append(selectedClasses, d)
		}

		rows, err = db.Query("SELECT * FROM Schedules")
		if err != nil {
			http.Error(w, "Database query error: "+err.Error(), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var schedules []Schedule
		for rows.Next() {
			var s Schedule
			if err := rows.Scan(&s.ScheduleID, &s.ClassNum, &s.ClassType, &s.ClassSection, &s.ClassTime, &s.Professor); err != nil {
				http.Error(w, "Database scan error: "+err.Error(), http.StatusInternalServerError)
				return
			}
			schedules = append(schedules, s)
		}	

		data := struct {
			Courses []Courses
			Classes []Classes
			SelectedClasses []SelectedClasses
			Schedules []Schedule
		}{
			Courses: courses,
			Classes: classes,
			SelectedClasses: selectedClasses,
			Schedules: schedules,
		}
		
		if err := tmpl.Execute(w, data); err != nil {
			http.Error(w, "Template execution error: "+ err.Error(), http.StatusInternalServerError)
			return
		}
	})

	// handler to add classes to selected classes list
	http.HandleFunc("/add-class", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}
	
		// parse JSON body
		var selectedClass SelectedClasses
		if err := json.NewDecoder(r.Body).Decode(&selectedClass); err != nil {
			http.Error(w, "Invalid JSON body: "+err.Error(), http.StatusBadRequest)
			return
		}
	
		// insert class into the database
		_, err := db.Exec("INSERT OR REPLACE INTO SelectedClasses (ClassNum) VALUES (?)", selectedClass.ClassNum)
		if err != nil {
			http.Error(w, "Database insert error: "+err.Error(), http.StatusInternalServerError)
			return
		}
	
		// Respond with the added class as JSON
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(selectedClass)
	})
	
	// handler to delete class from selected classes list
	http.HandleFunc("/delete-class", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodDelete {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}
		var requestData struct {
			ClassNum string `json:"ClassNum"`
		}
		if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
			http.Error(w, "Invalid JSON body", http.StatusBadRequest)
			return
		}
		if requestData.ClassNum == "" {
			http.Error(w, "Missing ClassNum", http.StatusBadRequest)
			return
		}
		_, err := db.Exec("DELETE FROM SelectedClasses WHERE ClassNum = ?", requestData.ClassNum)
		if err != nil {
			http.Error(w, "Failed to delete class: "+err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "success"})
	})	

	// handler to get list of classes to dropdown when course is selected
	http.HandleFunc("/get-classes", func(w http.ResponseWriter, r *http.Request) {
		courseCode := r.URL.Query().Get("courseCode") // get selected CourseCode from query parameter
		
		if courseCode == "" {
			http.Error(w, "Missing courseCode parameter", http.StatusBadRequest)
			return
		}
	
		// queries for classes of specified code
		rows, err := db.Query("SELECT ClassNum, ClassCode FROM Classes WHERE ClassCode = ?", courseCode)
		if err != nil {
			http.Error(w, "Database query error: "+err.Error(), http.StatusInternalServerError)
			return
		}
		defer rows.Close()
	
		// makes list of classes with specified code
		var classes []Classes
		for rows.Next() {
			var class Classes
			if err := rows.Scan(&class.ClassNum, &class.ClassCode); err != nil {
				http.Error(w, "Database scan error: "+err.Error(), http.StatusInternalServerError)
				return
			}
			classes = append(classes, class)
		}
	
		// posts back to front end
		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(classes); err != nil {
			http.Error(w, "JSON encoding error: "+err.Error(), http.StatusInternalServerError)
		}

	})

	// create server
	log.Println("opening website on http://localhost:8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}