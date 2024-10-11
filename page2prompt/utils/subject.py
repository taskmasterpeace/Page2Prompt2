class Subject:
    def __init__(self, name, description, type, prefix="", suffix="", alias=None):
        self.name = name
        self.description = description
        self.type = type
        self.prefix = prefix
        self.suffix = suffix
        self.alias = alias if alias else name  # Use name as alias if not provided

    def __repr__(self):
        return f"Subject(name='{self.name}', alias='{self.alias}', type='{self.type}')"
