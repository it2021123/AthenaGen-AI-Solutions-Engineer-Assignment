# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 10:44:23 2025

@author: User
"""

import os
import os
from google.cloud import storage  # ή όποια βιβλιοθήκη χρειάζεσαι

#Path Φακελος
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER =  BASE_DIR
#Path Email-Forms Folder
EMAIL_FOLDER = os.path.join(DATA_FOLDER,"emails")

#Path File model
MODEL_FILE = os.path.join(BASE_DIR, "priority_model.pkl")

#Path Credentials json
current_dir = os.getcwd()
credentials_path = os.path.join(current_dir, "credentials.json")
# Ανάλογα με τη βιβλιοθήκη, π.χ. για storage:
client = storage.Client.from_service_account_json(credentials_path)


# Στήλες CSV
COLUMNS = ['Type','Source','Date','Client_Name','Email','Phone','Company',
           'Service_Interest','Amount','VAT','Total_Amount','Invoice_Number','Priority','Message']