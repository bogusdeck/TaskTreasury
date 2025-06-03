"""
Patch script to modify Django's version.py file to avoid distutils dependency.
This script should be run before Django is imported.
"""
import os
import sys
import re

def patch_django_version():
    """
    Find and patch Django's version.py file to use our custom LooseVersion.
    """
    # Find Django's version.py file in site-packages
    django_path = None
    for path in sys.path:
        version_path = os.path.join(path, 'django', 'utils', 'version.py')
        if os.path.exists(version_path):
            django_path = version_path
            break
    
    if not django_path:
        print("Could not find Django's version.py file")
        return False
    
    # Read the file
    with open(django_path, 'r') as f:
        content = f.read()
    
    # Check if it imports distutils
    if 'from distutils.version import LooseVersion' in content:
        # Replace with our custom import
        new_content = content.replace(
            'from distutils.version import LooseVersion',
            'from main.compat import LooseVersion'
        )
        
        # Write the modified file
        with open(django_path, 'w') as f:
            f.write(new_content)
        
        print(f"Successfully patched {django_path}")
        return True
    
    print("File does not import distutils.version.LooseVersion")
    return False

if __name__ == "__main__":
    patch_django_version()
