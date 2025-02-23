document.getElementById('processButton').addEventListener('click', () => {
  const inputText = document.getElementById('inputBox').value.trim();

  try {
    if (!inputText) {
      alert("Please enter a valid input.");  // Validation check
      return;
    }
    
    // Simulate processing the input (Replace with actual logic if needed)
    alert("Processing: " + inputText);

  } catch (error) {
    console.error("An error occurred:", error);  // Error logging
    alert("Something went wrong. Please try again.");
  }
});


// Placeholder JSON data for panel 'A'
const data_for_a = {
  "label_a": ["label_a/item1", "label_a/item2"],
  "label_b": ["label_b/item1"],
  "label_n": []  // Example label with no items
};

// Store checked items
const checkedItems = new Set();

/**
 * Function to create a hierarchical tree structure with tiles
 * @param {Object} data - The JSON object containing labels and items
 * @param {HTMLElement} parentElement - The parent element to append the tree structure
 */
function createTreeView(data, parentElement) {
  try {
      for (const [label, items] of Object.entries(data)) {
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
              items.forEach(item => {
                  let itemTile = document.createElement("div");
                  itemTile.classList.add("tile", "sub-tile");

                  // Create checkbox for each item
                  let itemCheckbox = document.createElement("input");
                  itemCheckbox.type = "checkbox";
                  itemCheckbox.addEventListener("change", () => toggleChecked(item, itemCheckbox.checked));

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
const data_for_b = {
  "category_x": ["category_x/item1", "category_x/item2"],
  "category_y": ["category_y/item1"],
  "category_z": []
};

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
document.addEventListener("DOMContentLoaded", () => {
  const treeViewElementB = document.getElementById("treeViewB");
  if (treeViewElementB) {
      createTreeViewB(data_for_b, treeViewElementB);
  }
});
