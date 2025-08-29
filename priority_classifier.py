# -*- coding: utf-8 -*-
"""
Priority Email Classifier (SVM version)
Created on Tue Aug 26 10:44:23 2025
"""

import re
import unicodedata
import dill  # για pickle αντικείμενα με πιο σύνθετα objects
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ===== Preprocessing =====
def clean_text(text):
    """
    Καθαρίζει το κείμενο:
    - μετατρέπει σε πεζά
    - αφαιρεί τόνους και διακριτικά
    - κρατά μόνο αλφαριθμητικά και κενά
    """
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    text = re.sub(r'[^a-zα-ω0-9 ]', ' ', text)
    return text.strip()

# ===== Classifier =====
class PriorityClassifier:
    def __init__(self, model_path="priority_model.pkl"):
        self.model_path = model_path
        self.pipeline = None
        print(f"[DEBUG] PriorityClassifier initialized with model_path: {self.model_path}")

    def train(self, texts, labels):
        """
        Εκπαιδεύει τον ταξινομητή (TF-IDF + LinearSVC)
        και αποθηκεύει το μοντέλο σε αρχείο.
        """
        #print("[DEBUG] Training PriorityClassifier...")
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(preprocessor=clean_text, ngram_range=(1, 2))),
            ('clf', LinearSVC())
        ])
        self.pipeline.fit(texts, labels)
        #print("[DEBUG] Training completed.")

        # Αποθήκευση με dill
        with open(self.model_path, "wb") as f:
            dill.dump(self.pipeline, f)
        #print(f"[DEBUG] Model saved to {self.model_path}")

    def load(self):
        """
        Φορτώνει το μοντέλο από αρχείο.
        """
        try:
            with open(self.model_path, "rb") as f:
                self.pipeline = dill.load(f)
            #print(f"[DEBUG] Model loaded from {self.model_path}")
        except FileNotFoundError:
            print(f"[DEBUG][ERROR] Model file not found: {self.model_path}")
            self.pipeline = None

    def predict(self, text):
        """
        Κάνει πρόβλεψη προτεραιότητας για ένα κείμενο.
        """
        if not self.pipeline:
            raise Exception("[DEBUG][ERROR] Model not loaded or trained yet!")
        prediction = self.pipeline.predict([text])[0]
        #print(f"[DEBUG] Prediction for text: {text} → {prediction}")
        return prediction


