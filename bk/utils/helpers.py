import csv
import json
import os
from typing import List, Dict, Any

def read_csv_file(file_path: str) -> List[Dict[str, str]]:
    """Read a CSV file and return its contents as a list of dictionaries."""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def write_csv_file(file_path: str, data: List[Dict[str, Any]], fieldnames: List[str]):
    """Write a list of dictionaries to a CSV file."""
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read a JSON file and return its contents as a dictionary."""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

def write_json_file(file_path: str, data: Dict[str, Any]):
    """Write a dictionary to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2)
