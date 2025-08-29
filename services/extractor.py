# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 10:44:23 2025

@author: User
"""
import os
import pandas as pd
import re
from datetime import datetime
from priority_classifier import PriorityClassifier
from email.utils import parsedate_to_datetime


class EmailExtractor:
    def __init__(self, email_folder, priority_model=None, summarizer=None):
        """
        Κλάση για εξαγωγή δεδομένων από .eml αρχεία.
        :param email_folder: φάκελος με τα .eml αρχεία
        :param priority_model: μοντέλο για πρόβλεψη προτεραιότητας
        :param summarizer: συνάρτηση generate_summary
        """
        self.email_folder = email_folder
        self.priority_model = priority_model
        self.summarizer = summarizer
        self.fields = ['Type','Source','Date','Client_Name','Email','Phone','Company',
                       'Service_Interest','Amount','VAT','Total_Amount','Invoice_Number','Priority','Message']
        #print(f"[DEBUG] EmailExtractor initialized for folder: {self.email_folder}")

    # --- Εξαγωγή ενδιαφέροντος υπηρεσίας ---
    def extract_service_interest(self, text):
        #print("[DEBUG] Extracting service interest...")
        lines = text.splitlines()
        service_lines = []
        keywords = ["χρειαζόμαστε", "ανάγκη", "θα θέλαμε", "θέλουμε", "προβλημα μας", "θα θελησουμε"]
        capture = False

        for line in lines:
            line_clean = line.lower().strip()
            if any(keyword in line_clean for keyword in keywords):
                capture = True
                service_lines.append(line.strip())
                continue
            if capture:
                if line.strip().startswith("-") or re.match(r"\d+\.", line.strip()) or line.strip() == "":
                    service_lines.append(line.strip())
                else:
                    break

        service_lines = [l for l in service_lines if l]
        interest_text = "\n".join(service_lines)
        #print(f"[DEBUG] Extracted service interest length: {len(interest_text)}")
        return interest_text

    # --- Εξαγωγή ημερομηνίας email ---
    def extract_email_date(self, text):
        match = re.search(r'^Date:\s*(.*)', text, re.MULTILINE)
        if match:
            date_str = match.group(1).strip()
            try:
                dt = parsedate_to_datetime(date_str)
                formatted_date = dt.strftime("%Y-%m-%d")
                #print(f"[DEBUG] Extracted email date: {formatted_date}")
                return formatted_date
            except (TypeError, ValueError):
                print(f"[DEBUG][WARNING] Could not parse date, returning raw string: {date_str}")
                return date_str
        else:
            current_date = datetime.now().strftime("%Y-%m-%d")
            print(f"[DEBUG][INFO] Date not found, using current date: {current_date}")
            return current_date

    # --- Εξαγωγή τιμολογίων ---
    def extract_invoice_info(self, text):
        data = {}
        #print("[DEBUG] Extracting invoice info...")
        match = re.search(r'Αριθμός:\s*([A-Z0-9\-]+)', text)
        data['Invoice_Number'] = match.group(1).strip() if match else ""

        match = re.search(r'Καθαρή Αξία:\s*€([\d,\.]+)', text)
        data['Amount'] = match.group(1).replace(",", "").strip() if match else ""

        match = re.search(r'ΦΠΑ\s*\d+%:\s*€([\d,\.]+)', text)
        data['VAT'] = match.group(1).replace(",", "").strip() if match else ""

        match = re.search(r'Συνολικό Ποσό:\s*€([\d,\.]+)', text)
        data['Total_Amount'] = match.group(1).replace(",", "").strip() if match else ""

        #print(f"[DEBUG] Invoice info extracted: {data}")
        return data

    # --- Εξαγωγή όλων των πεδίων από κείμενο ---
    def extract_from_text(self, text, source_file):
        #print(f"[DEBUG] Extracting data from text of file: {source_file}")
        data = {field: "" for field in self.fields}
        data['Type'] = 'EMAIL'
        data['Source'] = source_file
        data['Date'] = self.extract_email_date(text)

        # Extract βασικά στοιχεία
        patterns = {
            'Client_Name': r'- Όνομα:\s*(.*)',
            'Email': r'- Email:\s*([\w\.\-@]+)',
            'Phone': r'- Τηλέφωνο:\s*(.*)',
            'Company': r'- Εταιρεία:\s*(.*)'
        }
        for field, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                data[field] = match.group(1).strip()
                #print(f"[DEBUG] Extracted {field}: {data[field]}")
            else:
                print(f"[DEBUG] No Extracted {field} with pattern:{pattern}")
            

        # Service interest ή invoice info
        mes = self.extract_service_interest(text)
        data['Service_Interest'] = mes

        if mes == "":
            invoice_data = self.extract_invoice_info(text)
            data.update(invoice_data)
            data['Priority'] = 'medium'
            match = re.search(r'Προμηθευτής:\s*(.*)', text)
            if match:
                data['Company'] = match.group(1).strip()
                if not data.get('Client_Name'):
                    data['Client_Name'] = match.group(1).strip()
        else:
            # Δημιουργία summary
            if self.summarizer:
                summary_text = self.summarizer(mes)
                if isinstance(summary_text, list) and 'summary_text' in summary_text[0]:
                    summary_text = summary_text[0]['summary_text']
                data['Message'] = summary_text
                #print(f"[DEBUG] Generated summary length: {len(summary_text)}")
            else:
                data['Message'] = mes
            # Προτεραιότητα
            if self.priority_model:
                data['Priority'] = self.priority_model.predict(data['Message'])
                #print(f"[DEBUG] Predicted priority: {data['Priority']}")

        return data

    # --- Επεξεργασία μεμονωμένου email ---
    def process_email(self, file_path, existing_df=None):
        filename = os.path.basename(file_path)
        if existing_df is None:
            existing_df = pd.DataFrame(columns=self.fields)

        if not ((existing_df['Source'] == filename).any()):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                    content = file.read()
                new_data = self.extract_from_text(content, filename)
                #print(f"[DEBUG] Processed email: {filename}")
                return new_data
            except Exception as e:
                print(f"[DEBUG][ERROR] Failed to process email {filename}: {e}")
                return None
        else:
            print(f"[DEBUG][INFO] Το αρχείο {filename} έχει ήδη επεξεργαστεί.")
            return None

    # --- Έλεγχος ύπαρξης αρχείου και επεξεργασία ---
    def process_single_email(self, file_path, existing_df=None):
        if os.path.exists(file_path):
            return self.process_email(file_path, existing_df=existing_df)
        else:
            print(f"[DEBUG][ERROR] Το αρχείο δεν βρέθηκε: {file_path}")
            return None

    # --- Επεξεργασία όλων των emails στον φάκελο ---
    def process_all_emails(self, existing_df=None):
        files = [f for f in os.listdir(self.email_folder) if f.endswith(".eml")]
        all_new_data = []

        for f in files:
            if existing_df is None or not ((existing_df['Source'] == f).any()):
                path = os.path.join(self.email_folder, f)
                new_data = self.process_email(path, existing_df=existing_df)
                if new_data:
                    all_new_data.append(new_data)
                    

        #print(f"[DEBUG] Processed {len(all_new_data)} new emails.")
        return all_new_data


"""

