# 📚 아두이노 기본 라이브러리 버전 관리 시스템

> 효율적인 라이브러리 버전 관리

## 🗂 파일 구조

### `_file_meta.json`
   📄 라이브러리 버전 정보를 저장하는 JSON 파일   
  
  #### 수작업으로 변경해야 함.

  #### 중요 항목
   -. header -> updated_at : 메타파일 수정일자  
   -. body -> created_at   : 해당 라이브러 수정일자  
   -. body -> name, version, url : 아두이노 라이브러리.json 파일에서 가져옮  

### 기본 - 라이브러리 추가
   1. 라이브러리의 버전을 확인하고 설치한다. (예, OneWire 2.3.8)
   2. 라이브러리 예제를 컴파일하고 펌웨어를 기기에 업로드하여 테스트한다.
   3. 해당 라이브러리를 압축한다.(예, OneWire.zip)
   4. 해당 라이브러리 이름으로 폴더를 생성한다. (OneWire)
   5. 폴더안 dist 폴더를 만든다.(OneWire\dist)
   6. 버전을 나타내는 폴더를 만든다.(OneWire\dist\00._created_2024_11_06__15_15_55)
   7. dist 폴더 안애 압축파일을 복사 한다.(OneWire\dist\OneWire.zip)
   8. __file_meta.json 파일에 메타 정보를 업데이트 한다.(app\Arduino15\library_index.json 참고)
   

