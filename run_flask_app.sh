#!/bin/bash
# ------------------ Εγκατάσταση Packages ------------------
pip install --user spacy sentence-transformers flask bs4 numpy pandas scikit-learn torch dill pickle-mixin rouge-score gspread oauth2client transformers requests google-cloud-storage google-cloud-core google-auth google-auth-oauthlib google-api-python-client

# ------------------ Εγκατάσταση μοντέλου Hugging Face ------------------
python3 -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('kriton/greek-text-summarization'); AutoModelForSeq2SeqLM.from_pretrained('kriton/greek-text-summarization')"

# ------------------ Τρέξιμο Flask app σε νέο terminal (μένει ανοιχτό) ------------------
gnome-terminal -- bash -c "python3 app.py; exec bash"

# ------------------ Περίμενε 3 δευτ. για να ξεκινήσει ο server ------------------
sleep 3

# ------------------ Άνοιγμα browser στο Flask app ------------------
xdg-open "http://127.0.0.1:5000/"

# ------------------ Άνοιγμα Google Sheet ------------------
xdg-open "https://docs.google.com/spreadsheets/d/1Qu2jIx439K05kgPM_aNHAxwg_wtiDp3_Db_OWhXJN-0/edit?usp=sharing"
