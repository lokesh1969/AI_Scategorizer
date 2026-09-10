import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DATASET = [
    # --- SAFETY (English + Hindi + Mixed) ---
    ("Emergency fire alarm triggered at platform 2 station area. Evacuate passengers immediately.", "SAFETY"),
    ("Emergency fire alarm detected on platform 2 station area. Evacuate passengers immediately.", "SAFETY"),
    ("Accident report: Passenger slipped near escalator 3. Medical first aid administered.", "SAFETY"),
    ("Hazardous chemical spill detected near electrical substation room. Station safety protocol initiated.", "SAFETY"),
    ("Fire safety inspection report: All extinguishers verified and pressure levels normal.", "SAFETY"),
    ("Emergency notice: Platform edge safety door malfunction reported at Station Central.", "SAFETY"),
    ("प्लेटफॉर्म नंबर 2 पर आपातकालीन स्थिति उत्पन्न हुई। अग्निशामक दल तुरंत पहुंचे।", "SAFETY"),
    ("दुर्घटना रिपोर्ट: यात्री घायल सुरक्षा अधिकारी को सूचित किया गया।", "SAFETY"),
    ("आपातकालीन निर्देश: प्लेटफॉर्म खाली करने के निर्देश दिए गए हैं।", "SAFETY"),
    ("आग लगने की सूचना स्टेशन मास्टर कक्ष सुरक्षा चेतावनी जारी।", "SAFETY"),
    ("Platform 3 पर emergency fire alarm detected. Safety instructions issued.", "SAFETY"),
    ("Hazardous smoke reported near train 104 engine. Safety squad dispatched.", "SAFETY"),

    # --- FINANCE (English + Hindi + Mixed) ---
    ("Invoice #4029: Vendor payment clearance for electrical machinery parts total amount ₹4,50,000.", "FINANCE"),
    ("Quarterly financial budget allocation statement for metro line expansion Q3.", "FINANCE"),
    ("Expenditure statement: Monthly salary payouts, contractor bills, and utility expenses.", "FINANCE"),
    ("Purchase order PO-8891 for track maintenance tools total cost ₹2,15,000.", "FINANCE"),
    ("Financial audit report: Revenue collection from ticketing gates and commercial spaces.", "FINANCE"),
    ("वित्तीय विवरण: तिमाही बजट आवंटन रिपोर्ट और बैंक भुगतान विवरण।", "FINANCE"),
    ("इनवॉइस भुगतान चालान कुल राशि ₹4,50,000 स्वीकृत की गई।", "FINANCE"),
    ("वित्तीय लेखा परीक्षा रिपोर्ट वर्ष 2025-26 राजस्व संग्रह और व्यय।", "FINANCE"),
    ("भुगतान रसीद ठेकेदार बिल भुगतान बैंक खाता विवरण।", "FINANCE"),
    ("Invoice clearance for maintenance vendor amount ₹85,000 approved.", "FINANCE"),
    ("Financial statement and expense ledger for monthly operations.", "FINANCE"),

    # --- MAINTENANCE (English + Hindi + Mixed) ---
    ("Track defect report: Rail alignment fault detected near signal post 14. Maintenance needed.", "MAINTENANCE"),
    ("Escalator motor failure at West Gate exit. Spare part replacement requested.", "MAINTENANCE"),
    ("Equipment repair report: Air conditioning HVAC unit breakdown in server room.", "MAINTENANCE"),
    ("Routine preventive maintenance schedule for Metro rake 12 for the month of September.", "MAINTENANCE"),
    ("Machinery inspection report: Hydraulic brake system servicing completed.", "MAINTENANCE"),
    ("मशीनरी खराबी: प्लेटफॉर्म 3 पर एस्केलेटर बंद मरम्मत कार्य जारी।", "MAINTENANCE"),
    ("टैक रखरखाव: ट्रैक लाइन 2 मरम्मत कार्य अनुसूची तुरंत आवश्यक।", "MAINTENANCE"),
    ("उपकरण खराबी रिपोर्ट: एयर कंडीशनिंग यूनिट रिपेयरिंग शेड्यूल।", "MAINTENANCE"),
    ("स्टेशन बिजली आपूर्ति खराबी जनरेटर मरम्मत दल को भेजा गया।", "MAINTENANCE"),
    ("Platform 3 पर maintenance work urgently required machinery defect detected.", "MAINTENANCE"),
    ("Preventive track inspection and brake servicing scheduled overnight.", "MAINTENANCE"),

    # --- OPERATIONS (English + Hindi + Mixed) ---
    ("Daily station operational log: Train punctuality index 98.4%, total passenger count 1,24,000.", "OPERATIONS"),
    ("Shift handover report: Station master morning shift log and train arrival timelines.", "OPERATIONS"),
    ("Administrative operational policy update: Revised station security and ticketing guidelines.", "OPERATIONS"),
    ("Operational schedule adjustment for weekend passenger surge during festival season.", "OPERATIONS"),
    ("Station daily operations report: Platform crowd control and train dispatch timing.", "OPERATIONS"),
    ("दैनिक परिचालन रिपोर्ट: ट्रेन आगमन समय सारणी एवं प्लेटफॉर्म crowd प्रबंधन।", "OPERATIONS"),
    ("स्टेशन मास्टर शिफ्ट रिपोर्ट: दैनिक प्रशासनिक कार्य संचालन विवरण।", "OPERATIONS"),
    ("परिचालन अनुसूची बदलाव: सप्ताहांत ट्रेन फ्रीक्वेंसी वृद्धि निर्देश।", "OPERATIONS"),
    ("यात्री आवागमन और ऑटोमैटिक फेयर कलेक्शन गेट संचालन विवरण।", "OPERATIONS"),
    ("Daily train schedule and station control shift activity log.", "OPERATIONS"),
    ("Administrative memo regarding station staff duty schedules.", "OPERATIONS")
]

def train():
    texts = [item[0] for item in DATASET]
    labels = [item[1] for item in DATASET]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    X_vec = vectorizer.fit_transform(texts)

    model = LogisticRegression(C=10.0, max_iter=300, random_state=42)
    model.fit(X_vec, labels)

    save_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "classifier.pkl")

    joblib.dump({"vectorizer": vectorizer, "model": model}, model_path)
    print(f"[Train] Saved retrained classifier model to {model_path}")

if __name__ == "__main__":
    train()
