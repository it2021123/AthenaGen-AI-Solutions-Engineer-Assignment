# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 11:01:21 2025

@author: User
"""

from flask import request, jsonify, render_template, send_file
import pandas as pd
import os
from services.data_service import read_google_sheet, update_google_sheet,clean_dataframe_for_gsheet,append_to_google_sheet,get_client
from services.form_extractor import HtmlExtractor
from services.extractor import EmailExtractor
from config import EMAIL_FOLDER, COLUMNS
import numpy as np

def register_routes(app, priority_model, generate_summary):
#-------------------Route για την αρχική σελίδα -------------------------------
    @app.route("/")
    def index():
        #print("[DEBUG] Accessed /")  # DEBUG: Έλεγχο πρόσβασης
        return render_template("index.html")

#-------------------Route για ανάκτηση δεδομένων από Google Sheet---------------
    @app.route("/data")
    def data():
        #print("[DEBUG] Accessed /data")
        df = read_google_sheet()  # Διαβάζουμε τα δεδομένα από το Google Sheet
        #print("[DEBUG] Read Google Sheet, rows:", len(df))

        if df.empty:  # Αν το dataframe είναι άδειο
            print("[DEBUG] DataFrame is empty")
            return jsonify([])

        # Μετατροπή της στήλης 'Date' σε datetime format
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Date'] = df['Date'].apply(
                lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(x) else ''
            )
            #print("[DEBUG] Converted Date column")

        # Ταξινόμηση κατά ημερομηνία, αντικατάσταση NaN με κενό string
        df = df.sort_values(by='Date', ascending=False)
        df = df.fillna('').astype(str)

       # print("[DEBUG] Returning JSON data")
        return jsonify(df.to_dict(orient="records"))  # Επιστρέφουμε JSON

#-------------------Route για προσθήκη νέας γραμμής στο Google Sheet---------------------------
    @app.route("/add", methods=["POST"])
    def add():
        #print("[DEBUG] Accessed /add")
        new_row = request.get_json()  # Λαμβάνουμε το JSON από τον client
        #print("[DEBUG] Received JSON:", new_row)
    
        if not new_row:  # Αν δεν υπάρχει JSON
            print("[DEBUG] No JSON received")
            return jsonify({"status": "error", "message": "No JSON received"}), 400
    
        df = read_google_sheet()  # Διαβάζουμε τα δεδομένα
        #print("[DEBUG] Read Google Sheet, rows:", len(df))
    
        # Καθαρισμός δεδομένων: αντικατάσταση None ή NaN με κενό string
        for k, v in new_row.items():
            if v is None or (isinstance(v, float) and (pd.isna(v) or np.isinf(v))):
                new_row[k] = ""
        #print("[DEBUG] Cleaned new row:", new_row)
    
        # Προσθήκη νέας γραμμής στο DataFrame και ενημέρωση Google Sheet
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df = clean_dataframe_for_gsheet(df)
        update_google_sheet(df)
        #print("[DEBUG] Updated Google Sheet")
    
        return jsonify({"status": "ok"})

#--------------Route για διαγραφή γραμμών με βάση την στήλη 'Source'-----------------------------
    @app.route("/delete_by_source/", defaults={"source": ""}, methods=["DELETE"])
    @app.route("/delete_by_source/<source>", methods=["DELETE"])
    def delete_by_source(source):
        #print(f"[DEBUG] Accessed /delete_by_source/{source}")
        df = read_google_sheet()
        #print("[DEBUG] Read Google Sheet, rows:", len(df))

        # Έλεγχος ύπαρξης στήλης 'Source'
        if 'Source' not in df.columns:
            print("[DEBUG] 'Source' column missing")
            return jsonify({"status": "error", "message": "'Source' column missing"}), 400

        df['Source'] = df['Source'].astype(str).str.strip().str.lower()
        
        if not source.strip():  # Διαγραφή κενών
            df = df[df['Source'] != ""].reset_index(drop=True)
        else:  # Διαγραφή συγκεκριμένου source
            df = df[~df['Source'].eq(source.strip().lower())].reset_index(drop=True)
        
        df = clean_dataframe_for_gsheet(df)
        update_google_sheet(df)
        #print("[DEBUG] Updated Google Sheet after delete")
        
        return jsonify({"status": "ok"})

#-----------------------Route για εξαγωγή δεδομένων από email ή HTML------------#
    @app.route("/extract/<filename>", methods=["POST"])
    def extract_file(filename):
        #print(f"[DEBUG] Accessed /extract/{filename}")
        file_path = os.path.join(EMAIL_FOLDER, filename)
        if not os.path.exists(file_path):
            print("[DEBUG] File not found:", file_path)
            return jsonify({"status": "file_not_found"}), 404
    
        df = read_google_sheet()
        if 'Source' in df.columns:
            df['Source'] = df['Source'].astype(str).str.strip().str.lower()
            if (df['Source'] == filename.strip().lower()).any():
                print("[DEBUG] File already extracted:", filename)
                return jsonify({"status": "already_extracted"})
    
        new_data = {}
        # Επιλογή κατάλληλου extractor
        if filename.lower().endswith(".eml"):
            extractor = EmailExtractor(
                email_folder=EMAIL_FOLDER,
                priority_model=priority_model,
                summarizer=generate_summary
            )
            new_data = extractor.process_single_email(file_path)
        elif filename.lower().endswith(".html"):
            extractor = HtmlExtractor(
                html_folder=EMAIL_FOLDER,
                priority_model=priority_model
            )
            new_data = extractor.process_single_form(file_path)
        else:
            print("[DEBUG] Unsupported file type")
            return jsonify({"status": "unsupported_file"}), 400
    
        #print("[DEBUG] Extracted data:", new_data)
        if new_data:
            # Καθαρισμός πεδίων
            for k, v in new_data.items():
                if v is None or (isinstance(v, float) and (pd.isna(v) or np.isinf(v))):
                    new_data[k] = ""
            new_data["Source"] = filename.strip()
    
            client = get_client()
            sheet = client.open("TechFlow Solution").sheet1
            row_data = [str(new_data.get(col, "")) for col in COLUMNS]
            sheet.append_row(row_data, value_input_option="USER_ENTERED")
            #print("[DEBUG] Appended row to Google Sheet")
    
            return jsonify({"status": "ok", "data": new_data})
        else:
            print("[DEBUG] No new data extracted")
            return jsonify({"status": "no_new_data"})

#------------------------ Route για λίστα email αρχείων ---------------------------
    @app.route("/list_emails")
    def list_emails():
        #print("[DEBUG] Accessed /list_emails")
        files = []
        if os.path.exists(EMAIL_FOLDER):
            files = [f for f in os.listdir(EMAIL_FOLDER) if f.endswith(".eml")]
        #print("[DEBUG] Email files:", files)
        return jsonify(files)

# ------------------------ Route για λίστα HTML αρχείων---------------------------
    @app.route("/list_forms")
    def list_forms():
        #print("[DEBUG] Accessed /list_forms")
        files = []
        if os.path.exists(EMAIL_FOLDER):
            files = [f for f in os.listdir(EMAIL_FOLDER) if f.endswith(".html")]
        #print("[DEBUG] HTML files:", files)
        return jsonify(files)

# ------------------------ Delete File από τοπικό Φακελό ------------------------
    @app.route("/delete_file/<filename>", methods=["DELETE"])
    def delete_file(filename):
        try:
            file_path = os.path.join(EMAIL_FOLDER, filename)
            #print(f"[DEBUG] Attempting to delete file: {file_path}")  # debug
    
            if os.path.exists(file_path):
                os.remove(file_path)
                #print(f"[DEBUG] File deleted successfully: {filename}")  # debug
                return jsonify({"status": "ok", "message": f"{filename} διαγράφηκε"})
            else:
                print(f"[DEBUG] File not found: {filename}")  # debug
                return jsonify({"status": "error", "message": "Το αρχείο δεν βρέθηκε"}), 404
        except Exception as e:
            print(f"[ERROR] Exception while deleting file {filename}: {e}")  # debug
            return jsonify({"status": "error", "message": str(e)}), 500


# ------------------------ Get File Data για Manual Edit ------------------------
    @app.route("/get_file_data/<filename>")
    def get_file_data(filename):
        try:
            file_path = os.path.join(EMAIL_FOLDER, filename)
            #print(f"[DEBUG] Fetching data for file: {file_path}")  # debug
    
            if not os.path.exists(file_path):
                print(f"[DEBUG] File does not exist: {filename}")
                return jsonify({"status": "file_not_found"}), 404
    
            # Προσπάθεια να φέρουμε τα υπάρχοντα δεδομένα από το Google Sheet
            df = read_google_sheet()
           # print(f"[DEBUG] Google Sheet loaded, rows: {len(df)}")  # debug
    
            if 'Source' in df.columns:
                df['Source'] = df['Source'].astype(str).str.strip().str.lower()
                row = df[df['Source'] == filename.strip().lower()]
                if not row.empty:
                    print(f"[DEBUG] Found existing data in sheet for {filename}")
                    return jsonify(row.iloc[0].to_dict())
    
            # Αν δεν υπάρχει ήδη στο sheet, κάνε ένα extract μόνο για preview
            if filename.lower().endswith(".eml"):
                extractor = EmailExtractor(email_folder=EMAIL_FOLDER, priority_model=priority_model)
                data = extractor.process_single_email(file_path)
            elif filename.lower().endswith(".html"):
                extractor = HtmlExtractor(html_folder=EMAIL_FOLDER, priority_model=priority_model)
                data = extractor.process_single_form(file_path)
            else:
                print(f"[DEBUG] Unsupported file type: {filename}")
                return jsonify({"status": "unsupported_file"}), 400
    
            #print(f"[DEBUG] Extracted preview data for {filename}: {data}")
            return jsonify(data or {})
        
        except Exception as e:
            print(f"[ERROR] Exception in get_file_data for {filename}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500


# ------------------------ Save File Data (για Manual Edit) ------------------------
    @app.route("/save_file_data", methods=["POST"])
    def save_file_data():
        try:
            payload = request.get_json()
            filename = payload.get("filename")
            data = payload.get("data")
            #print(f"[DEBUG] Saving data for file: {filename}, data: {data}")  # debug
    
            if not filename or not data:
                print("[DEBUG] Missing filename or data in request")
                return jsonify({"status": "error", "message": "Missing filename or data"}), 400
    
            df = read_google_sheet()
            #print(f"[DEBUG] Google Sheet loaded, rows before update: {len(df)}")
    
            # Αφαίρεσε παλιά εγγραφή για το συγκεκριμένο αρχείο
            if 'Source' in df.columns:
                df['Source'] = df['Source'].astype(str).str.strip().str.lower()
                df = df[df['Source'] != filename.strip().lower()]
    
            # Πρόσθεσε τα νέα δεδομένα
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            df = clean_dataframe_for_gsheet(df)
            update_google_sheet(df)
            #print(f"[DEBUG] Google Sheet updated, rows after update: {len(df)}")
    
            return jsonify({"status": "ok"})
    
        except Exception as e:
            print(f"[ERROR] Exception in save_file_data for {filename}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
