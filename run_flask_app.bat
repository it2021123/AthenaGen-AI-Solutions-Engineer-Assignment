@echo off
REM ------------------ Εγκατάσταση Packages ------------------
pip install spacy sentence-transformers flask bs4 numpy pandas scikit-learn torch dill pickle-mixin rouge-score gspread oauth2client transformers requests google-cloud-storage google-cloud-core google-auth google-auth-oauthlib google-api-python-client

REM ------------------ Εγκατάσταση μοντέλου Hugging Face ------------------
python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('kriton/greek-text-summarization'); AutoModelForSeq2SeqLM.from_pretrained('kriton/greek-text-summarization')"

REM ------------------ Τρέξιμο Flask app σε νέο παράθυρο (μένει ανοιχτό) ------------------
start "Flask Server" cmd /k "python app.py"

REM ------------------ Περίμενε 3 δευτ. για να ξεκινήσει ο server ------------------
timeout /t 3 /nobreak >nul

REM ------------------ Άνοιγμα browser στο Flask app ------------------
start http://127.0.0.1:5000/

REM ------------------ Άνοιγμα Google Sheet ------------------
start https://docs.google.com/spreadsheets/d/1Qu2jIx439K05kgPM_aNHAxwg_wtiDp3_Db_OWhXJN-0/edit?usp=sharing
