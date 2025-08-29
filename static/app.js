const COLUMNS = ['Type','Source','Date','Client_Name','Email','Phone','Company',
           'Service_Interest','Amount','VAT','Total_Amount','Invoice_Number','Priority','Message'];

let data = [];
let sortColumn = null;
let sortAsc = true;

// ------------------------ DOM Ready ------------------------
document.addEventListener("DOMContentLoaded", () => {
    initForm();
    loadData();
    loadEmailList();
    loadFormList();
    setInterval(loadData, 20000); // reload every 20s

    document.getElementById("searchInput").addEventListener("input", () => renderTable(filterData()));
    document.getElementById("recordFilter").addEventListener("change", () => renderTable(filterData()));

    document.getElementById("add-form").addEventListener("submit", addNewRow);
});

// ------------------------ Initialize Form ------------------------
function initForm() {
    const formFields = document.getElementById("form-fields");
    formFields.innerHTML = "";
    COLUMNS.forEach(col => {
        const input = document.createElement("input");
        input.name = col;
        input.placeholder = col;
        input.style.marginBottom = "5px";
        input.style.width = "100%";
        formFields.appendChild(input);
    });
}

// ------------------------ Load Data ------------------------
async function loadData() {
    try {
        const res = await fetch("/data");
        data = await res.json();
        renderTable(filterData());
    } catch (err) {
        console.error("Error loading data:", err);
    }
}

// ------------------------ Render Table ------------------------
function renderTable(rows) {
    const tableHeaders = document.getElementById("table-headers");
    const tableBody = document.getElementById("table-body");

    if (!tableHeaders || !tableBody) return;

    tableHeaders.innerHTML = "";
    tableBody.innerHTML = "";

    if (!rows.length) {
        tableHeaders.innerHTML = "<th>Δεν υπάρχουν δεδομένα</th>";
        return;
    }

    // Δημιουργία κεφαλίδων
    COLUMNS.forEach(h => {
        const th = document.createElement("th");
        th.textContent = h;
        th.onclick = () => { sortTable(h); };
        if (sortColumn === h) th.className = sortAsc ? 'sort-asc' : 'sort-desc';
        tableHeaders.appendChild(th);
    });

    const thActions = document.createElement("th");
    thActions.textContent = "Ενέργειες";
    tableHeaders.appendChild(thActions);

    // Δημιουργία γραμμών
    rows.forEach(row => {
        const tr = document.createElement("tr");

        COLUMNS.forEach(h => {
            const td = document.createElement("td");
            td.textContent = row[h] || "";
            tr.appendChild(td);
        });

        const tdActions = document.createElement("td");

        // Διαγραφή
        const btnDel = document.createElement("button");
        btnDel.textContent = "Διαγραφή";
        btnDel.onclick = async () => {
            if (!await showConfirm("Να διαγραφεί η γραμμή;", "delete")) return;
            const res = await fetch(`/delete_by_source/${encodeURIComponent(row.Source)}`, { method: "DELETE" });
            const result = await res.json();
            if (result.status === "ok") loadData();
        };
        tdActions.appendChild(btnDel);

        // PDF
        const btnPdf = document.createElement("button");
        btnPdf.textContent = "PDF";
        btnPdf.style.marginLeft = "5px";
        btnPdf.style.backgroundColor = "green";
        btnPdf.style.color = "white";
        btnPdf.onclick = () => {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            let y = 10;
            COLUMNS.forEach(key => {
                const value = row[key] || "";
                doc.text(`${key}: ${value}`, 10, y);
                y += 10;
            });
            doc.save(`Εγγραφή_${row.Source || Date.now()}.pdf`);
        };
        tdActions.appendChild(btnPdf);

        tr.appendChild(tdActions);
        tableBody.appendChild(tr);
    });
}

// ------------------------ Filter Data ------------------------
function filterData() {
    const query = document.getElementById("searchInput").value.toLowerCase();
    const recordFilter = document.getElementById("recordFilter").value;

    return data.filter(row => {
        const matchesSearch = Object.values(row).some(val => (val+"").toLowerCase().includes(query));
        let matchesFilter = true;
        if (recordFilter === "invoices") matchesFilter = row["Invoice_Number"] && row["Invoice_Number"].toString().trim() !== "nan";
        if (recordFilter === "emails") matchesFilter = !row["Invoice_Number"] || row["Invoice_Number"].toString().trim() === "nan";
        return matchesSearch && matchesFilter;
    });
}

