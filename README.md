# 위즈 크롬 익스텐션

# 크롬 익스텐션 시작하기

이 프로젝트는 기본적인 크롬 익스텐션의 템플릿입니다. 각 파일의 목적과 역할은 다음과 같습니다.

## 파일 구조

### `manifest.json`

이 파일은 크롬 익스텐션의 설정 파일입니다. 익스텐션의 이름, 설명, 버전, 필요한 권한 등을 설정할 수 있습니다.

### `background.js`

이 파일은 백그라운드에서 실행되는 스크립트입니다. 이 스크립트는 브라우저가 열려 있는 동안 계속 실행되며, 주로 웹 요청을 가로채거나 사용자의 행동에 반응하는 등의 작업을 수행합니다.

### `popup.html`

이 파일은 사용자가 익스텐션 아이콘을 클릭했을 때 나타나는 팝업의 HTML 구조를 정의합니다.

### `popup.js`

이 파일은 팝업에 대한 로직을 처리하는 스크립트입니다. 예를 들어, 버튼 클릭 이벤트나 사용자 입력 등을 처리할 수 있습니다.

### `styles.css`

이 파일은 팝업의 디자인을 담당하는 CSS 스타일시트입니다.

# 시험방 테스트 서버 사용하기
1. 터미널에서 'pip install flask' 입력
2. 터미널에서 'pip install flask-cors' 입력
3. 터미널에서 'flask run' 입력
4. 생성되는 __pycache__ 폴더 삭제하기
5. 아래 시작하기 대로..

## 시작하기

1. 이 저장소를 복제하거나 다운로드합니다.
2. 크롬에서 `chrome://extensions` 주소로 이동합니다.
3. 페이지 오른쪽 상단의 '개발자 모드'를 활성화합니다.
4. '압축해제된 확장 프로그램을 로드하기'를 클릭하고, 복제 또는 다운로드한 폴더를 선택합니다.
5. 이제 서버를 실행해야 합니다. `app.py`파일을 실행하고 열린 포트가 5000인지 확인하세요.(5000포트만 가능)
6. 이제 크롬 익스텐션이 로드되고 사용 가능한 상태가 되었습니다! 에듀테크 캠퍼스 사이트에서 사용해보세요!

## 라이센스

이 프로젝트는 MIT 라이센스에 따라 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.