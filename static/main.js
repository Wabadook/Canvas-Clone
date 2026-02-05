function say_hi(elt) {
    console.log("Welcome to", elt.innerText);
}

function make_table_sortable(table) {
    //Check if the table has class attribute 'sortable'.
    //If yes then make it sortable; else, return.
    if (!table.classList.contains('sortable')) {
        return;
    }
    
    //Table's header.
    const thead = table.querySelector('thead');
    //Table's body.
    const tbody = table.querySelector('tbody');
    //Profile page Grade cell or Assignment Due Date Cell should be (0,1) since table has multiple row and 2 - 3 columns.
    const targetCell = thead.rows[0].cells[1];
    //Index page Weight cell should be (0,2 since table has multiple row and 3 columns).
    const targetCellWeight = thead.rows[0].cells[2];
    //Rows of tbody
    const rows = Array.from(tbody.rows);
    //Used to determine if the table is ascending or descending.
    let ascending = true;

    let state1 = false;
    let state2 = false;

    let index = 0;
    //Set data-index attributes to all tr elements in the table.
    rows.forEach(row => {
        row.setAttribute('data-index', index);
        index++;
    });

    //Handle changing classes of the header's final cell.
    targetCell.addEventListener('click', () => {
        state1 = true;

        if (state2 == true){
            sortByIndex(rows, tbody);
            state2 = false;
        }

        const currentClasses = targetCell.className;

        //By default, remove all classes.
        targetCell.classList.remove('sort-asc', 'sort-desc');

        //If the table is already ascending, change the class to descending.
        if (currentClasses.includes('sort-asc')){
            targetCell.classList.add('sort-desc');
            console.log('Descendingly Sorted.');
            ascending = false;
        }         
        //If the table is already descending, change the class to unsorted.
        else if (currentClasses.includes('sort-desc')) {
            targetCell.classList.remove('sort-asc', 'sort-desc');
            console.log('Unsorted.');
        } 
        //If the table is unsorted, change the class to ascending.
        else {
            targetCell.classList.add('sort-asc');
            console.log('Ascendingly Sorted.');
            ascending = true;
        }

        //Sort the list in ascending or descending order.
        if (targetCell.className.includes('sort-asc') || targetCell.className.includes('sort-desc')) {
            //Handle sorting table row of tbody.
            rows.sort((row1, row2) => {
                const cell1Text = row1.cells[1].textContent;
                const cell2Text = row2.cells[1].textContent;
                
                let val1;
                let val2;
                if (isNumber(cell1Text) && isNumber(cell2Text)) {
                    val1 = parseFloat(cell1Text);
                    val2 = parseFloat(cell2Text);
                } else {
                    val1 = convertToCorrectFormat(cell1Text);
                    val2 = convertToCorrectFormat(cell2Text);
                }    

                //Return negative if num1 comes before num2.
                //Return 0 if a equals b.
                //Return positive if num1 comes after num2.
                if (val1 === val2) {
                    return 0;
                } else {
                    if (ascending) {
                        return val1 - val2;
                    } else {
                        return val2 - val1;
                    }
                }
            });

            //Add the sorted row to the tbody of the table.
            rows.forEach(row => tbody.appendChild(row));
        //Sort the list in data-index order.
        } else {
            sortByIndex(rows,tbody);
        }
    });

    try {
        targetCellWeight.addEventListener('click', () => {
            state2 = true;
    
            if (state1 == true){
                sortByIndex(rows, tbody);
                state1 = false;
            }
    
            const currentClasses = targetCellWeight.className;
    
            //By default, remove all classes.
            targetCellWeight.classList.remove('sort-asc', 'sort-desc');
    
            //If the table is already ascending, change the class to descending.
            if (currentClasses.includes('sort-asc')){
                targetCellWeight.classList.add('sort-desc');
                console.log('Descendingly Sorted.');
                ascending = false;
            }         
            //If the table is already descending, change the class to unsorted.
            else if (currentClasses.includes('sort-desc')) {
                targetCellWeight.classList.remove('sort-asc', 'sort-desc');
                console.log('Unsorted.');
            } 
            //If the table is unsorted, change the class to ascending.
            else {
                targetCellWeight.classList.add('sort-asc');
                console.log('Ascendingly Sorted.');
                ascending = true;
            }
    
            //Sort the list in ascending or descending order.
            if (targetCellWeight.className.includes('sort-asc') || targetCellWeight.className.includes('sort-desc')) {
                //Handle sorting table row of tbody.
                rows.sort((row1, row2) => {
                    const cell1Text = row1.cells[2].textContent;
                    const cell2Text = row2.cells[2].textContent;
                    
                    let val1;
                    let val2;
                    if (isNumber(cell1Text) && isNumber(cell2Text)) {
                        val1 = parseFloat(cell1Text);
                        val2 = parseFloat(cell2Text);
                    } else {
                        val1 = convertToCorrectFormat(cell1Text);
                        val2 = convertToCorrectFormat(cell2Text);
                    }    
    
                    //Return negative if num1 comes before num2.
                    //Return 0 if a equals b.
                    //Return positive if num1 comes after num2.
                    if (val1 === val2) {
                        return 0;
                    } else {
                        if (ascending) {
                            return val1 - val2;
                        } else {
                            return val2 - val1;
                        }
                    }
                });
    
                //Add the sorted row to the tbody of the table.
                rows.forEach(row => tbody.appendChild(row));
            //Sort the list in data-index order.
            } else {
                sortByIndex(rows, tbody);
            }
        });
    } catch (error) {

    }
}

