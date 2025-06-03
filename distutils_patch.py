"""
A patch module to provide the missing distutils functionality.
This will be imported by the wsgi.py file before Django is loaded.
"""

# Create a version module with LooseVersion
class LooseVersion:
    """
    A simplified version of distutils.version.LooseVersion that Django uses.
    """
    def __init__(self, vstring=None):
        self.parse(vstring)
        
    def parse(self, vstring):
        if vstring is None:
            self.vstring = ""
        else:
            self.vstring = str(vstring)
            
        components = []
        for component in self.vstring.split('.'):
            try:
                components.append(int(component))
            except ValueError:
                components.append(component)
        self.version = components
        
    def __str__(self):
        return self.vstring
        
    def __repr__(self):
        return f"LooseVersion('{self.vstring}')"
        
    def __eq__(self, other):
        if isinstance(other, str):
            other = LooseVersion(other)
        return self.version == other.version
        
    def __lt__(self, other):
        if isinstance(other, str):
            other = LooseVersion(other)
        
        # Compare version components
        for i, component in enumerate(self.version):
            if i >= len(other.version):
                # If self has more components and all previous components were equal, self is greater
                return False
                
            # If components are different types (str vs int), convert to str for comparison
            if type(component) != type(other.version[i]):
                if component < str(other.version[i]):
                    return True
                elif component > str(other.version[i]):
                    return False
            else:
                if component < other.version[i]:
                    return True
                elif component > other.version[i]:
                    return False
                    
        # If we get here and other has more components, self is less
        return len(self.version) < len(other.version)
        
    def __gt__(self, other):
        if isinstance(other, str):
            other = LooseVersion(other)
        return not (self < other or self == other)
        
    def __le__(self, other):
        if isinstance(other, str):
            other = LooseVersion(other)
        return self < other or self == other
        
    def __ge__(self, other):
        if isinstance(other, str):
            other = LooseVersion(other)
        return self > other or self == other
