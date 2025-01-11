document.addEventListener('DOMContentLoaded', () => {
    console.log('JavaScript is loaded and working!');
});

function fetchClasses() {
    alert("hello");
    /*const courseCode = document.getElementById('courses').value;

    if (courseCode) {
        // Make an AJAX request to fetch the classes based on selected courseCode
        fetch(`/get-classes?courseCode=${courseCode}`)
            .then(response => response.json())
            .then(data => {
                const classSelect = document.getElementById('classes');
                classSelect.innerHTML = '<option value="">Select a class</option>'; // Reset the options

                data.forEach(classInfo => {
                    const option = document.createElement('option');
                    option.value = classInfo.CourseCode;
                    option.textContent = classInfo.CourseNum;
                    classSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching classes:', error));
    }*/
}