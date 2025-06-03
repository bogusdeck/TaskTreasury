import os
import base64
import mimetypes
import firebase_admin
from firebase_admin import credentials, firestore
import re

# Helper function to properly format the Firebase private key
def format_private_key(private_key):
    """Format the private key by handling various newline formats"""
    if not private_key:
        return ''
    
    # Check if the key is already properly formatted
    if private_key.startswith('-----BEGIN PRIVATE KEY-----') and private_key.endswith('-----END PRIVATE KEY-----'):
        # If it's already in PEM format, just ensure newlines are correct
        return private_key
    
    # For Vercel deployment, the private key is often provided as a base64 string without headers
    # Let's create a proper PEM format
    
    # Remove any existing newlines or spaces
    clean_key = private_key.replace('\n', '').replace('\\n', '').replace(' ', '')
    
    # Check if it's a raw base64 string (no PEM headers)
    if not clean_key.startswith('-----'):
        # Format as proper PEM with newlines every 64 characters
        chunks = [clean_key[i:i+64] for i in range(0, len(clean_key), 64)]
        formatted_key = '-----BEGIN PRIVATE KEY-----\n' + '\n'.join(chunks) + '\n-----END PRIVATE KEY-----'
        return formatted_key
    
    # If we got here, it's not a standard format - try to extract any base64 content
    # and reformat it properly
    try:
        # Try to find any base64-like content
        base64_pattern = re.compile(r'[A-Za-z0-9+/=]{20,}')  # Look for base64 characters
        match = base64_pattern.search(private_key)
        if match:
            base64_content = match.group(0)
            chunks = [base64_content[i:i+64] for i in range(0, len(base64_content), 64)]
            return '-----BEGIN PRIVATE KEY-----\n' + '\n'.join(chunks) + '\n-----END PRIVATE KEY-----'
    except Exception as e:
        print(f"Error reformatting private key: {e}")
    
    # If all else fails, return the original key
    return private_key

# Path to the Firebase service account key file
# For production, store this securely and reference via environment variables
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": os.environ.get('FIREBASE_PROJECT_ID', ''),
    "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID', ''),
    "private_key": format_private_key(os.environ.get('FIREBASE_PRIVATE_KEY', '')),
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
            # Verify that we have the minimum required credentials
            if not FIREBASE_CONFIG['project_id'] or not FIREBASE_CONFIG['client_email']:
                print("Missing required Firebase credentials: project_id or client_email")
                return None
                
            # Log private key format for debugging (first 10 chars and last 10 chars)
            if FIREBASE_CONFIG['private_key']:
                key_length = len(FIREBASE_CONFIG['private_key'])
                print(f"Private key format: {FIREBASE_CONFIG['private_key'][:10]}...{FIREBASE_CONFIG['private_key'][-10:]} (length: {key_length})")
            else:
                print("WARNING: Firebase private key is empty")
            
            # First attempt: Try direct initialization with the config dictionary
            try:
                cred = credentials.Certificate(FIREBASE_CONFIG)
                app = firebase_admin.initialize_app(cred)
                print(f"Initialized Firebase with project ID: {FIREBASE_CONFIG['project_id']}")
                return app
            except Exception as e:
                print(f"First initialization attempt failed: {str(e)}")
                # Continue to alternative method
            
            # Alternative method: Create a temporary service account file
            # This is more reliable for Vercel deployment
            import json
            import tempfile
            
            # Create a temporary file with the Firebase config
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                json.dump(FIREBASE_CONFIG, temp_file)
                temp_file_path = temp_file.name
            
            try:
                # Initialize with the temporary file
                cred = credentials.Certificate(temp_file_path)
                app = firebase_admin.initialize_app(cred)
                print(f"Initialized Firebase with temporary file and project ID: {FIREBASE_CONFIG['project_id']}")
                
                # Clean up the temporary file
                import os
                os.unlink(temp_file_path)
                
                return app
            except Exception as e:
                print(f"Second initialization attempt failed: {str(e)}")
                # Clean up the temporary file
                import os
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                raise
        except Exception as e:
            print(f"Error initializing Firebase: {str(e)}")
            # Print more detailed error information
            import traceback
            traceback.print_exc()
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