class EmailExtractor:
    def __init__(self, email_folder, priority_model=None, summarizer=None):
        
        :param email_folder: φάκελος με τα .eml αρχεία
        :param priority_model: μοντέλο για πρόβλεψη προτεραιότητας
        :param summarizer: συνάρτηση generate_summary
        :param sheet_updater: συνάρτηση για ενημέρωση Google Sheet με νέα δεδομένα
        
        self.email_folder = email_folder
        self.priority_model = priority_model
        self.summarizer = summarizer
        self.fields = ['Type','Source','Date','Client_Name','Email','Phone','Company',
                       'Service_Interest','Amount','VAT','Total_Amount','Invoice_Number','Priority','Message']

    def extract_service_interest(self, text):
        lines = text.splitlines()
        service_lines = []
        keywords = ["χρειαζόμαστε", "ανάγκη", "θα θέλαμε", "θέλουμε", "προβλημα μας", "θα θελησουμε"]
        capture = False

        for line in lines:
            line_clean = line.lower().strip()
            if any(keyword in line_clean for keyword in keywords):
                capture = True
                service_lines.append(line.strip())
                continue

            if capture:
                if line.strip().startswith("-") or re.match(r"\d+\.", line.strip()) or line.strip() == "":
                    service_lines.append(line.strip())
                else:
                    break

        service_lines = [l for l in service_lines if l]
        return "\n".join(service_lines)

    def extract_email_date(self,text):
        match = re.search(r'^Date:\s*(.*)', text, re.MULTILINE)
        if match:
            date_str = match.group(1).strip()
            try:
                dt = parsedate_to_datetime(date_str)
                return dt.strftime("%Y-%m-%d")
            except (TypeError, ValueError):
                return date_str
        else:
            return datetime.now().strftime("%Y-%m-%d")

    def extract_invoice_info(self, text):
        data = {}
        match = re.search(r'Αριθμός:\s*([A-Z0-9\-]+)', text)
        data['Invoice_Number'] = match.group(1).strip() if match else ""

        match = re.search(r'Καθαρή Αξία:\s*€([\d,\.]+)', text)
        data['Amount'] = match.group(1).replace(",", "").strip() if match else ""

        match = re.search(r'ΦΠΑ\s*\d+%:\s*€([\d,\.]+)', text)
        data['VAT'] = match.group(1).replace(",", "").strip() if match else ""

        match = re.search(r'Συνολικό Ποσό:\s*€([\d,\.]+)', text)
        data['Total_Amount'] = match.group(1).replace(",", "").strip() if match else ""

        return data

    def extract_from_text(self, text, source_file):
        data = {field: "" for field in self.fields}
        data['Type'] = 'EMAIL'
        data['Source'] = source_file
        data['Date'] = self.extract_email_date(text)

        match = re.search(r'- Όνομα:\s*(.*)', text)
        if match: data['Client_Name'] = match.group(1).strip()

        match = re.search(r'- Email:\s*([\w\.\-@]+)', text)
        if match: data['Email'] = match.group(1).strip()

        match = re.search(r'- Τηλέφωνο:\s*(.*)', text)
        if match: data['Phone'] = match.group(1).strip()

        match = re.search(r'- Εταιρεία:\s*(.*)', text)
        if match: data['Company'] = match.group(1).strip()

        mes = self.extract_service_interest(text)
        data['Service_Interest'] = mes

        if data['Service_Interest'] == "":
            invoice_data = self.extract_invoice_info(text)
            data.update(invoice_data)
            data['Priority'] = 'medium'
            match = re.search(r'Προμηθευτής:\s*(.*)', text)
            if match:
                data['Company'] = match.group(1).strip()
                if not data.get('Client_Name'):
                    data['Client_Name'] = match.group(1).strip()
        else:
            if self.summarizer:
                summary_text = self.summarizer(mes)
                if isinstance(summary_text, list) and 'summary_text' in summary_text[0]:
                    summary_text = summary_text[0]['summary_text']
                data['Message'] = summary_text
            else:
                data['Message'] = mes
            if self.priority_model:
                data['Priority'] = self.priority_model.predict(data['Message'])

        return data

    def process_email(self, file_path, existing_df=None):
        filename = os.path.basename(file_path)
        if existing_df is None:
            existing_df = pd.DataFrame(columns=self.fields)

        if not ((existing_df['Source'] == filename).any()):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
            new_data = self.extract_from_text(content, filename)

            print(f"Processed single email: {filename}")
            return new_data
        else:
            print(f"Το αρχείο {filename} έχει ήδη επεξεργαστεί.")
            return None

    def process_single_email(self, file_path, existing_df=None):
        if os.path.exists(file_path):
            return self.process_email(file_path, existing_df=existing_df)
        else:
            raise FileNotFoundError(f"Το αρχείο δεν βρέθηκε: {file_path}")

    def process_all_emails(self, existing_df=None):
        files = [f for f in os.listdir(self.email_folder) if f.endswith(".eml")]
        all_new_data = []

        for f in files:
            if existing_df is None or not ((existing_df['Source'] == f).any()):
                path = os.path.join(self.email_folder, f)
                new_data = self.process_email(path, existing_df=existing_df)
                if new_data:
                    all_new_data.append(new_data)

        print(f"Processed {len(all_new_data)} emails.")
        return all_new_data
"""