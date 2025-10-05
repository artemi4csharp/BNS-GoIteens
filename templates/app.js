// Згрузка наследствия

async function loadElement(file, selector, targetId) {
    const response = await fetch(file);
    const text = await response.text();

    const parser = new DOMParser();
    const doc = parser.parseFromString(text, 'text/html');

    const element = doc.querySelector(selector);
    if (element) {
        document.getElementById(targetId).appendChild(element);
    }
}

loadElement('base.html', 'header', 'header');
loadElement('base.html', 'footer', 'footer');

//Большая буква в инпут боксе

const inputs = document.querySelectorAll(".capitalize-first");

inputs.forEach(input => {
input.addEventListener("input", () => {
    let value = input.value;
    if (value.length > 0) {
    input.value = value.charAt(0).toUpperCase() + value.slice(1);
    }
});
});