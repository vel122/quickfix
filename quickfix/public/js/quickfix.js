frappe.ready(function () {
    if (frappe.boot.quickfix_shop_name) {
        const shopName = frappe.boot.quickfix_shop_name;

        // Add to navbar
        const navbar = document.querySelector(".navbar .container");
        if (navbar) {
            const el = document.createElement("span");
            el.style.marginLeft = "20px";
            el.style.fontWeight = "600";
            el.innerText = shopName;

            navbar.appendChild(el);
        }
    }
});