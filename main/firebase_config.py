import os
import base64
import firebase_admin
from firebase_admin import credentials, storage, db
import mimetypes

FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID", ""),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL", ""),
    "client_id": os.environ.get("FIREBASE_CLIENT_ID", ""),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_CERT_URL", ""),
    "universe_domain": "googleapis.com"
}

def initialize_firebase(use_database=False):
    try:
        app = firebase_admin.get_app()
        return app
    except ValueError:
        cred = credentials.Certificate(FIREBASE_CONFIG)

        if use_database:
            database_url = f"https://{FIREBASE_CONFIG['project_id']}-default-rtdb.firebaseio.com"
            app = firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            print(f"Initialized Firebase with Realtime Database: {database_url}")
        else:
            app = firebase_admin.initialize_app(cred)
            print(f"Initialized Firebase with project ID: {FIREBASE_CONFIG['project_id']}")
        
        return app

def get_database_ref(path='media'):
    initialize_firebase(use_database=True)
    try:
        ref = db.reference(path)
        return ref
    except Exception as e:
        print(f"Error getting database reference: {str(e)}")
        return None

def get_bucket(custom_bucket=None):
    initialize_firebase()
    try:
        bucket = storage.bucket()
        return bucket
    except Exception as e:
        print(f"Error getting bucket: {str(e)}")
        return None

def upload_file_to_database(file_path, destination_path):
    ref = get_database_ref()
    if not ref:
        return None
    
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        encoded_data = base64.b64encode(file_data).decode('utf-8')
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'content_type': mime_type,
            'size': len(file_data),
            'data': encoded_data,
            'uploaded_at': {'.sv': 'timestamp'}
        }
        
        safe_path = destination_path.replace('.', '_dot_')
        safe_path = safe_path.replace('$', '_dollar_')
        safe_path = safe_path.replace('#', '_hash_')
        safe_path = safe_path.replace('[', '_lbracket_')
        safe_path = safe_path.replace(']', '_rbracket_')
        safe_path = safe_path.replace('/', '_slash_')
        
        file_ref = ref.child(safe_path)
        file_ref.set(file_metadata)
        
        return f"/media/{destination_path}"
    except Exception as e:
        print(f"Error uploading file to database: {str(e)}")
        return None

def upload_from_memory_to_database(file_bytes, destination_path, content_type, filename):
    ref = get_database_ref()
    if not ref:
        return None
    
    try:
        encoded_data = base64.b64encode(file_bytes).decode('utf-8')
        
        file_metadata = {
            'name': filename,
            'content_type': content_type,
            'size': len(file_bytes),
            'data': encoded_data,
            'uploaded_at': {'.sv': 'timestamp'}
        }
        
        safe_path = destination_path.replace('.', '_dot_')
        safe_path = safe_path.replace('$', '_dollar_')
        safe_path = safe_path.replace('#', '_hash_')
        safe_path = safe_path.replace('[', '_lbracket_')
        safe_path = safe_path.replace(']', '_rbracket_')
        safe_path = safe_path.replace('/', '_slash_')
        
        file_ref = ref.child(safe_path)
        file_ref.set(file_metadata)
        
        return f"/media/{destination_path}"
    except Exception as e:
        print(f"Error uploading file to database: {str(e)}")
        return None

def get_file_from_database(file_path):
    ref = get_database_ref()
    if not ref:
        return None
    
    try:
        safe_path = file_path.replace('.', '_dot_')
        safe_path = safe_path.replace('$', '_dollar_')
        safe_path = safe_path.replace('#', '_hash_')
        safe_path = safe_path.replace('[', '_lbracket_')
        safe_path = safe_path.replace(']', '_rbracket_')
        safe_path = safe_path.replace('/', '_slash_')
        
        file_ref = ref.child(safe_path)
        file_data = file_ref.get()
        
        if not file_data:
            return None
        
        return file_data
    except Exception as e:
        print(f"Error getting file from database: {str(e)}")
        return None

def delete_file_from_database(file_path):
    ref = get_database_ref()
    if not ref:
        return False
    
    try:
        safe_path = file_path.replace('.', '_dot_')
        safe_path = safe_path.replace('$', '_dollar_')
        safe_path = safe_path.replace('#', '_hash_')
        safe_path = safe_path.replace('[', '_lbracket_')
        safe_path = safe_path.replace(']', '_rbracket_')
        safe_path = safe_path.replace('/', '_slash_')
        
        file_ref = ref.child(safe_path)
        file_ref.delete()
        return True
    except Exception as e:
        print(f"Error deleting file from database: {str(e)}")
        return False

def upload_file(file_path, destination_blob_name):
    return upload_file_to_database(file_path, destination_blob_name)

def upload_from_memory(file_bytes, destination_blob_name, content_type):
    filename = os.path.basename(destination_blob_name)
    return upload_from_memory_to_database(file_bytes, destination_blob_name, content_type, filename)

def delete_file(blob_name):
    return delete_file_from_database(blob_name)

def get_firebase_database_ref(path='media'):
    return get_database_ref(path)

def upload_file_to_firebase_database(file_path, destination_path):
    return upload_file_to_database(file_path, destination_path)

def get_firebase_storage_bucket(custom_bucket=None):
    print("Warning: Using Firebase Realtime Database instead of Storage")
    return get_database_ref()

def upload_file_to_firebase(file_path, destination_blob_name, custom_bucket=None):
    print("Using Firebase Realtime Database instead of Storage")
    return upload_file_to_database(file_path, destination_blob_name)
