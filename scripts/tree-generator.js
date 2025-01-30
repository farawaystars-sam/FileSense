function generateTreeHTML(nodes) {
    let html = "<ul>";
    nodes.forEach(node => {
        const parts = node.split('/');
        const displayName = parts.length > 1 ? parts[1] : parts[0];
        const details = node;

        html += `<li data-details="${details}">${displayName}`;
        html += "</li>";
    });
    html += "</ul>";
    return html;
}

function createTabs(treeData, middlePanel) {
    middlePanel.innerHTML = "";

    const folders = Object.keys(treeData);

    folders.forEach((folder, index) => {
        const tabButton = document.createElement('button');
        tabButton.classList.add('tab-button');
        if (index === 0) tabButton.classList.add('active-tab');
        tabButton.textContent = folder;
        tabButton.dataset.tabId = folder;
        tabButton.addEventListener('click', () => {
            const allTabButtons = middlePanel.querySelectorAll('.tab-button');
            allTabButtons.forEach(btn => btn.classList.remove('active-tab'));
            tabButton.classList.add('active-tab');

            const allTabContent = middlePanel.querySelectorAll('.tab-content');
            allTabContent.forEach(content => content.classList.remove('active-tab-content'));
            const activeTabContent = middlePanel.querySelector(`#${folder}`);
            activeTabContent.classList.add('active-tab-content');

            const filesForFolder = Object.entries(treeData).filter(([key, value]) => key.startsWith(folder));
            const filePaths = filesForFolder.map(([key, value]) => value);
            displayTree(filePaths, activeTabContent);
        });
        middlePanel.appendChild(tabButton);

        const tabContent = document.createElement('div');
        tabContent.id = folder;
        tabContent.classList.add('tab-content');
        if (index === 0) tabContent.classList.add('active-tab-content');
        middlePanel.appendChild(tabContent);
    });
}

function displayTree(files, tabContent) {
    tabContent.innerHTML = generateTreeHTML(files);
}