function make_form_async(form) {
    form.addEventListener('submit', async (event) => {
        try {
            //Prevent the form from submitting the default way.
            event.preventDefault();

            const oldMessage = form.querySelector('.status-message');
            if (oldMessage) {
                oldMessage.remove();
            }

            //Create a new formData through the sent in form and extract it's action URL.
            const formData = new FormData(form);
            const actionURL = form.action;

            //Build the response and send the data.
            const response = await fetch(actionURL, {
                method: "POST",
                body: formData
            });

            if(response.ok) {
                localStorage.setItem('uploadStatus', 'success');
            } else {
                localStorage.setItem('uploadStatus', 'failure');
            }

            location.reload();
        } catch (e) {
            console.error(e);
        }
    });
}

function make_grade_hypothesized(table) {
    //Check if the table has class attribute 'sortable'.
    //If yes then make it sortable; else, return.
    if (!table.classList.contains('hypothesizable')) {
        return;
    }

    //Formatting the look of the hypothesize button. 
    //Let the button be located to the right and separated from the action card.
    const buttonContainer = document.createElement('div');
    buttonContainer.style.display = "flex";
    buttonContainer.style.justifyContent = "flex-end";
    buttonContainer.style.marginTop = "1.5rem";

    let hypothesizeButton = document.createElement("button");
    hypothesizeButton.textContent = "Hypothesize";

    hypothesizeButton.addEventListener('click', () => {
        const cells = table.querySelectorAll('td.grade_weight');
    
        if (!table.classList.contains('hypothesized')){ 
            table.classList.add('hypothesized');

            hypothesizeButton.textContent = "Actual Grade";

            cells.forEach(cell => {
                const orginalText = cell.textContent.trim();

                if (orginalText === "Ungraded" || orginalText === "Not Due") {
                    //Create the input field and set the type to number.
                    const input = document.createElement("input");
                    input.classList.add('existing-input');
                    input.setAttribute('max', 100);
                    input.setAttribute('min', 0);
                    input.setAttribute('step', '1'); 
                    input.type = "number";
                    
                    //Save the old data as a new attribute, data-original.
                    cell.setAttribute('data-original', orginalText);
                    cell.textContent = "";
                    cell.appendChild(input);

                    input.addEventListener('keyup', () => {
                        let inputVal = parseFloat('input.value');

                        computeGrade(table);
                    })
                }
            });

            computeGrade(table);
        } else {
            computeGrade(table);

            hypothesizeButton.textContent = "Hypothesize";

            cells.forEach(cell => {
                if (cell.querySelector('input.existing-input')) {
                    const originalInput = cell.getAttribute('data-original') || "";
                    cell.textContent = originalInput;
                    cell.removeAttribute('data-original');
                }
            });

            table.classList.remove('hypothesized');
            computeGrade(table);
        }
    });
    
    buttonContainer.appendChild(hypothesizeButton);
    table.parentNode.insertBefore(buttonContainer, table);
}

