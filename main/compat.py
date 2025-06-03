"""
Compatibility module to handle missing distutils in Python 3.9+ environments.
"""

class LooseVersion:
    """
    Simple implementation of LooseVersion to avoid distutils dependency.
    """
    def __init__(self, version_string):
        self.version_string = version_string
        
        # Split version string into components
        components = []
        for part in self.version_string.split('.'):
            try:
                components.append(int(part))
            except ValueError:
                components.append(part)
        self.components = components
    
    def __str__(self):
        return self.version_string
    
    def __repr__(self):
        return f"LooseVersion('{self.version_string}')"
    
    def __eq__(self, other):
        if isinstance(other, str):
            other = LooseVersion(other)
        return self.components == other.components
    
    def __lt__(self, other):
        if isinstance(other, str):
            other = LooseVersion(other)
        
        for i, component in enumerate(self.components):
            if i >= len(other.components):
                # If we've reached the end of other's components, self is longer
                # and therefore greater unless all remaining components are 0
                return False
            
            # Compare components
            if component == other.components[i]:
                continue
            
            # Handle different types (int vs str)
            if isinstance(component, int) and isinstance(other.components[i], str):
                return True  # Numbers come before strings
            if isinstance(component, str) and isinstance(other.components[i], int):
                return False  # Strings come after numbers
            
            # Same types, can compare directly
            return component < other.components[i]
        
        # If we've exhausted self's components but other has more,
        # self is less than other unless all remaining components are 0
        return len(self.components) < len(other.components)
