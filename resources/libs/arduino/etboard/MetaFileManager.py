import json
from typing import Any, Dict, List
import os

class FileMetaManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self._read_file()

    def _read_file(self) -> Dict[str, Any]:
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _write_file(self):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def read(self) -> Dict[str, Any]:
        return self.data

    def create(self, section: str, entry: Dict[str, Any]):
        if section in self.data:
            self.data[section].append(entry)
        else:
            self.data[section] = [entry]
        self._write_file()

    def update(self, section: str, entry_name: str, updated_entry: Dict[str, Any]):
        if section in self.data:
            for entry in self.data[section]:
                if entry.get('name') == entry_name:
                    entry.update(updated_entry)
                    self._write_file()
                    return
            # If entry_name is not found, create a new entry
            self.create(section, updated_entry)
        else:
            # If section does not exist, create it and add the entry
            self.create(section, updated_entry)

    def delete(self, section: str, entry_name: str):
        if section in self.data:
            self.data[section] = [entry for entry in self.data[section] if entry.get('name') != entry_name]
            self._write_file()
        else:
            raise ValueError(f"Section {section} not found")

    # CRUD methods for 'body' section
    def read_body(self) -> Dict[str, Dict[str, Any]]:
        return {item['name']: item for item in self.data.get('body', [])}

    def create_body_entry(self, entry: Dict[str, Any]):
        if 'body' not in self.data:
            self.data['body'] = []
        self.data['body'].append(entry)
        self._write_file()

    def update_body_entry(self, entry_name: str, updated_entry: Dict[str, Any]):
        if 'body' in self.data:
            for entry in self.data['body']:
                if entry.get('name') == entry_name:
                    entry.update(updated_entry)
                    self._write_file()
                    return
            # If entry_name is not found, create a new entry
            self.create_body_entry(updated_entry)
        else:
            # If body section does not exist, create it and add the entry
            self.create_body_entry(updated_entry)

    def delete_body_entry(self, entry_name: str):
        if 'body' in self.data:
            self.data['body'] = [entry for entry in self.data['body'] if entry.get('name') != entry_name]
            self._write_file()
        else:
            raise ValueError(f"Body section not found")

# Usage example:
# manager = FileMetaManager('_file_meta.json')
# manager.create('body', {"name": "NewEntry", "created_at": "2024_08_10__10_00_00", "ignore": False})
# manager.update('body', 'ET_BluetoothSerial', {"ignore": True})
# manager.delete('body', 'ET_BluetoothSerial')

def get_folders_in_directory(directory: str) -> List[str]:
    folders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            folders.append(item)
    return folders


manager = FileMetaManager('_file_meta.json')

# Example usage:
directory = './'
folders = get_folders_in_directory(directory)
print(folders)

for folder in folders:
    manager.create('body', {"name": folder, "created_at": "2024_08_10__10_00_00", "ignore": False})
    #manager.update('body', folder, {"ignore": True})
