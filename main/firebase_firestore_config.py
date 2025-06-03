import os
import base64
import mimetypes
import firebase_admin
from firebase_admin import credentials, firestore

# Path to the Firebase service account key file
# For production, store this securely and reference via environment variables
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": os.environ.get('FIREBASE_PROJECT_ID', ''),
    "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID', ''),
    "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
    "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL', ''),
    "client_id": os.environ.get('FIREBASE_CLIENT_ID', ''),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL', '')
}

# Initialize Firebase
def initialize_firebase():
    try:
        # Check if Firebase is already initialized
        app = firebase_admin.get_app()
        return app
    except ValueError:
        try:
            cred = credentials.Certificate(FIREBASE_CONFIG)
            app = firebase_admin.initialize_app(cred)
            print(f"Initialized Firebase with project ID: {FIREBASE_CONFIG['project_id']}")
            return app
        except Exception as e:
            print(f"Error initializing Firebase: {str(e)}")
            return None

# Get a reference to the Firestore database
def get_firestore_db():
    # Initialize Firebase
    app = initialize_firebase()
    if not app:
        return None
    try:
        # Get Firestore client
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Error getting Firestore client: {str(e)}")
        return None
        
# Get a reference to the media collection in Firestore
def get_media_collection(collection_name='media'):
    db = get_firestore_db()
    if not db:
        return None
    
    try:
        # Get reference to the media collection
        collection_ref = db.collection(collection_name)
        return collection_ref
    except Exception as e:
        print(f"Error getting media collection: {str(e)}")
        return None

# Upload a file to Firestore
def upload_file_to_firestore(file_path, destination_path):
    # Get media collection reference
    collection_ref = get_media_collection()
    if not collection_ref:
        return None
    
    try:
        # Read file as binary
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # Get file mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Encode file data as base64
        encoded_data = base64.b64encode(file_data).decode('utf-8')
        
        # Create file metadata
        file_metadata = {
            'name': os.path.basename(file_path),
            'path': destination_path,
            'content_type': mime_type,
            'size': len(file_data),
            'data': encoded_data,
            'uploaded_at': firestore.SERVER_TIMESTAMP
        }
        
        # Create a document ID from the path (with some cleaning)
        doc_id = destination_path.replace('/', '_')
        
        # Save to Firestore
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(file_metadata)
        
        # Return a URL-like reference to the file
        return f"/media/{destination_path}"
    except Exception as e:
        print(f"Error uploading file to Firestore: {str(e)}")
        return None

# Upload a file from memory to Firestore
def upload_from_memory_to_firestore(file_bytes, destination_path, content_type, filename):
    # Get media collection reference
    collection_ref = get_media_collection()
    if not collection_ref:
        return None
    
    try:
        # Encode file data as base64
        encoded_data = base64.b64encode(file_bytes).decode('utf-8')
        
        # Create file metadata
        file_metadata = {
            'name': filename,
            'path': destination_path,
            'content_type': content_type,
            'size': len(file_bytes),
            'data': encoded_data,
            'uploaded_at': firestore.SERVER_TIMESTAMP
        }
        
        # Create a document ID from the path (with some cleaning)
        doc_id = destination_path.replace('/', '_')
        
        # Save to Firestore
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(file_metadata)
        
        # Return a URL-like reference to the file
        return f"/media/{destination_path}"
    except Exception as e:
        print(f"Error uploading file to Firestore: {str(e)}")
        return None

# Get file from Firestore
def get_file_from_firestore(file_path):
    # Get media collection reference
    collection_ref = get_media_collection()
    if not collection_ref:
        print(f"Could not get media collection reference for {file_path}")
        return None
    
    try:
        # Create a document ID from the path (with some cleaning)
        doc_id = file_path.replace('/', '_')
        
        # Get document from Firestore
        doc_ref = collection_ref.document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"File not found in Firestore: {file_path}")
            return None
    except Exception as e:
        print(f"Error getting file from Firestore: {str(e)}")
        return None

# Delete file from Firestore
def delete_file_from_firestore(file_path):
    # Get media collection reference
    collection_ref = get_media_collection()
    if not collection_ref:
        print(f"Could not get media collection reference for deleting {file_path}")
        return False
    
    try:
        # Create a document ID from the path (with some cleaning)
        doc_id = file_path.replace('/', '_')
        
        # Delete document from Firestore
        doc_ref = collection_ref.document(doc_id)
        doc_ref.delete()
        
        print(f"Successfully deleted file from Firestore: {file_path}")
        return True
    except Exception as e:
        print(f"Error deleting file from Firestore: {str(e)}")
        return False

# Functions for backward compatibility
def upload_file_to_firebase(file_path, destination_blob_name, custom_bucket=None):
    try:
        return upload_file_to_firestore(file_path, destination_blob_name)
    except Exception as e:
        print(f"Error in backward compatibility upload: {str(e)}")
        return None
