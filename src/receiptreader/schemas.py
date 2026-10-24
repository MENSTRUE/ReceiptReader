from dataclasses import dataclass, asdict

@dataclass
class ReceiptFields:
    company: str = ''
    date: str = ''
    address: str = ''
    total: str = ''
    def to_dict(self):
        return asdict(self)