// ------------------------ Sort Table ------------------------
function sortTable(column) {
    if (sortColumn === column) sortAsc = !sortAsc;
    else { sortColumn = column; sortAsc = true; }

    data.sort((a,b) => {
        const x = a[column] || "";
        const y = b[column] || "";
        if (x === y) return 0;
        return sortAsc ? (x > y ? 1 : -1) : (x < y ? 1 : -1);
    });

    renderTable(filterData());
}


async function addNewRow(e) {
    e.preventDefault();

    const confirm = await showConfirm("Να προστεθεί η νέα γραμμή;", "add");
    if (!confirm) return;

    const formData = {};
    [...e.target.elements].forEach(el => {
        if(el.name) formData[el.name] = el.value.trim();
    });

    // ---------------- Υποχρεωτικά πεδία ----------------
    const requiredFields = ["Type", "Source", "Date", "Client_Name"];
    const errors = [];

    requiredFields.forEach(field => {
        if (!formData[field]) {
            errors.push(`${field} είναι υποχρεωτικό.`);
        }
    });

    if (errors.length) {
        alert("Σφάλματα:\n" + errors.join("\n"));
        return;
    }

    // ---------------- Send to Server ----------------
    try {
        const res = await fetch("/add", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(formData)
        });
        const result = await res.json();
        if (result.status === "ok") {
            e.target.reset();
            loadData();
        } else {
            alert("Σφάλμα κατά την προσθήκη: " + result.message);
        }
    } catch (err) {
        console.error("Add row error:", err);
        alert("Σφάλμα κατά την προσθήκη!");
    }
}


// ------------------------ Confirm Modal ------------------------
async function showConfirm(message, type = "default") {
    return new Promise(resolve => {
        const modal = document.getElementById("custom-confirm");
        const msg = document.getElementById("confirm-message");
        const yesBtn = document.getElementById("confirm-yes");
        const noBtn = document.getElementById("confirm-no");

        let icon = "⚠️", color = "#3498db";
        if (type === "delete") { icon = "🗑️"; color = "#e74c3c"; }
        if (type === "add") { icon = "➕"; color = "#2ecc71"; }
        if (type === "extract") { icon = "📂"; color = "#f39c12"; }

        msg.innerHTML = `<span style="font-size:22px; color:${color}">${icon}</span><br><br>${message}`;
        modal.style.display = "flex";

        function cleanup() {
            yesBtn.removeEventListener("click", onYes);
            noBtn.removeEventListener("click", onNo);
            modal.style.display = "none";
        }

        function onYes() { cleanup(); resolve(true); }
        function onNo() { cleanup(); resolve(false); }

        yesBtn.addEventListener("click", onYes);
        noBtn.addEventListener("click", onNo);
    });
}


// ------------------------ Manual Edit Modal -----------------------
async function showEditModal(data) {
    return new Promise(resolve => {
        const modal = document.getElementById("custom-confirm1");
        const msg = document.getElementById("confirm-message1");
        const formDiv = document.getElementById("confirm-form1");
        const yesBtn = document.getElementById("confirm-yes1");
        const noBtn = document.getElementById("confirm-no1");

        msg.innerHTML = "<b>Manual Edit Mode:</b> Επεξεργαστείτε τα στοιχεία πριν αποθήκευση:";
        
        // Δημιουργούμε input για κάθε πεδίο
        formDiv.innerHTML = "";
        Object.entries(data).forEach(([key, value]) => {
            const label = document.createElement("label");
            label.textContent = key + ": ";
            const input = document.createElement("input");
            input.name = key;
            input.value = value ?? "";
            input.style.display = "block";
            input.style.marginBottom = "8px";
            label.appendChild(input);
            formDiv.appendChild(label);
        });

        modal.style.display = "flex";
	
        function cleanup() {
            yesBtn.removeEventListener("click", onYes);
            noBtn.removeEventListener("click", onNo);
            modal.style.display = "none";
        }

        function onYes() {
            const editedData = {};
            formDiv.querySelectorAll("input").forEach(input => {
                editedData[input.name] = input.value;
            });
            cleanup();
            resolve(editedData);  // Επιστρέφει τα edited data
        }

        function onNo() {
            cleanup();
            resolve(null); // Ακυρώνεται
        }

        yesBtn.addEventListener("click", onYes);
        noBtn.addEventListener("click", onNo);
    });
}

