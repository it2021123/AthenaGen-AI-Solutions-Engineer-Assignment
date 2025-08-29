# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 10:45:11 2025

@author: User
"""
import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from config import COLUMNS
import numpy as np


def get_client():
    try:
        # Παίρνει το path από το ENV VAR
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path or not os.path.exists(credentials_path):
            print("[DEBUG][ERROR] GOOGLE_APPLICATION_CREDENTIALS not set or file not found!")
            return None

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"[DEBUG][ERROR] Failed to authorize Google Sheets client: {e}")
        return None 

def read_google_sheet():
    client = get_client()
    sheet = client.open("TechFlow Solution").sheet1
    data = sheet.get_all_records()
    
    # Έλεγχος αν υπάρχει τουλάχιστον μια γραμμή δεδομένων
    if not data:
        print("[DEBUG] Google Sheet is empty, returning empty DataFrame")
        return pd.DataFrame(columns=COLUMNS)
    
    df = pd.DataFrame(data)
    
    # Έλεγχος αν λείπουν απαραίτητες στήλες
    missing_cols = [col for col in COLUMNS if col not in df.columns]
    if missing_cols:
        print("[DEBUG] WARNING: Missing columns in sheet:", missing_cols)
    
    return df


def update_google_sheet(df):
    #print("[DEBUG] Updating Google Sheet...")
    
    # Έλεγχος αν το DataFrame είναι άδειο
    if df.empty:
        print("[DEBUG][WARNING] DataFrame is empty. Nothing to update.")
        return False
    
    # Απόκτηση client
    client = get_client()
    if client is None:
        print("[DEBUG][ERROR] Could not get Google Sheets client.")
        return False
    
    try:
        sheet = client.open("TechFlow Solution").sheet1
        print("[DEBUG] Clearing existing sheet data...")
        sheet.clear()  # Σβήνει ΟΛΑ πριν γράψεις ξανά
        
        # Προετοιμασία δεδομένων για Google Sheet
        data = [df.columns.values.tolist()] + df.values.tolist()
        #print(f"[DEBUG] Updating sheet with {len(df)} rows.")
        sheet.update("A1", data)
        #print("[DEBUG] Google Sheet updated successfully.")
        return True
    except Exception as e:
        print(f"[DEBUG][ERROR] Failed to update Google Sheet: {e}")
        return False

def clean_dataframe_for_gsheet(df):
   # print("[DEBUG] Cleaning DataFrame for Google Sheet...")
    
    # Έλεγχος αν DataFrame έχει στήλες
    if df.empty:
        print("[DEBUG][WARNING] DataFrame is empty. Nothing to clean.")
        return df
    
    try:
        for col in df.columns:
            # Αντικατάσταση None με κενό string
            df[col] = df[col].apply(lambda x: "" if x is None else x)
            # Αντικατάσταση NaN ή inf με κενό string
            df[col] = df[col].apply(lambda x: "" if isinstance(x, float) and (pd.isna(x) or np.isinf(x)) else x)
            df[col] = df[col].astype(str)
        #print("[DEBUG] DataFrame cleaned successfully.")
        return df
    except Exception as e:
        print(f"[DEBUG][ERROR] Failed to clean DataFrame: {e}")
        return df


def append_to_google_sheet(new_row):
    # Έλεγχος αν η είσοδος είναι dict
    if not isinstance(new_row, dict):
        print("[DEBUG] ERROR: new_row is not a dictionary:", new_row)
        return False
    
    # Καθαρισμός δεδομένων πριν append
    for col in COLUMNS:
        if col not in new_row:
            new_row[col] = ""
        elif new_row[col] is None or (isinstance(new_row[col], float) and (pd.isna(new_row[col]) or np.isinf(new_row[col]))):
            new_row[col] = ""
    
    #print("[DEBUG] Appending new row:", new_row)
    client = get_client()
    sheet = client.open("TechFlow Solution").sheet1
    row_data = [new_row[col] for col in COLUMNS]
    sheet.append_row(row_data, value_input_option="USER_ENTERED")
    #print("[DEBUG] Row appended successfully")
    return True


