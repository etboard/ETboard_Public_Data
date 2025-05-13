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

# 스크립트 경로를 기준으로 프로젝트 루트 계산 (Path 사용)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

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
    
    # 라이브러리 이름 추출 (Path 사용)
    lib_dir = Path(lib_dir)
    lib_name = lib_dir.name
    
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
    for zip_file in lib_dir.rglob("*.zip"):
        zip_files.append(zip_file)
    
    if zip_files:
        # ZIP 파일이 있는 경우
        for zip_file in zip_files:
            zip_name = zip_file.stem
            if debug:
                print(f"  Found ZIP: {zip_file}, name: {zip_name}")
            
            # ZIP 파일 추출
            extract_subdir = Path(extract_dir) / zip_name
            if extract_subdir.exists():
                shutil.rmtree(extract_subdir)
            extract_subdir.mkdir(parents=True, exist_ok=True)
            
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_subdir)
                
                # 라이브러리와 동일한 이름의 폴더 확인
                matching_folder = extract_subdir / zip_name
                if matching_folder.exists() and matching_folder.is_dir():
                    if debug:
                        print(f"  Found matching folder: {matching_folder}")
                    
                    # 대상 폴더 생성
                    dest_folder = Path(bundle_dir) / zip_name
                    dest_folder.mkdir(parents=True, exist_ok=True)
                    
                    # 파일 복사
                    for item in matching_folder.iterdir():
                        if item.is_dir():
                            shutil.copytree(item, dest_folder / item.name, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest_folder / item.name)
                else:
                    if debug:
                        print(f"  No matching folder, copying all contents from: {extract_subdir}")
                    
                    # 대상 폴더 생성
                    dest_folder = Path(bundle_dir) / zip_name
                    dest_folder.mkdir(parents=True, exist_ok=True)
                    
                    # 모든 내용 복사
                    for item in extract_subdir.iterdir():
                        # 날짜 폴더 제외
                        if item.is_dir() and "00_created_" in item.name:
                            if debug:
                                print(f"  Skipping date folder: {item}")
                            continue
                            
                        if item.is_dir():
                            shutil.copytree(item, dest_folder / item.name, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest_folder / item.name)
            except Exception as e:
                print(f"Error processing ZIP file {zip_file}: {e}")
    else:
        # ZIP 파일이 없는 경우 직접 복사
        if debug:
            print(f"  No ZIP found in {lib_dir}, copying directly")
        
        # 대상 폴더 생성
        dest_folder = Path(bundle_dir) / lib_name
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        # 파일 복사
        for item in lib_dir.iterdir():
            # 제외 패턴 확인
            skip_item = False
            for pattern in exclude_patterns:
                if pattern in item.name:
                    skip_item = True
                    break
            
            if skip_item:
                if debug:
                    print(f"  Skipping excluded item: {item}")
                continue
                
            # 날짜 폴더 제외
            if item.is_dir() and "00_created_" in item.name:
                if debug:
                    print(f"  Skipping date folder: {item}")
                continue
                
            if item.is_dir():
                shutil.copytree(item, dest_folder / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest_folder / item.name)

def process_libraries(src_base_dir, bundle_dir, extract_dir, debug=False):
    """
    모든 라이브러리 처리를 위한 메인 함수
    """
    if debug:
        print(f"Processing libraries from: {src_base_dir}")
        print(f"Bundle directory: {bundle_dir}")
        print(f"Extract directory: {extract_dir}")
    
    # 디렉토리 생성
    Path(bundle_dir).mkdir(parents=True, exist_ok=True)
    Path(extract_dir).mkdir(parents=True, exist_ok=True)
    
    # 라이브러리 디렉토리 목록 가져오기
    src_base_dir = Path(src_base_dir)
    lib_dirs = [d for d in src_base_dir.iterdir() if d.is_dir()]
    
    if debug:
        print(f"Found {len(lib_dirs)} library directories")
    
    # 각 라이브러리 처리
    for lib_dir in lib_dirs:
        process_library(lib_dir, bundle_dir, extract_dir, debug)
    
    # 최종 정리: 불필요한 파일 제거
    bundle_dir = Path(bundle_dir)
    for item in bundle_dir.rglob("*"):
        if item.is_file() and item.name in ["MetaFileUpdate.py", "FileMetaManager.py", "_file_meta.json"]:
            item.unlink()
            if debug:
                print(f"Removed file: {item}")
        elif item.is_dir() and "00_created_" in item.name:
            shutil.rmtree(item)
            if debug:
                print(f"Removed directory: {item}")

def create_bundle(bundle_dir, output_file, version, versions=None, debug=False):
    """
    최종 번들 ZIP 파일 생성
    """
    if debug:
        print(f"Creating bundle ZIP: {output_file}")
    
    # 출력 디렉토리 생성
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # ZIP 파일 생성
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 라이브러리 파일 추가
        bundle_dir = Path(bundle_dir)
        for item in bundle_dir.rglob("*"):
            if item.is_file():
                arcname = os.path.join('libraries', item.relative_to(bundle_dir))
                zipf.write(item, arcname)
        
        # 생성 정보 폴더와 파일 추가 (libraries와 동일한 레벨)
        timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
        signature_dir = f"00._created_{timestamp}"
        signature_path = f"{signature_dir}/signature.txt"
        
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
    
    bundle_dir = Path(bundle_dir)
    extract_dir = Path(extract_dir)
    
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
        if debug:
            print(f"Removed directory: {bundle_dir}")
    
    if extract_dir.exists():
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
                        default=PROJECT_ROOT / 'resources/libs/arduino/etboard',
                        help='Path to ETboard libraries')
    parser.add_argument('--original-path', 
                        default=PROJECT_ROOT / 'resources/libs/arduino/original',
                        help='Path to original libraries')
    parser.add_argument('--bundle-dir', 
                        default=PROJECT_ROOT / 'temp/arduino_library_bundle',
                        help='Directory for bundle creation')
    parser.add_argument('--extract-dir', 
                        default=PROJECT_ROOT / 'temp/arduino_library_extract',
                        help='Directory for extraction')
    parser.add_argument('--output-dir', 
                        default=PROJECT_ROOT / 'resources/libs/arduino/all-zip',
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
            bundle_dir = Path(args.bundle_dir)
            for item in bundle_dir.rglob("*"):
                if item.is_dir():
                    level = len(item.relative_to(bundle_dir).parts)
                    indent = ' ' * 2 * level
                    print(f"{indent}{item.name}/")
                else:
                    level = len(item.parent.relative_to(bundle_dir).parts)
                    indent = ' ' * 2 * (level + 1)
                    print(f"{indent}{item.name}")
    
    elif args.command == 'create-bundle':
        os.makedirs(args.output_dir, exist_ok=True)
        output_file = Path(args.output_dir) / filename
        
        create_bundle(args.bundle_dir, output_file, None, None, args.debug)
    
    elif args.command == 'full-process':
        try:
            # 1. 라이브러리 처리
            process_libraries(args.etboard_path, args.bundle_dir, args.extract_dir, args.debug)
            process_libraries(args.original_path, args.bundle_dir, args.extract_dir, args.debug)
            
            # 2. 번들 생성
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / filename
            
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