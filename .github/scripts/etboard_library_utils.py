#!/usr/bin/env python3
# ********************************************************************************
# FileName     : etboard_library_utils.py
# Description  : ETboard Arduino Library Bundle Utility
# Author       : ETboard Team
# Created Date : 2024.03
# Reference    : pc에서 테스트 후에 github action에서 사용토록 제작됨
# Usage        : .github/scripts 폴더로 이동한 뒤에
#               python etboard_library_utils.py [command] [options]
#               commands:
#                 - process-libraries: Process library files
#                 - create-bundle: Create ZIP bundle
#                 - full-process: Run full process
#               example : python ./etboard_library_utils.py full-process --debug
# ********************************************************************************

import json
import os
import sys
import zipfile
import shutil
import glob
from pathlib import Path
from datetime import datetime

# 스크립트 경로를 기준으로 프로젝트 루트 계산
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))

def process_library(lib_dir, bundle_dir, extract_dir, debug=False):
    """
    단일 라이브러리 디렉토리를 처리하는 함수
    """
    # 불필요한 파일/폴더 패턴
    exclude_patterns = [
        "_file_meta.json",
        "MetaFileUpdate.py", 
        "FileMetaManager.py",
        "__pycache__"
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
    
    # ZIP 파일 생성
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 라이브러리 파일 추가
        for root, dirs, files in os.walk(bundle_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # libraries 폴더 아래에 상대 경로로 저장
                arcname = os.path.join('libraries', os.path.relpath(file_path, bundle_dir))
                zipf.write(file_path, arcname)
        
        # 생성 정보 폴더와 파일 추가 (libraries와 동일한 레벨)
        timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
        signature_dir = f"00._created_{timestamp}"
        signature_path = os.path.join(signature_dir, "signature.txt")
        
        # 빈 signature.txt 파일 생성
        with zipf.open(signature_path, 'w') as f:
            f.write(b'')
    
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
    
    parser = argparse.ArgumentParser(description='ETboard Arduino Library Bundle Utility')
    parser.add_argument('command', choices=['process-libraries', 'create-bundle', 'full-process'],
                        help='Command to execute')
    parser.add_argument('--etboard-path', 
                        default=os.path.join(PROJECT_ROOT, 'resources/libs/arduino/etboard'),
                        help='Path to ETboard libraries')
    parser.add_argument('--original-path', 
                        default=os.path.join(PROJECT_ROOT, 'resources/libs/arduino/original'),
                        help='Path to original libraries')
    parser.add_argument('--bundle-dir', 
                        default=os.path.join(PROJECT_ROOT, 'temp', 'arduino_library_bundle'),
                        help='Directory for bundle creation')
    parser.add_argument('--extract-dir', 
                        default=os.path.join(PROJECT_ROOT, 'temp', 'arduino_library_extract'),
                        help='Directory for extraction')
    parser.add_argument('--output-dir', 
                        default=os.path.join(PROJECT_ROOT, 'resources/libs/arduino/all-zip'),
                        help='Output directory for ZIP file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    if args.debug:
        print(f"Project root: {PROJECT_ROOT}")
        print(f"ETboard path: {args.etboard_path}")
        print(f"Original path: {args.original_path}")
    
    # 버전 없는 파일명 사용
    filename = "ETboard_Arduino_Libraries.zip"
    
    if args.command == 'process-libraries':
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
        os.makedirs(args.output_dir, exist_ok=True)
        output_file = os.path.join(args.output_dir, filename)
        
        create_bundle(args.bundle_dir, output_file, None, None, args.debug)
    
    elif args.command == 'full-process':
        try:
            # 1. 라이브러리 처리
            process_libraries(args.etboard_path, args.bundle_dir, args.extract_dir, args.debug)
            process_libraries(args.original_path, args.bundle_dir, args.extract_dir, args.debug)
            
            # 2. 번들 생성
            os.makedirs(args.output_dir, exist_ok=True)
            output_file = os.path.join(args.output_dir, filename)
            
            create_bundle(args.bundle_dir, output_file, None, None, args.debug)
            
            print(f"\nBundle created successfully: {output_file}")
            
        finally:
            # 3. 정리
            cleanup(args.bundle_dir, args.extract_dir, args.debug)

if __name__ == "__main__":
    main()

# ********************************************************************************
# End of File
# ********************************************************************************    