// ------------------------ Load Email List ------------------------
async function loadEmailList() {
    try {
        const res = await fetch("/list_emails");
        const files = await res.json();
        const list = document.getElementById("email-list");
        list.innerHTML = "";

        files.forEach(f => {
            const li = document.createElement("li");
            li.textContent = f + " ";

            // Κουμπί Extract με Manual Edit
            const btnExtract = document.createElement("button");
            btnExtract.textContent = "Extract";
            btnExtract.onclick = async () => {
                // 1. Φέρε τα δεδομένα του αρχείου
                const res = await fetch(`/get_file_data/${f}`);
                const data = await res.json();

                // 2. Άνοιξε το Manual Edit Modal
                const edited = await showEditModal(data);
                if (!edited) return; // Cancel

                // 3. Στείλε τα edited δεδομένα στον server
                const saveRes = await fetch("/save_file_data", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ filename: f, data: edited })
                });
                const saveResult = await saveRes.json();
                if (saveResult.status !== "ok") {
                    alert("Αποτυχία αποθήκευσης αλλαγών!");
                    return;
                }

                // 4. Κάνε το κανονικό extract
                if (!await showConfirm(`Είστε σίγουροι ότι θέλετε να κάνετε extract από το ${f};`, 'extract')) return;
                const r = await fetch(`/extract/${f}`, { method: "POST" });
                const result = await r.json();
                if (result.status === "ok") loadData();
            };
            li.appendChild(btnExtract);

            // Κουμπί Delete
            const btnDelete = document.createElement("button");
            btnDelete.textContent = "Delete";
            btnDelete.style.marginLeft = "10px";
            btnDelete.onclick = async () => {
                if (!await showConfirm(`Είστε σίγουροι ότι θέλετε να διαγράψετε το ${f};`, 'delete')) return;
                const r = await fetch(`/delete_file/${f}`, { method: "DELETE" });
                const result = await r.json();
                alert(result.message);
                if (result.status === "ok") loadEmailList(); // ανανέωση λίστας
            };
            li.appendChild(btnDelete);

            list.appendChild(li);
        });
    } catch (err) { console.error(err); }
}

// ------------------------ Load Form List ------------------------
async function loadFormList() {
    try {
        const res = await fetch("/list_forms");
        const files = await res.json();
        const list = document.getElementById("form-list");
        list.innerHTML = "";

        files.forEach(f => {
            const li = document.createElement("li");
            li.textContent = f + " ";

            // Κουμπί Extract με Manual Edit
            const btnExtract = document.createElement("button");
            btnExtract.textContent = "Extract";
            btnExtract.onclick = async () => {
                const res = await fetch(`/get_file_data/${f}`);
                const data = await res.json();

                const edited = await showEditModal(data);
                if (!edited) return; // Cancel

                const saveRes = await fetch("/save_file_data", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ filename: f, data: edited })
                });
                const saveResult = await saveRes.json();
                if (saveResult.status !== "ok") {
                    alert("Αποτυχία αποθήκευσης αλλαγών!");
                    return;
                }

                if (!await showConfirm(`Είστε σίγουροι ότι θέλετε να κάνετε extract από το ${f};`, 'extract')) return;
                const r = await fetch(`/extract/${f}`, { method: "POST" });
                const result = await r.json();
                if (result.status === "ok") loadData();
            };
            li.appendChild(btnExtract);

            // Κουμπί Delete
            const btnDelete = document.createElement("button");
            btnDelete.textContent = "Delete";
            btnDelete.style.marginLeft = "10px";
            btnDelete.onclick = async () => {
                if (!await showConfirm(`Είστε σίγουροι ότι θέλετε να διαγράψετε το ${f};`, 'delete')) return;
                const r = await fetch(`/delete_file/${f}`, { method: "DELETE" });
                const result = await r.json();
                alert(result.message);
                if (result.status === "ok") loadFormList(); // ανανέωση λίστας
            };
            li.appendChild(btnDelete);

            list.appendChild(li);
        });
    } catch (err) { console.error(err); }
}
