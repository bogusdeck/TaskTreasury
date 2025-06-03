import os
import mimetypes
from io import BytesIO
from urllib.parse import urljoin
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from .firebase_config import upload_from_memory, delete_file

@deconstructible
class FirebaseStorage(Storage):
    """
    Custom storage backend for Django that uses Firebase Storage
    """
    def __init__(self, location=None, base_url=None):
        self.location = location or ''
        self.base_url = base_url or ''

    def _get_full_path(self, name):
        """
        Get the full path including location
        """
        if self.location:
            return os.path.join(self.location, name)
        return name

    def _open(self, name, mode='rb'):
        """
        Not implemented for Firebase Storage
        """
        raise NotImplementedError("Firebase Storage backend doesn't support opening files")

    def _save(self, name, content):
        """
        Save the file to Firebase Storage
        """
        full_path = self._get_full_path(name)
        content_type, _ = mimetypes.guess_type(name)
        
        # Read the content into memory
        content.seek(0)
        file_bytes = content.read()
        
        # Upload to Firebase
        upload_from_memory(file_bytes, full_path, content_type or 'application/octet-stream')
        
        return name

    def delete(self, name):
        """
        Delete the file from Firebase Storage
        """
        full_path = self._get_full_path(name)
        delete_file(full_path)

    def exists(self, name):
        """
        Always return False to force save
        """
        return False

    def url(self, name):
        """
        Return the URL of the file in Firebase Storage
        """
        full_path = self._get_full_path(name)
        project_id = os.environ.get("FIREBASE_PROJECT_ID", "")
        
        # Construct the Firebase Storage URL
        firebase_url = f"https://storage.googleapis.com/{project_id}.appspot.com/{full_path}"
        
        return firebase_url

    def size(self, name):
        """
        Not implemented for Firebase Storage
        """
        raise NotImplementedError("Firebase Storage backend doesn't support size")

    def get_accessed_time(self, name):
        """
        Not implemented for Firebase Storage
        """
        raise NotImplementedError("Firebase Storage backend doesn't support get_accessed_time")

    def get_created_time(self, name):
        """
        Not implemented for Firebase Storage
        """
        raise NotImplementedError("Firebase Storage backend doesn't support get_created_time")

    def get_modified_time(self, name):
        """
        Not implemented for Firebase Storage
        """
        raise NotImplementedError("Firebase Storage backend doesn't support get_modified_time")
