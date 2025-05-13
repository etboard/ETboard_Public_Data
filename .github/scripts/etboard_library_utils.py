#!/usr/bin/env python3
# .github/scripts/etboard_library_utils.py

import json
import os
import sys
import zipfile
import shutil
import glob
from pathlib import Path

def extract_versions(etboard_meta_path, original_meta_path):
    """
    etboard와 original 라이브러리의 버전 정보를 추출하는 함수
    """
    versions = {}
    
    # ETboard 아두이노 라이브러리 버전 정보
    if os.path.exists(etboard_meta_path):
        try:
            with open(etboard_meta_path, 'r') as f:
                data = json.load(f)
                # 데이터가 딕셔너리인지 확인
                if isinstance(data, dict):
                    for lib, info in data.items():
                        if isinstance(info, dict) and 'version' in info:
                            versions[lib] = info['version']
                # 리스트인 경우 처리
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'name' in item and 'version' in item:
                            versions[item['name']] = item['version']
        except Exception as e:
            print(f"Error reading {etboard_meta_path}: {e}")
    
    # Original 아두이노 라이브러리 버전 정보
    if os.path.exists(original_meta_path):
        try:
            with open(original_meta_path, 'r') as f:
                data = json.load(f)
                # 데이터가 딕셔너리인지 확인
                if isinstance(data, dict):
                    for lib, info in data.items():
                        if isinstance(info, dict) and 'version' in info:
                            versions[lib] = info['version']
                # 리스트인 경우 처리
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'name' in item and 'version' in item:
                            versions[item['name']] = item['version']
        except Exception as e:
            print(f"Error reading {original_meta_path}: {e}")
    
    # 버전 정보가 없는 경우 기본값 설정
    if not versions:
        print("No version information found. Using default values.")
        versions["ETboard_Libraries"] = "latest"
    
    return versions

def process_library(lib_dir, bundle_dir, extract_dir, debug=False):
    """
    단일 라이브러리 디렉토리를 처리하는 함수
    """
    # 불필요한 파일/폴더 패턴
    exclude_patterns = [
        "_file_meta.json",
        "MetaFileUpdate.py", 
        "FileMetaManager.py"
    ]
    
    # 라이브러리 이름 추출
    lib_name = os.path.basename(lib_dir)
    
    # 제외 패턴 확인
    for pattern in exclude_patterns:
        if pattern in lib_name:
            if debug:
                print(f"Skipping excluded item: {lib_name}")
            return
    
    if debug:
        print(f"Processing library: {lib_name}")
    
    # ZIP 파일 검색
    zip_files = []
    for root, dirs, files in os.walk(lib_dir):
        for file in files:
            if file.endswith('.zip'):
                zip_files.append(os.path.join(root, file))
    
    if zip_files:
        # ZIP 파일이 있는 경우
        for zip_file in zip_files:
            zip_name = os.path.splitext(os.path.basename(zip_file))[0]
            if debug:
                print(f"  Found ZIP: {zip_file}, name: {zip_name}")
            
            # ZIP 파일 추출
            extract_subdir = os.path.join(extract_dir, zip_name)
            if os.path.exists(extract_subdir):
                shutil.rmtree(extract_subdir)
            os.makedirs(extract_subdir, exist_ok=True)
            
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_subdir)
                
                # 라이브러리와 동일한 이름의 폴더 확인
                matching_folder = os.path.join(extract_subdir, zip_name)
                if os.path.exists(matching_folder) and os.path.isdir(matching_folder):
                    if debug:
                        print(f"  Found matching folder: {matching_folder}")
                    
                    # 대상 폴더 생성
                    dest_folder = os.path.join(bundle_dir, zip_name)
                    os.makedirs(dest_folder, exist_ok=True)
                    
                    # 파일 복사
                    for item in os.listdir(matching_folder):
                        item_path = os.path.join(matching_folder, item)
                        if os.path.isdir(item_path):
                            shutil.copytree(item_path, os.path.join(dest_folder, item), dirs_exist_ok=True)
                        else:
                            shutil.copy2(item_path, os.path.join(dest_folder, item))
                else:
                    if debug:
                        print(f"  No matching folder, copying all contents from: {extract_subdir}")
                    
                    # 대상 폴더 생성
                    dest_folder = os.path.join(bundle_dir, zip_name)
                    os.makedirs(dest_folder, exist_ok=True)
                    
                    # 모든 내용 복사
                    for item in os.listdir(extract_subdir):
                        item_path = os.path.join(extract_subdir, item)
                        # 날짜 폴더 제외
                        if os.path.isdir(item_path) and "00_created_" in item:
                            if debug:
                                print(f"  Skipping date folder: {item}")
                            continue
                            
                        if os.path.isdir(item_path):
                            shutil.copytree(item_path, os.path.join(dest_folder, item), dirs_exist_ok=True)
                        else:
                            shutil.copy2(item_path, os.path.join(dest_folder, item))
            except Exception as e:
                print(f"Error processing ZIP file {zip_file}: {e}")
    else:
        # ZIP 파일이 없는 경우 직접 복사
        if debug:
            print(f"  No ZIP found in {lib_dir}, copying directly")
        
        # 대상 폴더 생성
        dest_folder = os.path.join(bundle_dir, lib_name)
        os.makedirs(dest_folder, exist_ok=True)
        
        # 파일 복사
        for item in os.listdir(lib_dir):
            # 제외 패턴 확인
            skip_item = False
            for pattern in exclude_patterns:
                if pattern in item:
                    skip_item = True
                    break
            
            if skip_item:
                if debug:
                    print(f"  Skipping excluded item: {item}")
                continue
                
            item_path = os.path.join(lib_dir, item)
            # 날짜 폴더 제외
            if os.path.isdir(item_path) and "00_created_" in item:
                if debug:
                    print(f"  Skipping date folder: {item}")
                continue
                
            if os.path.isdir(item_path):
                shutil.copytree(item_path, os.path.join(dest_folder, item), dirs_exist_ok=True)
            else:
                shutil.copy2(item_path, os.path.join(dest_folder, item))

