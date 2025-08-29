# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 10:44:23 2025

@author: User
"""
from flask import Flask
from routes.routes import register_routes
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from priority_classifier import PriorityClassifier
from config import MODEL_FILE


app = Flask(__name__)

#print("[DEBUG] Initializing Flask app...")

# Φόρτωση μοντέλου προτεραιότητας
#print("[DEBUG] Loading PriorityClassifier model from:", MODEL_FILE)
priority_model = PriorityClassifier(model_path=MODEL_FILE)
priority_model.load()
#print("[DEBUG] PriorityClassifier model loaded successfully")

# Φόρτωση μοντέλου σύνοψης κειμένου
#print("[DEBUG] Loading Greek text summarization model...")
tokenizer = AutoTokenizer.from_pretrained("kriton/greek-text-summarization")
model = AutoModelForSeq2SeqLM.from_pretrained("kriton/greek-text-summarization")
#print("[DEBUG] Summarization model loaded successfully")

# Συνάρτηση δημιουργίας summary
def generate_summary(article):
    #print("[DEBUG] Generating summary for article (length:", len(article), ")")
    inputs = tokenizer(
        article,
        return_tensors="pt",
        max_length=512,
        truncation=True,
        padding="max_length"
    )

    outputs = model.generate(
        inputs["input_ids"],
        max_length=60,
        min_length=25,
        length_penalty=1.3,
        num_beams=10,
        early_stopping=True,
        no_repeat_ngram_size=2
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    #print("[DEBUG] Summary generated:", summary[:75], "...")
    return summary

# Εγγραφή routes
#print("[DEBUG] Registering routes...")
register_routes(app, priority_model, generate_summary)
#print("[DEBUG] Routes registered successfully")

# Εκκίνηση Flask server
if __name__ == "__main__":
   # print("[DEBUG] Starting Flask server in debug mode...")
    app.run(debug=True)
