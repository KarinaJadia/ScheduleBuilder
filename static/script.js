function fetchClasses() { // updates classes based on selected course
    const courseCode = document.getElementById('courses').value; // gets course code eg ACCT
    if (courseCode) {
        // fetch the classes based on selected courseCode
        fetch(`/get-classes?courseCode=${courseCode}`)
            .then(response => response.json())
            .then(data => {
                const classSelect = document.getElementById('classes');
                classSelect.innerHTML = ''; // clear existing options

                const placeholderOption = document.createElement('option');
                placeholderOption.value = '';
                placeholderOption.textContent = 'please select';
                placeholderOption.disabled = true;
                placeholderOption.selected = true;
                classSelect.appendChild(placeholderOption);

                // populate new options
                data.forEach(classInfo => {
                    const option = document.createElement('option');
                    option.value = classInfo.ClassNum;
                    option.textContent = classInfo.ClassNum;
                    classSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching classes:', error));
    }
}

function addClass() {
    const selectedClassNum = document.getElementById('classes').value;
    // alert(selectedClassNum)
    if (selectedClassNum) {
        const existingRow = document.querySelector(`#row-${selectedClassNum}`);
        if (existingRow) {
            alert('class already added');
            return;
        }

        fetch('/add-class', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ClassNum: selectedClassNum }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to add class');
            }
            return response.json();
        })
        .then(data => {
            console.log('class added:', data);
            // dynamically update the table to show the new class
            const tableBody = document.querySelector('#selected-classes-table tbody');
            const newRow = document.createElement('tr');
            newRow.id = `row-${data.ClassNum}`;
            newRow.innerHTML = `
                <td>${data.ClassNum}</td>
                <td>
                    <button id="${data.ClassNum}" value="${data.ClassNum}" onclick="deleteClass('${data.ClassNum}')">delete</button>
                </td>
            `;
            tableBody.appendChild(newRow);
        })
        .catch(error => console.error('Error:', error));
    }
}

function deleteClass(classNum) {
    alert("class deleted")
    fetch(`/delete-class`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ClassNum: classNum }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('failed to delete class');
            }
            return response.json();
        })
        .then(data => {
            console.log('class deleted:', data);

            // remove the row from the table
            const row = document.getElementById(`row-${classNum}`);
            if (row) {
                row.remove();
            }
        })
        .catch(error => {
            console.error('error deleting class:', error);
        });
}