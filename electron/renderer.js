// For reading the version num for the footer section
// var remote = require('remote'); // Load remote compnent that contains the dialog dependency
// var dialog = remote.require('dialog'); // Load the dialogs component of the OS
// var fs = require('fs'); // Load the File System to execute our common tasks (CRUD)

// Request project version from main process
// ipcRenderer.send("get-app-version");

// Receive and display the project version
// ipcRenderer.on("app-version", (event, version) => {
//     document.getElementById("projectVersion").textContent = `Version: ${version}`;
// });

const browseButton = document.getElementById('btn');
const filePathElement = document.getElementById('inputBox');

document.addEventListener("DOMContentLoaded", async() => {
    browseButton.addEventListener('click', async () => {
        const filePath = await window.electronAPI.openFile();
        filePathElement.value = filePath;    
    
        // display the initial file structure.
        const inputBox = document.getElementById("inputBox").value.trim();
        console.log("🔄 Sending input to backend for init struct:", inputBox);

        const response = await fetch("http://127.0.0.1:5000/browse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input_path: inputBox }),
        });

        // refresing panels a 
        data_for_a = await response.json();
        console.log("recived initial file structure {}", data_for_a);
        const treeViewElement = document.getElementById("treeView");
    
        if (treeViewElement) {
            createTreeView(data_for_a, treeViewElement);
        }   
    });
});
    


document.addEventListener("DOMContentLoaded", async() => {
    const treeViewElement = document.getElementById("treeView");
    const file_path = document.getElementById("inputBox").value;
    
    if (treeViewElement) {
        createTreeView(data_for_a, treeViewElement);
    }
});

const processButton = document.getElementById("processButton");
// processButton.addEventListener('click', () => {
//     const path = document.getElementById('inputBox').value;

//     window.electronAPI.processPath(path).then((result) => {
//       console.log('Result from main process:', result);
//     //   alert('Processed result: ' + result);
//     });
//   });

let result = {};

document.addEventListener("DOMContentLoaded", () => {
  const processButton = document.getElementById("processButton");
  
  if (processButton) {
      processButton.addEventListener("click", async () => {
          try {
              const inputBox = document.getElementById("inputBox").value.trim();
              if (!inputBox) {
                  alert("Please enter a valid input before processing.");
                  return;
              }

              console.log("🔄 Sending input to backend:", inputBox);

              const response = await fetch("http://127.0.0.1:5000/process", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ user_input: inputBox }),
              });

            result = await response.json();
            data_for_b = result;
            const treeViewElementB = document.getElementById("treeViewB");
                if (treeViewElementB) {
                    createTreeViewB(data_for_b, treeViewElementB);
                    console.log("✅ Response in createview:", data_for_b);
                }
              
              console.log("✅ Response from backend:", data_for_b);
            //   alert("Received from backend: " + result.response);

          } catch (error) {
              console.error("❌ Error communicating with backend:", error);
              alert("Error processing input. Please check the backend server.");
          }
      });
  }
});



// // Placeholder JSON data for panel 'A'
// var data_for_a = {
//   "label_a": ["label_a/item1", "label_a/item2"],
//   "label_b": ["label_b/item1"],
//   "label_n": []  // Example label with no items
// };

var data_for_a = {};
// Store checked items
const checkedItems = new Set();

/**
 * Function to create a hierarchical tree structure with tiles
 * @param {Object} data - The JSON object containing labels and items
 * @param {HTMLElement} parentElement - The parent element to append the tree structure
 */
// function createTreeView(data, parentElement) {
//   try {
//       for (const [label, items] of Object.entries(data)) {
//           let labelTile = document.createElement("div");
//           labelTile.classList.add("tile");

//           // Create checkbox for the label
//           let labelCheckbox = document.createElement("input");
//           labelCheckbox.type = "checkbox";
//           labelCheckbox.addEventListener("change", () => toggleChecked(label, labelCheckbox.checked));

//           let labelText = document.createElement("span");
//           labelText.textContent = label;

