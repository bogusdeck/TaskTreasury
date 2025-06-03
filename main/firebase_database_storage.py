import os
import base64
import mimetypes
from io import BytesIO
from urllib.parse import urljoin
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from .firebase_config import (
    get_database_ref,
    upload_file_to_database,
    upload_from_memory_to_database,
    get_file_from_database,
    delete_file_from_database
)

@deconstructible
class FirebaseDatabaseStorage(Storage):
    """
    Django storage backend that uses Firebase Realtime Database to store media files.
    Files are stored as base64-encoded strings in the database.
    """
    
    def __init__(self, location=None, base_url=None):
        self.location = location or settings.MEDIA_ROOT
        self.base_url = base_url or settings.MEDIA_URL
        self.db_ref = get_database_ref()
    
    def _get_path(self, name):
        """
        Get the full path of the file.
        """
        if name.startswith('/'):
            name = name[1:]
        return name
    
    def _open(self, name, mode='rb'):
        """
        Retrieve the file from Firebase Realtime Database.
        """
        path = self._get_path(name)
        file_data = get_file_from_database(path)
        
        if not file_data or 'data' not in file_data:
            raise FileNotFoundError(f"File {name} does not exist")
        
        # Decode base64 data
        decoded_data = base64.b64decode(file_data['data'])
        return ContentFile(decoded_data, name=name)
    
    def _save(self, name, content):
        """
        Save the file to Firebase Realtime Database.
        """
        path = self._get_path(name)
        content.seek(0)
        file_bytes = content.read()
        
        # Get content type
        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Upload to Firebase Realtime Database
        upload_from_memory_to_database(
            file_bytes,
            path,
            content_type,
            os.path.basename(name)
        )
        
        return name
    
    def delete(self, name):
        """
        Delete the file from Firebase Realtime Database.
        """
        path = self._get_path(name)
        delete_file_from_database(path)
    
    def exists(self, name):
        """
        Check if the file exists in Firebase Realtime Database.
        """
        path = self._get_path(name)
        file_data = get_file_from_database(path)
        return file_data is not None
    
    def url(self, name):
        """
        Return URL for accessing the file.
        Since files are stored in the database, we'll use a URL pattern that
        can be handled by a view to serve the file from the database.
        """
        path = self._get_path(name)
        return urljoin(self.base_url, path)
    
    def size(self, name):
        """
        Return the size of the file.
        """
        path = self._get_path(name)
        file_data = get_file_from_database(path)
        
        if not file_data or 'size' not in file_data:
            raise FileNotFoundError(f"File {name} does not exist")
        
        return file_data['size']
    
    def get_accessed_time(self, name):
        """
        Return the last accessed time of the file.
        Not supported for Firebase Realtime Database.
        """
        raise NotImplementedError("Firebase Realtime Database doesn't track access time")
    
    def get_created_time(self, name):
        """
        Return the creation time of the file.
        """
        path = self._get_path(name)
        file_data = get_file_from_database(path)
        
        if not file_data or 'uploaded_at' not in file_data:
            raise FileNotFoundError(f"File {name} does not exist")
        
        # Firebase timestamps are in milliseconds
        timestamp = file_data['uploaded_at'] / 1000
        from datetime import datetime
        return datetime.fromtimestamp(timestamp)
    
    def get_modified_time(self, name):
        """
        Return the last modified time of the file.
        Same as creation time for Firebase Realtime Database.
        """
        return self.get_created_time(name)
