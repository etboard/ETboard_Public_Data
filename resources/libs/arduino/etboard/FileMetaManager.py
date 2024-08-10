import json
import os

class FileMetaHeader:
    def __init__(self, filename="", content="", description="", author="", created_at="", updated_at=""):
        self.filename = filename
        self.content = content
        self.description = description
        self.author = author
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "filename": self.filename,
            "content": self.content,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class FileMetaBodyEntry:
    def __init__(self, created_at="", ignore=False):
        self.created_at = created_at
        self.ignore = ignore

    def to_dict(self):
        return {
            "created_at": self.created_at,
            "ignore": self.ignore
        }

class FileMetaBody:
    def __init__(self):
        self.entries = {}

    def add_entry(self, key, entry):
        if isinstance(entry, FileMetaBodyEntry):
            self.entries[key] = entry

    def update_entry(self, key, created_at=None, ignore=None):
        if key not in self.entries:
            print(f"Warning: Key '{key}' not found in 'body'. Creating key '{key}'.")
            self.entries[key] = FileMetaBodyEntry()
        if created_at is not None:
            self.entries[key].created_at = created_at
        if ignore is not None:
            self.entries[key].ignore = ignore

    def to_dict(self):
        return {key: entry.to_dict() for key, entry in self.entries.items()}

class FileMetaManager:
    def __init__(self, file_name):
        self.file_path = os.path.join(os.path.dirname(__file__), file_name)
        self.header = None
        self.body = FileMetaBody()
        self._load_file()

    def _load_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                header_data = data[0].get("header", {})
                self.header = FileMetaHeader(
                    header_data.get("filename", ""),
                    header_data.get("content", ""),
                    header_data.get("description", ""),
                    header_data.get("author", ""),
                    header_data.get("created_at", ""),
                    header_data.get("updated_at", "")
                )
                body_data = data[1].get("body", {})
                for key, value in body_data.items():
                    self.body.add_entry(key, FileMetaBodyEntry(value["created_at"], value["ignore"]))
        else:
            self.header = FileMetaHeader()

    def _save_file(self):
        data = [
            {"header": self.header.to_dict()},
            {"body": self.body.to_dict()}
        ]
        print("Saving data:", data)  # 디버깅 출력 추가
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"File saved to {self.file_path}")  # 디버깅 출력 추가

    def read(self):
        return {
            "header": self.header.to_dict(),
            "body": self.body.to_dict()
        }

    def create(self, section, obj):
        if section == 'header' and isinstance(obj, FileMetaHeader):
            self.header = obj
        elif section == 'body' and isinstance(obj, FileMetaBody):
            self.body = obj
        self._save_file()

    def update(self, section, key, value):
        if section == 'header':
            if not hasattr(self.header, key):
                print(f"Warning: 'header' key '{key}' not found. Creating key '{key}'.")
            setattr(self.header, key, value)
        elif section == 'body':
            self.body.update_entry(key, value.get("created_at"), value.get("ignore"))
        self._save_file()

    def delete(self, section, key):
        if section == 'header':
            if hasattr(self.header, key):
                setattr(self.header, key, None)
        elif section == 'body':
            if key in self.body.entries:
                del self.body.entries[key]
        self._save_file()

# Usage example
file_meta_manager = FileMetaManager('_file_meta.json')

# Create a new header entry using the FileMetaHeader class
new_header = FileMetaHeader(
    filename="_file_meta.json",
    content="라이브러리 버전 관리 메타 파일",
    description="라이브러리 버전 관리를 위한 메타 파일입니다.",
    author="손철수",
    created_at="2024-08-09",
    updated_at="2024-08-11"
)
file_meta_manager.create('header', new_header)

# Create a new body entry using the FileMetaBodyEntry class
new_body_entry = FileMetaBodyEntry(
    created_at="2024_08_04__22_18_35",
    ignore=False
)
file_meta_manager.body.add_entry('ET_BluetoothSerial3', new_body_entry)
file_meta_manager._save_file()

# Read the current state of the JSON data
print(file_meta_manager.read())

# Update the 'author' field in the header
file_meta_manager.update('header', 'author', '손철수(cheolsu.son@gmail.com)')

# Update the 'ignore' field for 'ET_BluetoothSerial1' in the body
file_meta_manager.update('body', 'ET_BluetoothSerial1', {"ignore": True})

# Read the updated state of the JSON data
print(file_meta_manager.read())