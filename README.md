# Athengen AI Interface

**Έκδοση:** 1.0  
**Ημερομηνία:** 28/08/2025  
**Συντάκτης:** Πουλημένος Γεώργιος

## 🧠 Περιγραφή Συστήματος

Το **Athengen AI Interface** είναι μια web εφαρμογή βασισμένη σε Flask που επιτρέπει την ανάγνωση και επεξεργασία email και HTML forms (.eml/.html αρχεία). Η εφαρμογή:

- Εξάγει βασικά δεδομένα (Subject, From, To, Body)
- Επιτρέπει χειροκίνητη επεξεργασία μέσω browser
- Αποθηκεύει δεδομένα σε Google Sheets
- Χρησιμοποιεί το μοντέλο `kriton/greek-text-summarization` για σύνοψη κειμένων
- Λειτουργεί τοπικά με browser-based UI

---

## 🛠️ Τεχνολογίες

| Κατηγορία       | Τεχνολογία                     | Περιγραφή                                 |
|----------------|-------------------------------|-------------------------------------------|
| Γλώσσα          | Python 3.11.9                  | Backend ανάπτυξη                          |
| Γλώσσα          | HTML / CSS                     | Frontend ανάπτυξη                         |
| Γλώσσα          | Javascript                     | Frontend / Request-Fetch                  |
| Framework       | Flask                          | Web server & API                          |
| NLP             | Hugging Face Transformers      | Summarization μοντέλο                     |
| NLP Utils       | spacy, sentence-transformers   | Tokenization & embeddings                 |
| Δεδομένα        | numpy, pandas, scikit-learn    | Data handling                             |
| Storage         | gspread, oauth2client          | Σύνδεση με Google Sheets                  |
| Cloud API       | Google Cloud API               | Sheets & Drive μέσω service account       |
| Utilities       | dill, pickle-mixin, requests, bs4 | Βοηθητικές λειτουργίες                 |
| Metrics         | rouge-score                    | Αξιολόγηση NLP outputs                    |

---

## ⚙️ Εγκατάσταση

### Windows

```bash
# Κατέβασε το GitHub repo
# Unzip το αρχείο athengen_ai/
# Άνοιξε τον φάκελο athengen_ai/
# Δεξί κλικ στο αρχείο run_flask_app.bat
```

### Linux
```bash
# Κατέβασε το GitHub repo
# Unzip το αρχείο athengen_ai/
# Άνοιξε τον φάκελο athengen_ai/
# chmod +x run_flask_app.sh
# ./run_flask_app.sh
```

```bash
###Εναλλακτικά (Cross-platform)
# Κατέβασε το GitHub repo
# Unzip το αρχείο athengen_ai/
# Άνοιξε τον φάκελο athengen_ai/
# pip install request
# python run.py
```

📁 Δομή Αρχείων
```bash
athengen_ai/
├── config.py
├── app.py
├── templates/
├── emails/
├── routes/
│   └── routes.py
├── static/
│   ├── style.css
│   └── app.js
├── services/
│   ├── data_services.py
│   ├── extractor.py
│   └── form_extractor.py
├── auto_testing.py
├── credential.json // Σας το εχώ προωθησεί μέσω email
├── priority_classifier.py
├── priority_model.pk
├── run_flask.sh
├── run_flask.bat
├── Ανάλυση Αναγκών-Τεχνική Πρόταση.pdf
├── Technical Documentation.pdf
├── User Manual.pdf
└── README.md
```


## 🔌 API Endpoints

| Endpoint                      | Description                     |
|------------------------------|---------------------------------|
| `/`                          | Home                            |
| `/data`                      | View extracted data             |
| `/add`                       | Add new entry                   |
| `/delete_by_source/`         | Delete entries by source        |
| `/delete_by_source/<source>` | Delete entries from source      |
| `/extract/<filename>`        | Extract data from file          |
| `/list_emails`               | List available email files      |
| `/list_forms`                | List available form files       |
| `/delete_file/<filename>`    | Delete file                     |
| `/get_file_data/<filename>`  | Retrieve file data              |
| `/save_file_data`            | Save edited data                |


📌 Σημειώσεις
- Βεβαιώσου ότι έχεις δημιουργήσει και ρυθμίσει το credential.json για πρόσβαση στο Google Cloud API.
- Το μοντέλο σύνοψης απαιτεί σύνδεση με Hugging Face και internet για αρχική φόρτωση.