//           labelTile.appendChild(labelCheckbox);
//           labelTile.appendChild(labelText);
//           parentElement.appendChild(labelTile);

//           if (items.length > 0) {
//               let subList = document.createElement("div");
//               items.forEach(item => {
//                   let itemTile = document.createElement("div");
//                   itemTile.classList.add("tile", "sub-tile");

//                   // Create checkbox for each item
//                   let itemCheckbox = document.createElement("input");
//                   itemCheckbox.type = "checkbox";
//                   itemCheckbox.addEventListener("change", () => toggleChecked(item, itemCheckbox.checked));

//                   let itemText = document.createElement("span");
//                   itemText.textContent = item.split("/")[1];  // Display only item name

//                   itemTile.appendChild(itemCheckbox);
//                   itemTile.appendChild(itemText);
//                   subList.appendChild(itemTile);
//               });
//               parentElement.appendChild(subList);
//           }
//       }
//   } catch (error) {
//       console.error("Error generating tree view:", error);
//       alert("An error occurred while loading the data.");
//   }
// }

function createTreeView(data, parentElement) {
    try {
        for (const [label, items] of Object.entries(data)) {
            if (label === ".") {
                items.forEach(item => {
                    let itemTile = document.createElement("div");
                    itemTile.classList.add("tile", "sub-tile");

                    let itemCheckbox = document.createElement("input");
                    itemCheckbox.type = "checkbox";
                    itemCheckbox.addEventListener("change", () => toggleChecked(item, itemCheckbox.checked));

                    let itemText = document.createElement("span");
                    itemText.textContent = item.split("/").pop();  // Display only item name

                    itemTile.appendChild(itemCheckbox);
                    itemTile.appendChild(itemText);
                    parentElement.appendChild(itemTile);
                });
            } else {
                let labelTile = document.createElement("div");
                labelTile.classList.add("tile");

                // Create checkbox for the label
                let labelCheckbox = document.createElement("input");
                labelCheckbox.type = "checkbox";
                labelCheckbox.addEventListener("change", () => toggleChecked(label, labelCheckbox.checked));

                let labelText = document.createElement("span");
                labelText.textContent = label;

                labelTile.appendChild(labelCheckbox);
                labelTile.appendChild(labelText);
                parentElement.appendChild(labelTile);

                if (items.length > 0) {
                    let subList = document.createElement("div");
                    subList.classList.add("sub-tile-list");

                    items.forEach(item => {
                        let itemTile = document.createElement("div");
                        itemTile.classList.add("tile", "sub-tile");

                        // Create checkbox for each item
                        let itemCheckbox = document.createElement("input");
                        itemCheckbox.type = "checkbox";
                        itemCheckbox.addEventListener("change", () => toggleChecked(item, itemCheckbox.checked));

                        let itemText = document.createElement("span");
                        itemText.textContent = item.split("/").pop();  // Display only item name

                        itemTile.appendChild(itemCheckbox);
                        itemTile.appendChild(itemText);
                        subList.appendChild(itemTile);
                    });
                    parentElement.appendChild(subList);
                }
            }
        }
    } catch (error) {
        console.error("Error generating tree view:", error);
        alert("An error occurred while loading the data.");
    }
}



/**
 * Function to track checked items and print to console
 * @param {string} item - The name of the item being checked/unchecked
 * @param {boolean} isChecked - Whether the checkbox is checked or not
 */
function toggleChecked(item, isChecked) {
    if (isChecked) {
        checkedItems.add(item);
    } else {
        checkedItems.delete(item);
    }
    console.log("Checked items:", Array.from(checkedItems));
}

// Initialize the tree in Panel A
document.addEventListener("DOMContentLoaded", () => {
    const treeViewElement = document.getElementById("treeView");
    if (treeViewElement) {
        createTreeView(data_for_a, treeViewElement);
    }
});

// Placeholder JSON data for Panel B
var data_for_b = {};
// Store checked items separately for Panel B
const checkedItemsB = new Set();

