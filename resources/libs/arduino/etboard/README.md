# 📚 라이브러리 버전 관리 시스템

> 효율적인 라이브러리 버전 관리를 위한 Python 기반 솔루션

## 🗂 파일 구조

### 1. `_file_meta.json`
   📄 라이브러리 버전 정보를 저장하는 JSON 파일

### 2. `MetaFileUpdate.py`
   🔍 디렉토리 스캔 및 메타 정보 업데이트
   - "00._created" 폴더 검색
   - `_file_meta.json` 파일 자동 갱신

### 3. `FileMetaManager.py`
   🔧 JSON 파일 관리 클래스 구현
   - `FileMetaHeader`: 헤더 정보 관리
   - `FileMetaBody`: 본문 정보 관리
   - `FileMetaManager`: 전체 파일 관리   

## 🚀 사용법
   - `MetaFileUpdate.py` 실행하여 메타 정보 갱신

