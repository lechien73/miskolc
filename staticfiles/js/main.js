async function postForm() {

    console.log("Posting the form");
    const form = new FormData(document.getElementById("q_form"));

    const response = await fetch("/", {
        method: "POST",
        body: form,
    });

    const data = await response.json();

    if (response.ok) {
        let results = document.getElementById("results");
        document.getElementById("loader").classList.add("d-none");
        results.innerHTML = data.content;
        MathJax.typeset();

        if (data.mcq) {
            document.getElementById("csv_text").value = data.mcq;
            results.innerHTML += '<br /><button class="btn btn-info mt-3" id="download">Download CSV</button>';
            document.getElementById("download").addEventListener("click", (e) => {
                function dataUrl(data) { return "data:x-application/text," + escape(data); }
                window.open(dataUrl(document.getElementById("csv_text").value));
            });

        }

    } else {
        throw new Error(data.error);
    }
}

document.getElementById("submit").addEventListener("click", (e) => {
    document.getElementById("results").innerHTML = "";
    document.getElementById("loader").classList.remove("d-none");
    postForm();
});

document.getElementById("transfer").addEventListener("click", (e) => {
    document.getElementById("ScriptArea").value = document.getElementById("results").innerText;
});

document.getElementById("copyresults").addEventListener("click", (e) => {

    copyToClipboard(document.getElementById("results").innerText);

    alert("Copied to clipboard");
});

function copyToClipboard(str) {
    let el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style = { position: 'absolute', left: '-9999px' };
    document.body.appendChild(el);
    el.select();
    navigator.clipboard.writeText(el.value);
    document.body.removeChild(el);
}