# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 20:08:33 2025

@author: User

Auto Test Script για PriorityClassifier, EmailExtractor, HtmlExtractor και Google Sheets
"""

import os
import pandas as pd
import requests
import json
from routes.routes import register_routes
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from priority_classifier import PriorityClassifier
from config import MODEL_FILE
from services.data_service import read_google_sheet, update_google_sheet,clean_dataframe_for_gsheet,append_to_google_sheet,get_client
from services.form_extractor import HtmlExtractor
from services.extractor import EmailExtractor

BASE_URL = "http://127.0.0.1:5000"


#==========Testing Flask Endpoints===============

def test_data():
    print("\n=== GET /data ===")
    r = requests.get(f"{BASE_URL}/data")
    print("Status:", r.status_code)
    print("Response:", r.json()[:3], "...")  # εμφανίζει μόνο τις πρώτες 3 εγγραφές

def test_add():
    print("\n=== POST /add ===")
    new_row = {
        "Type": "EMAIL",
        "Source": "test_email.eml",
        "Date": "2025-08-27",
        "Client_Name": "John Doe",
        "Email": "john@example.com"
    }
    r = requests.post(f"{BASE_URL}/add", json=new_row)
    print("Status:", r.status_code)
    print("Response:", r.json())

def test_delete():
    print("\n=== DELETE /delete_by_source/test_email.eml ===")
    r = requests.delete(f"{BASE_URL}/delete_by_source/test_email.eml")
    print("Status:", r.status_code)
    print("Response:", r.json())

def test_extract():
    print("\n=== POST /extract/test_email.eml ===")
    r = requests.post(f"{BASE_URL}/extract/test_email.eml")
    print("Status:", r.status_code)
    print("Response:", r.json())

def test_list_emails():
    print("\n=== GET /list_emails ===")
    r = requests.get(f"{BASE_URL}/list_emails")
    print("Status:", r.status_code)
    print("Emails:", r.json())

def test_list_forms():
    print("\n=== GET /list_forms ===")
    r = requests.get(f"{BASE_URL}/list_forms")
    print("Status:", r.status_code)
    print("Forms:", r.json())
     
def test_invalid_endpoint():
    print("\n=== GET /invalid_endpoint ===")
    r = requests.get(f"{BASE_URL}/invalid_endpoint")
    print("Status:", r.status_code)  # αναμένεται 404
    try:
        print("Response:", r.json())
    except:
        print("Response is not JSON:", r.text)

def test_add_missing_fields():
    print("\n=== POST /add (missing fields) ===")
    bad_row = {
        "Type": "EMAIL"
        # λείπουν Source, Date, Client_Name κ.λπ.
    }
    r = requests.post(f"{BASE_URL}/add", json=bad_row)
    print("Status:", r.status_code)  # αναμένεται 400 ή error
    print("Response:", r.text)

def test_delete_nonexistent():
    print("\n=== DELETE /delete_by_source/not_exists.eml ===")
    r = requests.delete(f"{BASE_URL}/delete_by_source/not_exists.eml")
    print("Status:", r.status_code)  # αναμένεται 404
    print("Response:", r.json())

def test_get_file_data(filename):
    print(f"\n=== GET /get_file_data/{filename} ===")
    r = requests.get(f"{BASE_URL}/get_file_data/{filename}")
    print("Status:", r.status_code)
    print("Data:", json.dumps(r.json(), indent=2))

def test_save_file_data(filename, data):
    print(f"\n=== POST /save_file_data for {filename} ===")
    payload = {"filename": filename, "data": data}
    r = requests.post(f"{BASE_URL}/save_file_data", json=payload)
    print("Status:", r.status_code)
    print("Response:", r.json())

def test_delete_file(filename):
    print(f"\n=== DELETE /delete_file/{filename} ===")
    r = requests.delete(f"{BASE_URL}/delete_file/{filename}")
    print("Status:", r.status_code)
    print("Response:", r.json())


print("\n===== Testing Flask Endpoints =====")
test_data()
print("\n")
test_add()
print("\n")
test_delete()
print("\n")
test_extract()
print("\n")
test_list_emails()
print("\n")
test_list_forms()
print("\n")
test_delete_nonexistent()
print("\n")
test_add_missing_fields()
print("\n")
test_invalid_endpoint()
print("\n")
print("\n")
# Δοκιμή για ένα συγκεκριμένο αρχείο
print("Δοκιμή για ένα συγκεκριμένο αρχείο οχ email_09.eml ")
test_get_file_data("email_09.eml")
print("\n")
#Δοκιμή αποθήκευσης manual edit
sample_data = {"Type": "EMAIL", "Source": "email_09.eml", "Date": "2025-08-27 22:00:00"}
test_save_file_data("email_09.eml", sample_data)
print("\n")
# Δοκιμή διαγραφής
test_delete_file("email_09.eml")
print("\n")
print("\n")



# ============== 1PriorityClassifier =====================
print("===== Testing PriorityClassifier =====")
clf = PriorityClassifier()
clf.load()  # debug prints θα εμφανιστούν
test_texts = [
    "Απαιτείται άμεση παρέμβαση από την τεχνική ομάδα",
    "Δεν υπάρχει βιασύνη, ενημερώστε με όποτε μπορέσετε"
]

for t in test_texts:
    priority = clf.predict(t)
    print(f"[Classifier] Text: '{t}' → Priority: {priority}")




# ============== 2EmailExtractor ======================
print("\n===== Testing EmailExtractor =====")
email_folder = "emails"
email_extractor = EmailExtractor(email_folder=email_folder, priority_model=clf)
print("\n")
print("Contact Email")
sample_email = os.path.join(email_folder, "email_01.eml")
if os.path.exists(sample_email):
    email_data = email_extractor.process_single_email(sample_email)
    print("[EmailExtractor] Data:", email_data)
else:
    print("[EmailExtractor] No test_email.eml found in emails/ folder")
print("\n")
print("Invoice Email")
sample_email = os.path.join(email_folder, "email_09.eml")
if os.path.exists(sample_email):
    email_data = email_extractor.process_single_email(sample_email)
    print("[EmailExtractor] Data:", email_data)
else:
    print("[EmailExtractor] No test_email.eml found in emails/ folder")
    
print("\n===== Testing EmailExtractor Error Case =====")
bad_email = os.path.join(email_folder, "fake_email.eml")
if os.path.exists(bad_email):
    os.remove(bad_email)  # σιγουρεύουμε ότι δεν υπάρχει
try:
    email_extractor.process_single_email(bad_email)
except Exception as e:
    print("[EmailExtractor][ERROR] as expected:", e)

    
# ========3HtmlExtractor ========================================

print("\n===== Testing HtmlExtractor =====")
html_folder = "emails"
html_extractor = HtmlExtractor(html_folder=html_folder, priority_model=clf)
print("\n")
print("Invoice Form")
sample_form = os.path.join(html_folder, "invoice_tf-2024-004.html")
if os.path.exists(sample_form):
    form_data = html_extractor.process_single_form(sample_form)
    print("[HtmlExtractor] Data:", form_data)
else:
    print("[HtmlExtractor] No test_form.html found in forms/ folder")
print("\n")
print("Contact Form")
sample_form = os.path.join(html_folder, "contact_form_1.html")
if os.path.exists(sample_form):
    form_data = html_extractor.process_single_form(sample_form)
    print("[HtmlExtractor] Data:", form_data)
else:
    print("[HtmlExtractor] No test_form.html found in forms/ folder")

print("\n===== Testing HtmlExtractor Error Case =====")
bad_html = os.path.join(email_folder, "fake_form.html")
if os.path.exists(bad_html):
    os.remove(bad_html)  # σιγουρεύουμε ότι δεν υπάρχει
    try:
        form_data = html_extractor.process_single_form(bad_html)
    except Exception as e:
        print("[HtmlExtractor][ERROR] as expected:", e)


# ================ 4Google Sheets Functions ====================


print("\n===== Testing Google Sheets =====")

# Ανάγνωση Sheet
try:
    df = read_google_sheet()
    print("[GoogleSheets] Read DataFrame:")
    print(df.head())
except Exception as e:
    print(f"[GoogleSheets][ERROR] Failed to read sheet: {e}")

# Προσθήκη νέας γραμμής
new_row = {
    "Type": "EMAIL",
    "Source": "test_email.eml",
    "Date": "2025-08-27",
    "Client_Name": "John Doe",
    "Email": "john@example.com",
    "Phone": "1234567890",
    "Company": "TechFlow",
    "Service_Interest": "CRM Support",
    "Amount": "",
    "VAT": "",
    "Total_Amount": "",
    "Invoice_Number": "",
    "Priority": "high",
    "Message": "Απαιτείται άμεση παρέμβαση"
}

try:
    append_to_google_sheet(new_row)
    print("[GoogleSheets] New row appended successfully")
except Exception as e:
    print(f"[GoogleSheets][ERROR] Failed to append row: {e}")

# Ενημέρωση Sheet
try:
    if not df.empty:
        df['Priority'] = df['Priority'].apply(lambda x: x.upper())
        update_google_sheet(df)
        print("[GoogleSheets] Sheet updated successfully")
except Exception as e:
    print(f"[GoogleSheets][ERROR] Failed to update sheet: {e}")

print("\n===== Auto Test Completed =====")
