async function fetchTreeData() {
    try {
        const response = await fetch('/get_tree_data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching tree data:", error);
        return null;
    }
}