# 신성EP 개발 샘플 통합 관리 시스템

이 프로젝트는 **Streamlit**을 사용하여 제작된 개발 샘플 관리 웹 애플리케이션입니다.

## ☁️ 웹 호스팅 (Streamlit Cloud 배포) 방법

이 시스템을 인터넷(웹)에서 누구나 접속할 수 있도록 하려면 **Streamlit Cloud**를 사용하는 것이 가장 간편합니다.

### 1단계: 준비 (GitHub 업로드)
1. [GitHub](https://github.com/)에 회원가입하고 로그인합니다.
2. 우측 상단의 `+` 버튼 -> `New repository`를 클릭합니다.
3. 저장소 이름(예: `sample-management-system`)을 입력하고 `Create repository`를 누릅니다.
4. 이 폴더의 모든 파일(`maintenance` 폴더 제외)을 해당 저장소에 업로드합니다.
   - (GitHub Desktop 등을 사용하거나, 'Upload files' 기능을 사용하여 파일들을 드래그 앤 드롭)

### 2단계: 배포 (Streamlit Cloud)
1. [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.
2. `New app` 버튼을 클릭합니다.
3. 방금 생성한 GitHub 저장소(`sample-management-system`)를 선택합니다.
4. `Main file path`에 `app.py`라고 입력되어 있는지 확인합니다.
5. `Deploy!` 버튼을 클릭합니다.

### ⚠️ 중요: 데이터 저장 주의사항 (Excel)
Streamlit Cloud는 **앱이 재시작되거나 업데이트될 때 로컬 파일(`sample_db.xlsx`)이 초기화될 수 있습니다.**
- **임시 사용/데모용**으로는 문제가 없으나, 장기간 중요 데이터를 저장하려면 **구글 시트(Google Sheets) 연동**이나 **외부 데이터베이스** 사용을 권장합니다.
- 현재 버전은 **엑셀 파일** 기반이므로, 데이터를 백업하려면 주기적으로 관리자 메뉴에서 **'엑셀 다운로드'**를 받아두시는 것이 좋습니다.

## 🛠️ 로컬 실행 방법
내 컴퓨터에서 바로 실행하려면:
1. `run_system.bat` 파일을 더블 클릭하세요.