def process_libraries(src_base_dir, bundle_dir, extract_dir, debug=False):
    """
    모든 라이브러리 처리를 위한 메인 함수
    """
    if debug:
        print(f"Processing libraries from: {src_base_dir}")
        print(f"Bundle directory: {bundle_dir}")
        print(f"Extract directory: {extract_dir}")
    
    # 디렉토리 생성
    os.makedirs(bundle_dir, exist_ok=True)
    os.makedirs(extract_dir, exist_ok=True)
    
    # 라이브러리 디렉토리 목록 가져오기
    lib_dirs = [
        d for d in glob.glob(os.path.join(src_base_dir, '*'))
        if os.path.isdir(d)
    ]
    
    if debug:
        print(f"Found {len(lib_dirs)} library directories")
    
    # 각 라이브러리 처리
    for lib_dir in lib_dirs:
        process_library(lib_dir, bundle_dir, extract_dir, debug)
    
    # 최종 정리: 불필요한 파일 제거
    for root, dirs, files in os.walk(bundle_dir):
        for file in files:
            if file in ["MetaFileUpdate.py", "FileMetaManager.py", "_file_meta.json"]:
                os.remove(os.path.join(root, file))
                if debug:
                    print(f"Removed file: {os.path.join(root, file)}")
        
        # 날짜 폴더 제거
        for dir_name in dirs[:]:  # 복사본으로 반복
            if "00_created_" in dir_name:
                shutil.rmtree(os.path.join(root, dir_name))
                if debug:
                    print(f"Removed directory: {os.path.join(root, dir_name)}")
                dirs.remove(dir_name)  # 원본 목록에서 제거

def create_bundle(bundle_dir, output_file, version, versions=None, debug=False):
    """
    최종 번들 ZIP 파일 생성
    """
    if debug:
        print(f"Creating bundle ZIP: {output_file}")
    
    # README 및 CHANGELOG 생성
    readme_content = f"""# ETboard 아두이노(Arduino) 라이브러리 묶음 패키지 v{version}

이 패키지는 ETboard 하드웨어를 위한 모든 필수 Arduino 라이브러리를 포함하고 있습니다.

## 설치 방법

### 수동 설치
1. 이 패키지의 압축을 해제합니다.
2. 압축을 해제한 폴더 내의 모든 라이브러리 폴더를 Arduino 스케치 폴더의 `libraries` 폴더에 복사합니다.
   - Windows: `%USERPROFILE%\Documents\Arduino\libraries\\`
   - Mac/Linux: `~/Documents/Arduino/libraries/`
3. Arduino IDE를 재시작합니다.

## 포함된 아두이노 라이브러리
"""
    
    if versions:
        for lib, ver in versions.items():
            readme_content += f"\n{lib}: v{ver}"
    
    changelog_content = f"""# ETboard 아두이노 라이브러리 변경 이력

## {version} - 새 버전 배포

### 포함된 아두이노 라이브러리 버전:
"""
    
    if versions:
        for lib, ver in versions.items():
            changelog_content += f"\n{lib}: v{ver}"
    
    # 임시 파일 생성
    readme_path = os.path.join(os.path.dirname(bundle_dir), "README.md")
    changelog_path = os.path.join(os.path.dirname(bundle_dir), "CHANGELOG.txt")
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(changelog_content)
    
    # ZIP 파일 생성
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 라이브러리 파일 추가
        for root, dirs, files in os.walk(bundle_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, bundle_dir)
                zipf.write(file_path, arcname)
        
        # README 및 CHANGELOG 추가
        zipf.write(readme_path, "README.md")
        zipf.write(changelog_path, "CHANGELOG.txt")
    
    # 임시 파일 삭제
    os.remove(readme_path)
    os.remove(changelog_path)
    
    if debug:
        print(f"ZIP bundle created: {output_file}")