"""

# ===== Training Data =====
train_texts = [
    # High Priority (20)
    "Χρειαζόμαστε άμεσα υποστήριξη στο CRM γιατί το σύστημα έχει πέσει",
    "Παρακαλώ δείτε το ζήτημα σήμερα, είναι κρίσιμο",
    "Πρέπει να λυθεί το πρόβλημα πριν την παρουσίαση σε πελάτες",
    "Απαιτείται άμεση παρέμβαση από την τεχνική ομάδα",
    "Το συμβόλαιο κινδυνεύει αν δεν επιλυθεί γρήγορα",
    "Πολύ επείγον αίτημα από τη διοίκηση",
    "Το σύστημα πληρωμών είναι εκτός λειτουργίας, άμεση επέμβαση",
    "Κρίσιμο θέμα ασφαλείας πρέπει να επιλυθεί τώρα",
    "Αν δεν διορθωθεί το bug θα σταματήσουν οι παραγγελίες",
    "Άμεση αναβάθμιση του server απαιτείται σήμερα",
    "Ζητείται παρέμβαση τεχνικής ομάδας άμεσα",
    "Σφάλμα στην πλατφόρμα εμποδίζει πωλήσεις",
    "Προβλήματα με ERP, χρειάζεται άμεση λύση",
    "Η εφαρμογή δεν φορτώνει, επιλύστε το τώρα",
    "Άμεση αντιμετώπιση προβλήματος με emails",
    "Το CRM μπλοκάρει τις νέες εγγραφές πελατών",
    "Υψηλή προτεραιότητα: backup server κατεστραμμένος",
    "Απαιτείται άμεση επιδιόρθωση της βάσης δεδομένων",
    "Πελάτες δεν λαμβάνουν τιμολόγια, κρίσιμο ζήτημα",
    "Το ticket system έχει κολλήσει, επιλύστε άμεσα",

    # Medium Priority (20)
    "Θα θέλαμε μια συνάντηση την επόμενη εβδομάδα",
    "Παρακαλώ στείλτε μια προσφορά μέχρι το τέλος του μήνα",
    "Να κανονίσουμε call την επόμενη Παρασκευή",
    "Χρειάζεται να δούμε τις λεπτομέρειες της προσφοράς",
    "Μπορείτε να μας ενημερώσετε για το χρονοδιάγραμμα",
    "Θα θέλαμε μια παρουσίαση του συστήματος στο γραφείο μας",
    "Παρακαλώ ελέγξτε την πρόταση και ενημερώστε μας",
    "Προγραμματίζουμε μια συνάντηση για τη νέα υπηρεσία",
    "Μπορείτε να μας στείλετε το ενημερωτικό δελτίο;",
    "Ας κανονίσουμε μια συζήτηση για το project",
    "Απαιτείται αναθεώρηση του πλάνου εργασίας",
    "Παρακαλώ προετοιμάστε την αναφορά για τον επόμενο μήνα",
    "Θα θέλαμε feedback σχετικά με την προσφορά μας",
    "Σχεδιάζουμε να παρουσιάσουμε την υπηρεσία στο client",
    "Ας κανονίσουμε μια δοκιμαστική συνάντηση",
    "Παρακαλώ επικοινωνήστε για λεπτομέρειες παραγγελίας",
    "Μπορείτε να μας ενημερώσετε για τις αλλαγές στο σύστημα;",
    "Χρειαζόμαστε ενημέρωση σχετικά με το status του project",
    "Ας προγραμματίσουμε demo για την επόμενη εβδομάδα",
    "Παρακαλώ ελέγξτε τα έγγραφα πριν την επόμενη συνάντηση",

    # Low Priority (20)
    "Μπορούμε να το δούμε σε μελλοντικό χρόνο",
    "Όταν έχετε χρόνο, στείλτε μου ένα update",
    "Δεν υπάρχει βιασύνη, απλώς για ενημέρωση",
    "Ας το προγραμματίσουμε για αργότερα",
    "Θα το ξανασυζητήσουμε τον επόμενο μήνα",
    "Αυτό είναι περισσότερο για πληροφόρηση παρά επείγον",
    "Μπορείτε να μας ενημερώσετε όταν βρείτε χρόνο",
    "Όταν έχετε διάθεση, ας το δούμε",
    "Προαιρετική ενημέρωση για το project",
    "Χαμηλή προτεραιότητα: μικρές διορθώσεις",
    "Δεν χρειάζεται άμεση ενέργεια για αυτό το θέμα",
    "Όταν υπάρχει χρόνος, ας συζητήσουμε τις λεπτομέρειες",
    "Μπορεί να εξεταστεί σε μελλοντική συνάντηση",
    "Χαμηλή προτεραιότητα: μόνο για αναφορά",
    "Αυτό μπορεί να περιμένει μέχρι την επόμενη εβδομάδα",
    "Μικρές αλλαγές στο σύστημα, όχι επείγον",
    "Πληροφοριακό μήνυμα, χωρίς άμεση ενέργεια",
    "Δεν χρειάζεται παρέμβαση άμεσα",
    "Απλώς για ενημέρωση, χωρίς πίεση",
    "Ας το δούμε όταν υπάρχει χρόνος διαθέσιμος",
    " "
]

train_labels = ["high"]*20 + ["medium"]*20 + ["low"]*21


X_train, X_test, y_train, y_test = train_test_split(
    train_texts, train_labels, test_size=0.3, random_state=42, stratify=train_labels
)


# ===== Train & Evaluate =====
classifier = PriorityClassifier()
classifier.train(X_train, y_train)

y_pred = classifier.pipeline.predict(X_test)

print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))


# ===== Example Predictions =====
clf2 = PriorityClassifier()
clf2.load()

examples = [
    "Παρακαλώ δείτε το ζήτημα σήμερα γιατί είναι κρίσιμο",
    "Χρειάζομαστε υποστήριξη στο σύστημα CRM",
    "Δεν υπάρχει βιασύνη, ενημερώστε με όποτε μπορέσετε",
    "Ας κανονίσουμε μια παρουσίαση την επόμενη εβδομάδα"
]

for ex in examples:
    print(f"Email: {ex} → Predicted Priority: {clf2.predict(ex)}")
"""