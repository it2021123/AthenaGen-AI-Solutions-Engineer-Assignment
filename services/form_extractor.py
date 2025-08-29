# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 10:44:23 2025

@author: User
"""


import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

class HtmlExtractor:
    def __init__(self, html_folder, priority_model=None):
        """
        Κλάση για εξαγωγή δεδομένων από .html αρχεία.
        :param html_folder: φάκελος με τα .html αρχεία
        :param priority_model: μοντέλο για πρόβλεψη προτεραιότητας
        """
        self.html_folder = html_folder
        self.priority_model = priority_model
        self.fields = ['Type','Source','Date','Client_Name','Email','Phone','Company',
                       'Service_Interest','Amount','VAT','Total_Amount','Invoice_Number','Priority','Message']
       # print(f"[DEBUG] HtmlExtractor initialized for folder: {self.html_folder}")

    # --- Εξαγωγή δεδομένων από HTML ---
    def extract_from_html(self, html_content, source_file):
        #print(f"[DEBUG] Extracting data from HTML file: {source_file}")
        data = {field: "" for field in self.fields}
        data['Source'] = source_file

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # === Contact Form ===
            if soup.find('input', {'name': 'full_name'}) or soup.find('textarea', {'name': 'message'}):
                data['Type'] = 'FORM'
                # Client_Name
                full_name = soup.find('input', {'name': 'full_name'})
                if full_name: data['Client_Name'] = full_name.get('value', '').strip()
                # Email
                email = soup.find('input', {'name': 'email'})
                if email: data['Email'] = email.get('value', '').strip()
                # Phone
                phone = soup.find('input', {'name': 'phone'})
                if phone: data['Phone'] = phone.get('value', '').strip()
                # Company
                company = soup.find('input', {'name': 'company'})
                if company: data['Company'] = company.get('value', '').strip()
                # Service Interest
                service = soup.find('select', {'name': 'service'})
                if service:
                    option = service.find('option', selected=True)
                    if option: data['Service_Interest'] = option.text.strip()
                # Message
                message = soup.find('textarea', {'name': 'message'})
                if message: data['Message'] = message.text.strip()
                # Date
                submission = soup.find('input', {'name': 'submission_date'})
                if submission:
                    date_str = submission.get('value', '').strip()
                    if date_str:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
                            data['Date'] = dt.strftime("%Y-%m-%d")
                        except ValueError:
                            data['Date'] = date_str
                # Priority
                priority = soup.find('select', {'name': 'priority'})
                if priority:
                    option = priority.find('option', selected=True)
                    if option: data['Priority'] = option.get('value', '').strip()
                # Προβλεψη προτεραιότητας αν δεν υπάρχει
                if self.priority_model and not data['Priority']:
                    data['Priority'] = self.priority_model.predict(data['Message'])
                    #print(f"[DEBUG] Predicted priority: {data['Priority']}")
            else:
                # === Invoice ===
                data['Type'] = 'INVOICE'
                invoice_number_tag = soup.find('strong', string="Αριθμός:")
                if invoice_number_tag and invoice_number_tag.next_sibling:
                    data['Invoice_Number'] = invoice_number_tag.next_sibling.strip()
                issuer_div = soup.find('div', {'class': 'company'})
                if issuer_div:
                    client_div = soup.find('strong', string="Πελάτης:")
                    if client_div:
                        next_elements = client_div.find_all_next(text=True)
                        if next_elements:
                            data['Client_Name'] = next_elements[1].strip()
                            data['Company'] = next_elements[1].strip()
                date_tag = soup.find('strong', string="Ημερομηνία:")
                if date_tag and date_tag.next_sibling:
                    date_str = date_tag.next_sibling.strip()
                    try:
                        dt = datetime.strptime(date_str, "%d/%m/%Y")
                        data['Date'] = dt.strftime("%Y-%m-%d")
                    except ValueError:
                        data['Date'] = date_str
                summary = soup.find("div", {"class": "summary"})
                if summary:
                    text = summary.get_text(" ", strip=True)
                    if "Καθαρή Αξία:" in text:
                        data['Amount'] = text.split("Καθαρή Αξία:")[-1].split("ΦΠΑ")[0].replace("€","").strip()
                    if "ΦΠΑ" in text:
                        data['VAT'] = text.split("ΦΠΑ 24%:")[-1].split("ΣΥΝΟΛΟ")[0].replace("€","").strip()
                    if "ΣΥΝΟΛΟ:" in text:
                        data['Total_Amount'] = text.split("ΣΥΝΟΛΟ:")[-1].replace("€","").strip()
           #print(f"[DEBUG] Extracted HTML data: {data}")
            return data
        except Exception as e:
            print(f"[DEBUG][ERROR] Failed to extract data from HTML {source_file}: {e}")
            return data

    # --- Επεξεργασία μεμονωμένου HTML ---
    def process_html(self, file_path, existing_df=None):
        filename = os.path.basename(file_path)
        if existing_df is None:
            existing_df = pd.DataFrame(columns=self.fields)

        if not ((existing_df['Source'] == filename).any()):
            if not os.path.exists(file_path):
                print(f"[DEBUG][ERROR] File not found: {file_path}")
                return None
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                new_data = self.extract_from_html(content, filename)
                #print(f"[DEBUG] Processed single HTML: {filename}")
                return new_data
            except Exception as e:
                print(f"[DEBUG][ERROR] Failed to process HTML {filename}: {e}")
                return None
        else:
            print(f"[DEBUG][INFO] Το αρχείο {filename} έχει ήδη επεξεργαστεί.")
            return None

    # --- Έλεγχος ύπαρξης αρχείου και επεξεργασία ---
    def process_single_form(self, file_path, existing_df=None):
        if os.path.exists(file_path):
            return self.process_html(file_path, existing_df=existing_df)
        else:
            print(f"[DEBUG][ERROR] Το αρχείο δεν βρέθηκε: {file_path}")
            return None

    # --- Επεξεργασία όλων των HTML στον φάκελο ---
    def process_all_htmls(self, existing_df=None):
        files = [f for f in os.listdir(self.html_folder) if f.endswith(".html")]
        all_new_data = []

        for f in files:
            if existing_df is None or not ((existing_df['Source'] == f).any()):
                path = os.path.join(self.html_folder, f)
                new_data = self.process_html(path, existing_df=existing_df)
                if new_data:
                    all_new_data.append(new_data)

        #print(f"[DEBUG] Processed {len(all_new_data)} new HTML files.")
        return all_new_data


"""

# === Χρήση για contact forms ===
priority_model = PriorityClassifier(model_path="priority_model.pkl")
priority_model.load()

contact_extractor = HtmlExtractor(html_folder="emails", csv_file="contact_forms.csv", priority_model=priority_model)
contact_extractor.process_all_htmls()
"""