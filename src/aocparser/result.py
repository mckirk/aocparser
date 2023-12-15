class NamespaceDict(dict):
    """A dictionary that allows access to its keys as attributes."""
    def __getattr__(self, key):
        return self[key]
    
    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]
