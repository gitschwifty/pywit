import json

def get_amount_json(self, str):
    return Amount(str).json()

def get_float_amount(self, amt: dict):
    return Amount(amt).amount

def print_json(self, jsdict):
    print(json.dumps(jsdict, indent=4))
