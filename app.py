from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
import tensorflow as tf  # Assuming TensorFlow is used for the model
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load necessary files and models
model = tf.keras.models.load_model("my_model.h5")  # Load your trained model
try:
    symptom_severity = pd.read_csv('Symptom-severity.csv')
    symptoms_df = pd.read_csv('symtoms_df (1).csv')
    doctor_df=pd.read_csv('doctor.csv')
except Exception as e:
    print("Error loading datasets:", e)
# Clean and preprocess data
symptom_severity['Symptom'] = symptom_severity['Symptom'].str.strip().str.lower()
symptoms_df.columns = symptoms_df.columns.str.strip().str.lower()
symptom_severity['Symptom'] = symptom_severity['Symptom'].str.strip().str.lower()

# Standardize symptom formatting in symptoms_df and combine symptom columns
symptoms_df['symptom_1'] = symptoms_df['symptom_1'].str.strip().str.lower()
symptoms_df['symptom_2'] = symptoms_df['symptom_2'].str.strip().str.lower()
symptoms_df['symptom_3'] = symptoms_df['symptom_3'].str.strip().str.lower()
symptoms_df['symptom_4'] = symptoms_df['symptom_4'].str.strip().str.lower()

# Combine symptom columns into a single list for each row
symptoms_df['combined_symptoms'] = symptoms_df[['symptom_1', 'symptom_2', 'symptom_3','symptom_4']].values.tolist()

# Create the symptom list and encode using MultiLabelBinarizer
symptom_list = symptom_severity['Symptom'].unique()
mlb = MultiLabelBinarizer(classes=symptom_list)

mlb.fit([symptom_list])  # Fit MultiLabelBinarizer with symptoms
label_encoder = LabelEncoder()
label_encoder.fit(doctor_df['Disease'])  # Fit LabelEncoder with diseases


def predict_disease(symptom_input):
    recognized_symptoms = [symptom.strip().lower() for symptom in symptom_input if symptom.strip().lower() in symptom_list]
    if not recognized_symptoms:
        return "No recognized symptoms provided. Please check the symptoms and try again.", None

    try:
        # Transform symptoms into the required format
        symptoms_array = mlb.transform([recognized_symptoms])
        
        # Check if input matches model's expected shape
        if symptoms_array.shape[1] != 132:
            return "Input format error: Incorrect number of input features.", None

        disease_prediction = model.predict(symptoms_array)
        disease_index = np.argmax(disease_prediction)
        disease_name = label_encoder.inverse_transform([disease_index])[0]

        # Find specialist
        if disease_name in doctor_df['Disease'].values:
            specialist = doctor_df[doctor_df['Disease'] == disease_name]['Specialty'].values[0]
            return disease_name, specialist
        else:
            return disease_name, "No specialist found for this disease."

    except Exception as e:
        print("Unexpected error during prediction:", e)
        return "An unexpected error occurred. Please try again.", None

@app.route('/get-symptoms', methods=['GET'])
def get_symptoms():
    try:
        symptoms = symptom_severity['Symptom'].tolist()
        return jsonify({"symptoms": symptoms}), 200
    except Exception as e:
        print("Error fetching symptoms:", e)
        return jsonify({"error": "Failed to fetch symptoms."}), 500

@app.route('/predict-disease', methods=['POST'])
def predict_disease_api():
    try:
        # Log incoming data
        print("Request data:", request.data)
        print("Request JSON:", request.get_json())
        
        # Get JSON data from the request
        data = request.get_json()

        if not data or "symptoms" not in data:
            return jsonify({"error": "No symptoms provided. Please send symptoms in the request."}), 400

        # Extract symptoms from the JSON
        symptoms = data["symptoms"]

        # Call the prediction function
        disease, specialist = predict_disease(symptoms)

        if specialist:
            return jsonify({
                "disease": disease,
                "specialist": specialist
            }), 200
        else:
            return jsonify({
                "error": disease  # This will contain the error message
            }), 400
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True)
