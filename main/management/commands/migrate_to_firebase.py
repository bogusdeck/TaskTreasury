import os
import django
import mimetypes
from django.core.management.base import BaseCommand
from django.conf import settings
from main.firebase_firestore_config import get_media_collection, upload_file_to_firestore

class Command(BaseCommand):
    help = 'Migrate files from local storage to Firebase Firestore'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            default='applogo',
            help='Directory within MEDIA_ROOT to migrate files from (default: applogo)'
        )
        parser.add_argument(
            '--destination-dir',
            default='applogo',
            help='Directory in Firebase Firestore to migrate files to (default: applogo)'
        )
        parser.add_argument(
            '--delete-local',
            action='store_true',
            help='Delete local files after successful migration'
        )
        parser.add_argument(
            '--bucket',
            help='Override Firebase Storage bucket name'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually uploading files'
        )

    def handle(self, *args, **options):
        source_dir = options['source_dir']
        destination_dir = options['destination_dir']
        delete_local = options['delete_local']
        bucket_override = options.get('bucket')
        dry_run = options.get('dry_run', False)
        
        # Set bucket name in environment if provided
        if bucket_override:
            os.environ['FIREBASE_STORAGE_BUCKET'] = bucket_override
            self.stdout.write(f"Using custom bucket name: {bucket_override}")
        
        # Get the full path to the source directory
        source_path = os.path.join(settings.MEDIA_ROOT, source_dir)
        
        if not os.path.exists(source_path):
            self.stdout.write(self.style.ERROR(f'Source directory {source_path} does not exist'))
            return
            
        # Get list of files in the source directory
        files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
        
        if not files:
            self.stdout.write(self.style.WARNING(f'No files found in {source_path}'))
            return
            
        self.stdout.write(f'Found {len(files)} files to migrate')
        
        # Get Firebase Firestore collection reference
        if not dry_run:
            collection_ref = get_media_collection()
            if not collection_ref:
                self.stdout.write(self.style.ERROR('Failed to get Firebase Firestore collection reference'))
                self.stdout.write(self.style.WARNING('Check your Firebase credentials and Firestore configuration'))
                self.stdout.write(self.style.WARNING('Make sure Firestore is enabled and the service account has access to it'))
                return
        else:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No files will be uploaded'))
            
        # Migrate each file
        success_count = 0
        for filename in files:
            file_path = os.path.join(source_path, filename)
            firebase_path = f"{destination_dir}/{filename}"
            
            self.stdout.write(f'Migrating {filename} to Firebase Firestore...')
            
            try:
                if not dry_run:
                    # Get file mime type
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if not mime_type:
                        mime_type = 'application/octet-stream'
                    
                    # Upload to Firebase Firestore
                    media_url = upload_file_to_firestore(file_path, firebase_path)
                    
                    if media_url:
                        self.stdout.write(self.style.SUCCESS(f'Successfully uploaded {filename} to Firebase Firestore'))
                        self.stdout.write(f'Media URL: {media_url}')
                        success_count += 1
                        
                        # Delete local file if requested
                        if delete_local:
                            os.remove(file_path)
                            self.stdout.write(f'Deleted local file {file_path}')
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to upload {filename} to Firebase Firestore'))
                else:
                    # Dry run - just log what would happen
                    self.stdout.write(f'[DRY RUN] Would upload {filename} to Firebase Firestore at path: {firebase_path}')
                    success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error migrating {filename}: {str(e)}'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'Migration complete. {success_count} of {len(files)} files migrated successfully.'))
        if delete_local and success_count == len(files):
            self.stdout.write(self.style.SUCCESS(f'All files have been deleted from local storage.'))