function sortByIndex(rows, tbody) {
    rows.sort((row1, row2) => {
        const cell1Index = row1.getAttribute('data-index');
        const cell2Index = row2.getAttribute('data-index');

        //Return negative if num1 comes before num2.
        //Return 0 if a equals b.
        //Return positive if num1 comes after num2.
        if (cell1Index === cell2Index) {
            return 0;
        } else {
            return cell1Index - cell2Index;
        }
    });

    //Add the sorted row to the tbody of the table.
    rows.forEach(row => tbody.appendChild(row));
}

function isNumber(input) {
    const value = parseFloat(input);

    if (!isNaN(value)) {
        return true;
    } else {
        return false;
    }
} 

function convertToCorrectFormat(input) {
    let value = input.replace(/\./g, "");
    value = value.replace(/\bSept\b/g, "Sep");

    let date = new Date(value);

    return date.getTime();
}

function computeGrade(table) {
    const cells = document.querySelectorAll("td.grade_weight");
    let totalWeight = 0;
    let weightedSum = 0;

    let value = 0;

    cells.forEach(cell => {
        const weight = parseFloat(cell.dataset.weight);
        
        //Table has the 'hypothesized' class, calculate both the input and the already exisiting score.
        if(table.classList.contains('hypothesized')) {
            const test = cell.querySelector('input.existing-input');

            //console.log(test);

            if (cell.innerText !== "Missing" && cell.innerText !== "Not Due" && cell.innerText !== "") {
                value = parseFloat(cell.innerText);
            } else if (cell.innerText === "Missing") {
                value = 0;
            } else {
                value = parseFloat(test.value);
            }
        //Table doesn't have 'hypothesized' class, calculate just the already exisiting score.
        } else {
            const input = cell.textContent.trim();

            if (input === "Ungraded" || input === "Not Due") {
                return;
            } else if (input === "Missing") {
                value = 0;
            } else {
                value = parseFloat(input);
            }
        }

        if (!isNaN(value)) {
            weightedSum += value * weight;
            totalWeight += weight;
        }
    });

    if (totalWeight > 0) {
        const gradeCell = table.querySelector(".earned_score");
        const grade = Math.ceil(weightedSum/totalWeight * 100) / 100;
        gradeCell.innerHTML = `<strong>${grade}%</strong>`;
    } else {
        const gradeCell = table.querySelector(".earned_score");
        gradeCell.innerHTML = `<strong>0%</strong>`;
    }
}

say_hi(document.querySelector("h1"));

document.addEventListener('DOMContentLoaded', () => {
    const table = document.querySelector('table.sortable');
    if (table) {
        make_table_sortable(table);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form.async');
    if (form) {
        make_form_async(form);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const table = document.querySelector('table.hypothesizable');
    if (table) {
        make_grade_hypothesized(table);
    }
})

window.addEventListener('load', () => {
    const statusMessage = localStorage.getItem('uploadStatus');
    const form = document.querySelector("form.async");

    if (statusMessage && form) {
        const status = document.createElement('p');
        status.classList.add('status-message');

        if (statusMessage === 'success') {
            status.textContent = "Your file has been uploaded!";
        } else {
            status.textContent = "Your file failed to upload!";
        }

        form.appendChild(status);

        // Clear the status from localStorage after it's displayed
        localStorage.removeItem('uploadStatus');
    }
});