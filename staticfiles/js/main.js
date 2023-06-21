async function postForm() {

    console.log("Posting the form");
    const form = new FormData(document.getElementById("q_form"));

    const response = await fetch("/", {
        method: "POST",
        body: form,
    });

    const data = await response.text();

    if (response.ok) {
        let results = document.getElementById("results");
        document.getElementById("loader").classList.add("d-none");
        results.innerHTML = data;
    } else {
        throw new Error(data.error);
    }
}

document.getElementById("submit").addEventListener("click", (e) => {
    document.getElementById("loader").classList.remove("d-none");
    postForm();
});
