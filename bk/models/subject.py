from typing import Optional

class Subject:
    def __init__(
        self,
        name: str,
        description: str,
        alias: str,
        type: str,
        prefix: Optional[str] = "",
        suffix: Optional[str] = "",
        active: bool = True
    ):
        self.name = name
        self.description = description
        self.alias = alias
        self.type = type
        self.prefix = prefix
        self.suffix = suffix
        self.active = active

    def to_dict(self):
        return {
            "Name": self.name,
            "Description": self.description,
            "Alias": self.alias,
            "Type": self.type,
            "Prefix": self.prefix,
            "Suffix": self.suffix,
            "Active": self.active
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["Name"],
            description=data["Description"],
            alias=data["Alias"],
            type=data["Type"],
            prefix=data.get("Prefix", ""),
            suffix=data.get("Suffix", ""),
            active=data.get("Active", True)
        )
class Subject:
    def __init__(
        self,
        name: str,
        description: str,
        alias: str,
        type: str,
        prefix: str = "",
        suffix: str = "",
        active: bool = True
    ):
        self.name = name
        self.description = description
        self.alias = alias
        self.type = type
        self.prefix = prefix
        self.suffix = suffix
        self.active = active

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "alias": self.alias,
            "type": self.type,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "active": self.active
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            description=data["description"],
            alias=data["alias"],
            type=data["type"],
            prefix=data.get("prefix", ""),
            suffix=data.get("suffix", ""),
            active=data.get("active", True)
        )