/**
* Function to create a hierarchical tree structure with tiles (for Panel B)
* @param {Object} data - The JSON object containing categories and items
* @param {HTMLElement} parentElement - The parent element to append the tree structure
*/
function createTreeViewB(data, parentElement) {
  try {
      for (const [category, items] of Object.entries(data)) {
          let categoryTile = document.createElement("div");
          categoryTile.classList.add("tile");

          // Create checkbox for the category
          let categoryCheckbox = document.createElement("input");
          categoryCheckbox.type = "checkbox";
          categoryCheckbox.addEventListener("change", () => toggleCheckedB(category, categoryCheckbox.checked));

          let categoryText = document.createElement("span");
          categoryText.textContent = category;

          categoryTile.appendChild(categoryCheckbox);
          categoryTile.appendChild(categoryText);
          parentElement.appendChild(categoryTile);

          if (items.length > 0) {
              let subList = document.createElement("div");
              items.forEach(item => {
                  let itemTile = document.createElement("div");
                  itemTile.classList.add("tile", "sub-tile");

                  // Create checkbox for each item
                  let itemCheckbox = document.createElement("input");
                  itemCheckbox.type = "checkbox";
                  itemCheckbox.addEventListener("change", () => toggleCheckedB(item, itemCheckbox.checked));

                  let itemText = document.createElement("span");
                  itemText.textContent = item.split("/")[1];  // Display only item name

                  itemTile.appendChild(itemCheckbox);
                  itemTile.appendChild(itemText);
                  subList.appendChild(itemTile);
              });
              parentElement.appendChild(subList);
          }

      }
  } catch (error) {
      console.error("Error generating tree view for Panel B:", error);
      alert("An error occurred while loading the data for Panel B.");
  }
}

function addPanelFooter(parentElement) {
    // Create the panel-b-footer div
    let panelFooter = document.createElement("div");
    panelFooter.classList.add("panel-b-footer");

    // Create the Accept button
    let acceptBtn = document.createElement("button");
    acceptBtn.id = "acceptBtn";
    acceptBtn.textContent = "Accept";

    // Create the Reject button
    let rejectBtn = document.createElement("button");
    rejectBtn.id = "rejectBtn";
    rejectBtn.textContent = "Reject";

    // Append buttons to the panel-b-footer div
    panelFooter.appendChild(acceptBtn);
    panelFooter.appendChild(rejectBtn);

    // Append the panel-b-footer div to the parent element
    parentElement.appendChild(panelFooter);
}


/**
* Function to track checked items in Panel B and print to console
* @param {string} item - The name of the item being checked/unchecked
* @param {boolean} isChecked - Whether the checkbox is checked or not
*/
function toggleCheckedB(item, isChecked) {
  if (isChecked) {
      checkedItemsB.add(item);
  } else {
      checkedItemsB.delete(item);
  }
  console.log("Checked items in Panel B:", Array.from(checkedItemsB));
}

// Initialize the tree in Panel B


// Function to handle "Accept" button click
async function onAcceptClick() {
  try {
      console.log("✅ Accept button clicked.");
    //   alert("Action Accepted!");
      // TODO: Add logic for processing accepted items
      console.log("making changes:");
      const status = await fetch("http://127.0.0.1:5000/accept-changes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ structure: data_for_b }),
      });
      console.log("Status:", await status.json)
  } catch (error) {
      console.error("Error handling Accept button:", error);
      alert("An error occurred while processing Accept.");
  }
}

// Function to handle "Reject" button click
function onRejectClick() {
  try {
      console.log("❌ Reject button clicked.");
      alert("Action Rejected!");
      // TODO: Add logic for handling rejection
  } catch (error) {
      console.error("Error handling Reject button:", error);
      alert("An error occurred while processing Reject.");
  }
}

// Attach event listeners when DOM loads
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("acceptBtn").addEventListener("click", onAcceptClick);
  document.getElementById("rejectBtn").addEventListener("click", onRejectClick);
});


