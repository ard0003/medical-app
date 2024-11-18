from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
import tensorflow as tf  # Assuming TensorFlow is used for the model

app = Flask(__name__)

# Load necessary files and models
model = tf.keras.models.load_model("my_model.h5")  # Load your trained model
symptom_list = ["fever", "cough", "headache", "lethargy", "weight_loss"]  # Example symptom list
doctor_df = pd.DataFrame({
    'Disease': ['Disease1', 'Disease2'],
    'Specialty': ['Specialist1', 'Specialist2']
})  # Replace with your doctor dataframe
mlb = MultiLabelBinarizer()
mlb.fit([symptom_list])  # Fit MultiLabelBinarizer with symptoms
label_encoder = LabelEncoder()
label_encoder.fit(doctor_df['Disease'])  # Fit LabelEncoder with diseases


def predict_disease(symptom_input):
    # Clean and check input symptoms
    recognized_symptoms = [symptom.strip().lower() for symptom in symptom_input if symptom.strip().lower() in symptom_list]
    if not recognized_symptoms:
        return "No recognized symptoms provided. Please check the symptoms and try again.", None

    try:
        # Transform symptoms into the required format
        symptoms_array = mlb.transform([recognized_symptoms])
        disease_prediction = model.predict(symptoms_array)
        disease_index = np.argmax(disease_prediction)
        disease_name = label_encoder.inverse_transform([disease_index])[0]

        # Check if disease exists in doctor_df
        if disease_name in doctor_df['Disease'].values:
            # Find specialist
            specialist = doctor_df[doctor_df['Disease'] == disease_name]['Specialty'].values[0]
            return disease_name, specialist
        else:
            return disease_name, "No specialist found for this disease."

    except KeyError as e:
        print("KeyError encountered during prediction:", e)
        print("Symptom input:", symptom_input)
        print("Recognized symptoms after filtering:", recognized_symptoms)
        return "Error during prediction. Please check the input symptoms and try again.", None
    except IndexError as e:
        print("IndexError encountered:", e)
        print("Disease name:", disease_name)
        return "Error: Specialist information is unavailable for this disease.", None
    except Exception as e:
        print("Unexpected error:", e)
        return "An unexpected error occurred. Please try again.", None


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