def cleanup(bundle_dir, extract_dir, debug=False):
    """
    임시 디렉토리 정리
    """
    if debug:
        print("Cleaning up temporary directories...")
    
    if os.path.exists(bundle_dir):
        shutil.rmtree(bundle_dir)
        if debug:
            print(f"Removed directory: {bundle_dir}")
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
        if debug:
            print(f"Removed directory: {extract_dir}")

def main():
    """
    메인 실행 함수
    """
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='ETboard Arduino Library Bundle Utility')
    parser.add_argument('command', choices=['extract-versions', 'process-libraries', 'create-bundle', 'full-process'],
                        help='Command to execute')
    parser.add_argument('--etboard-path', default='resources/libs/arduino/etboard',
                        help='Path to ETboard libraries')
    parser.add_argument('--original-path', default='resources/libs/arduino/original',
                        help='Path to original libraries')
    parser.add_argument('--bundle-dir', default='arduino_library_bundle_temp',
                        help='Directory for bundle creation')
    parser.add_argument('--extract-dir', default='arduino_library_extract_temp',
                        help='Directory for extraction')
    parser.add_argument('--output-dir', default='resources/libs/arduino/all-zip',
                        help='Output directory for ZIP file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # 날짜 기반 버전 설정
    today = datetime.now().strftime('%Y.%m.%d')
    filename = f"ETboard_Arduino_Libraries_v{today}.zip"
    
    if args.command == 'extract-versions':
        etboard_meta_path = os.path.join(args.etboard_path, '_file_meta.json')
        original_meta_path = os.path.join(args.original_path, '_file_meta.json')
        
        versions = extract_versions(etboard_meta_path, original_meta_path)
        for lib, version in versions.items():
            print(f'{lib}: v{version}')
    
    elif args.command == 'process-libraries':
        process_libraries(args.etboard_path, args.bundle_dir, args.extract_dir, args.debug)
        process_libraries(args.original_path, args.bundle_dir, args.extract_dir, args.debug)
        
        if args.debug:
            print("\nFinal directory structure:")
            for root, dirs, files in os.walk(args.bundle_dir):
                level = root.replace(args.bundle_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                for f in files:
                    print(f"{indent}  {f}")
    
    elif args.command == 'create-bundle':
        etboard_meta_path = os.path.join(args.etboard_path, '_file_meta.json')
        original_meta_path = os.path.join(args.original_path, '_file_meta.json')
        
        versions = extract_versions(etboard_meta_path, original_meta_path)
        
        os.makedirs(args.output_dir, exist_ok=True)
        output_file = os.path.join(args.output_dir, filename)
        
        create_bundle(args.bundle_dir, output_file, today, versions, args.debug)
    
    elif args.command == 'full-process':
        try:
            # 1. 버전 정보 추출
            etboard_meta_path = os.path.join(args.etboard_path, '_file_meta.json')
            original_meta_path = os.path.join(args.original_path, '_file_meta.json')
            
            versions = extract_versions(etboard_meta_path, original_meta_path)
            if args.debug:
                print("Extracted versions:")
                for lib, version in versions.items():
                    print(f'  {lib}: v{version}')
            
            # 2. 라이브러리 처리
            process_libraries(args.etboard_path, args.bundle_dir, args.extract_dir, args.debug)
            process_libraries(args.original_path, args.bundle_dir, args.extract_dir, args.debug)
            
            # 3. 번들 생성
            os.makedirs(args.output_dir, exist_ok=True)
            output_file = os.path.join(args.output_dir, filename)
            
            create_bundle(args.bundle_dir, output_file, today, versions, args.debug)
            
            print(f"\nBundle created successfully: {output_file}")
            
        finally:
            # 4. 정리
            cleanup(args.bundle_dir, args.extract_dir, args.debug)

if __name__ == "__main__":
    main()
    