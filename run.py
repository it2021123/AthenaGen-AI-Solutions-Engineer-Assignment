# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 23:14:47 2025

@author: User
"""

# -*- coding: utf-8 -*-
import subprocess
import sys
import webbrowser
import time
import requests

# Βασικά packages που χρειάζονται
required_packages = [
    "spacy", "sentence-transformers", "flask", "bs4", "numpy", "pandas", 
    "scikit-learn", "torch", "dill", "pickle-mixin", "rouge-score", 
    "gspread", "oauth2client", "transformers", "requests", "google-cloud-storage",
    "google-cloud-core","google-auth","google-auth-oauthlib","google-api-python-client"
]

# Εγκατάσταση πακέτων
for pkg in required_packages:
    subprocess.run([sys.executable, "-m", "pip", "install", pkg])

# Εγκατάσταση μοντέλου Hugging Face
subprocess.run([sys.executable, "-m", "pip", "install", "transformers[sentencepiece]"])
subprocess.run([sys.executable, "-c",
    "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; "
    "AutoTokenizer.from_pretrained('kriton/greek-text-summarization'); "
    "AutoModelForSeq2SeqLM.from_pretrained('kriton/greek-text-summarization')"
])

# Τρέξιμο Flask app σε background
process = subprocess.Popen([sys.executable, "app.py"])

# Περίμενε να ξεκινήσει ο server
flask_url = "http://127.0.0.1:5000/"
timeout = 30  # δευτερόλεπτα
start_time = time.time()
while True:
    try:
        r = requests.get(flask_url)
        if r.status_code == 200:
            print("[INFO] Flask server is up!")
            break
    except requests.exceptions.ConnectionError:
        pass
    time.sleep(0.5)
    if time.time() - start_time > timeout:
        print("[ERROR] Flask server did not start in time!")
        process.terminate()
        sys.exit(1)

# Άνοιγμα browser
webbrowser.open(flask_url)

# Η διεύθυνση του Google Sheet (προαιρετικά)
google_sheet_url = "https://docs.google.com/spreadsheets/d/1Qu2jIx439K05kgPM_aNHAxwg_wtiDp3_Db_OWhXJN-0/edit?usp=sharing"
webbrowser.open_new_tab(google_sheet_url)

# Περιμένει να τερματιστεί ο Flask server
process.wait()
