async function fetchProducts() {
    const response = await fetch("http://127.0.0.1:8000/items");
    const data = await response.json();
    const container = document.getElementById("products");
    container.innerHTML = "";
    data.forEach(product => {
        const div = document.createElement("div");
        div.className = "product";
        div.innerHTML = `<h3>${product.name}</h3><p>Cena: ${product.price} PLN</p>`;
        container.appendChild(div);
    });
}

async function addProduct() {
    const name = prompt("Podaj nazwe produktu:");
    const price = prompt("Podaj cene produktu:");
    if (!name || !price) return;
    await fetch("http://127.0.0.1:8000/items", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `name=${name}&price=${price}`
    });
    fetchProducts();
}

function searchProducts() {
    const query = document.getElementById("search").value.toLowerCase();
    const products = document.querySelectorAll(".product");
    products.forEach(product => {
        const name = product.querySelector("h3").textContent.toLowerCase();
        product.style.display = name.includes(query) ? "block" : "none";
    });
}

document.addEventListener("DOMContentLoaded", fetchProducts);
