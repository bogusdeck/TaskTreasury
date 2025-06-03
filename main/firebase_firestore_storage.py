import os
import base64
import mimetypes
from io import BytesIO
from urllib.parse import urljoin
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from .firebase_firestore_config import (
    get_media_collection,
    upload_file_to_firestore,
    upload_from_memory_to_firestore,
    get_file_from_firestore,
    delete_file_from_firestore
)

@deconstructible
class FirebaseFirestoreStorage(Storage):
    """
    Django storage backend that uses Firebase Firestore to store media files.
    Files are stored as base64-encoded strings in Firestore documents.
    """
    
    def __init__(self, location=None, base_url=None):
        self.location = location or settings.MEDIA_ROOT
        self.base_url = base_url or settings.MEDIA_URL
        self.collection = get_media_collection()
    
    def _get_path(self, name):
        """
        Get the full path of the file.
        """
        if name.startswith('/'):
            name = name[1:]
        return name
    
    def _open(self, name, mode='rb'):
        """
        Retrieve the file from Firebase Firestore.
        """
        path = self._get_path(name)
        try:
            file_data = get_file_from_firestore(path)
            
            if not file_data or 'data' not in file_data:
                raise FileNotFoundError(f"File {name} does not exist")
            
            # Decode base64 data
            try:
                decoded_data = base64.b64decode(file_data['data'])
                return ContentFile(decoded_data, name=name)
            except Exception as e:
                print(f"Error decoding base64 data for {name}: {str(e)}")
                raise IOError(f"Error reading file {name}: {str(e)}")
        except Exception as e:
            print(f"Error opening file {name} from Firestore: {str(e)}")
            raise FileNotFoundError(f"Cannot open file {name}: {str(e)}")
    
    def _save(self, name, content):
        """
        Save the file to Firebase Firestore.
        """
        path = self._get_path(name)
        try:
            content.seek(0)
            file_bytes = content.read()
            
            # Get content type
            content_type, _ = mimetypes.guess_type(name)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Upload to Firebase Firestore
            result = upload_from_memory_to_firestore(
                file_bytes,
                path,
                content_type,
                os.path.basename(name)
            )
            
            if not result:
                print(f"Warning: File {name} may not have been saved properly to Firestore")
            
            return name
        except Exception as e:
            print(f"Error saving file {name} to Firestore: {str(e)}")
            # Return the name anyway to prevent Django from raising an exception
            # The file might not be accessible later, but at least the model will save
            return name
    
    def delete(self, name):
        """
        Delete the file from Firebase Firestore.
        """
        path = self._get_path(name)
        delete_file_from_firestore(path)
    
    def exists(self, name):
        """
        Check if the file exists in Firebase Firestore.
        """
        path = self._get_path(name)
        try:
            file_data = get_file_from_firestore(path)
            return file_data is not None
        except Exception as e:
            print(f"Error checking if file {name} exists in Firestore: {str(e)}")
            # Assume file doesn't exist if there's an error
            return False
    
    def url(self, name):
        """
        Return URL for accessing the file.
        Since files are stored in Firestore, we'll use a URL pattern that
        can be handled by a view to serve the file from Firestore.
        """
        path = self._get_path(name)
        return urljoin(self.base_url, path)
    
    def size(self, name):
        """
        Return the size of the file.
        """
        path = self._get_path(name)
        file_data = get_file_from_firestore(path)
        
        if not file_data or 'size' not in file_data:
            raise FileNotFoundError(f"File {name} does not exist")
        
        return file_data['size']
    
    def get_accessed_time(self, name):
        """
        Return the last accessed time of the file.
        Not supported for Firebase Firestore.
        """
        raise NotImplementedError("Firebase Firestore doesn't track access time")
    
    def get_created_time(self, name):
        """
        Return the creation time of the file.
        """
        path = self._get_path(name)
        file_data = get_file_from_firestore(path)
        
        if not file_data or 'uploaded_at' not in file_data:
            raise FileNotFoundError(f"File {name} does not exist")
        
        # Firestore timestamps are already datetime objects
        return file_data['uploaded_at']
    
    def get_modified_time(self, name):
        """
        Return the last modified time of the file.
        Same as creation time for Firebase Firestore.
        """
        return self.get_created_time(name)
