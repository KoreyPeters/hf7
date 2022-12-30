window.onload = function (event) {
    document.querySelectorAll(".timestamp").forEach(stamp => {
        stamp.textContent = new Date(stamp.textContent).toString();
    })
}