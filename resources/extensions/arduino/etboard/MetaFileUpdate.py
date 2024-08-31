import os

from FileMetaManager import *

file_meta_manager = FileMetaManager('_file_meta.json')


# 현재 스크립트가 저장된 디렉토리
root_dir = os.path.dirname(os.path.abspath(__file__))

def find_created_folders(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name.startswith("00._created"):
                # 경로 분할
                path_parts = root.split(os.sep)
                main_folder = path_parts[-2] if len(path_parts) > 1 else ''
                #print(f"{main_folder}, {dir_name}")
                file_meta_manager.update('body', main_folder, {"created_at": dir_name})

if __name__ == "__main__":
    file_meta_manager.clear_body()
    find_created_folders(root_dir)
    file_meta_manager.update('header', 'updated_at', get_current_datetime())
