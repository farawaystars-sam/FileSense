document.addEventListener('DOMContentLoaded', () => {
    const middlePanel = document.getElementById('middle-panel');
    const rightPanel = document.getElementById('right-panel');
    const detailsArea = document.getElementById('details-area');

    fetchTreeData().then(treeData => {
        if (treeData) {
            createTabs(treeData, middlePanel);
        }
    });

    middlePanel.addEventListener('click', (event) => {
        const listItem = event.target.closest('li');
        if (listItem) {
            const details = listItem.dataset.details;
            detailsArea.textContent = details;
        }
    });
});