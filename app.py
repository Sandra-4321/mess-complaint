import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
from google.cloud import storage as google_storage

# Initialize Firebase Admin SDK with credentials from Streamlit secrets
try:
    cred = credentials.Certificate({
    "type": st.secrets["firebase_adminsdk"]["type"],
    "project_id": st.secrets["firebase_adminsdk"]["project_id"],
    "private_key_id": st.secrets["firebase_adminsdk"]["private_key_id"],
    "private_key": st.secrets["firebase_adminsdk"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase_adminsdk"]["client_email"],
    "client_id": st.secrets["firebase_adminsdk"]["client_id"],
    "auth_uri": st.secrets["firebase_adminsdk"]["auth_uri"],
    "token_uri": st.secrets["firebase_adminsdk"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase_adminsdk"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase_adminsdk"]["client_x509_cert_url"]
    })

    firebase_admin.initialize_app(cred, {
        'storageBucket': 'mess-complaint-app.appspot.com'
    })
    st.info("Firebase initialized successfully.")
except Exception as e:
    st.error(f"Error initializing Firebase: {e}")

# Initialize Firestore and Firebase Storage
db = firestore.client()
bucket = storage.bucket()

# Streamlit App for Uploading Complaints
def upload_complaint():
    st.title("Submit Your Complaint")

    complaint_text = st.text_area("Enter your complaint:")
    complaint_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

    if st.button("Submit"):
        if complaint_text and complaint_image:
            try:
                # Upload image to Firebase Storage
                image_filename = complaint_image.name
                image_path = os.path.join("images", image_filename)

                # Save the uploaded image to Firebase storage
                blob = bucket.blob(image_path)
                blob.upload_from_file(complaint_image)

                # Save complaint data to Firestore
                complaint_ref = db.collection('complaints')
                complaint_ref.add({
                    'complaint_text': complaint_text,
                    'complaint_image_url': blob.public_url,
                    'status': 'pending'
                })
                st.success("Your complaint has been submitted successfully!")
            except Exception as e:
                st.error(f"An error occurred while uploading: {e}")
        else:
            st.error("Please enter complaint text and upload an image!")

# Show complaints from Firestore
def show_complaints():
    st.title("Complaints")
    complaints_ref = db.collection('complaints')
    complaints = complaints_ref.stream()

    if not complaints:
        st.write("No complaints available.")
    for complaint in complaints:
        complaint_data = complaint.to_dict()
        st.subheader(f"Complaint ID: {complaint.id}")
        st.write(f"Complaint Text: {complaint_data['complaint_text']}")
        st.write(f"Status: {complaint_data['status']}")
        st.image(complaint_data['complaint_image_url'], caption='Complaint Image', use_column_width=True)
        st.write("---")

# Main function
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page", ["Submit Complaint", "View Complaints"])

    if page == "Submit Complaint":
        upload_complaint()
    elif page == "View Complaints":
        show_complaints()

if __name__ == "__main__":
    main()





