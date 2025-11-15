import streamlit as st

# 앱의 제목 설정
st.title('간단한 스트림릿 예제')

# 사용자에게 이름 입력 요청 (텍스트 입력 위젯)
name = st.text_input('여기에 이름을 입력해주세요:', '홍길동')

# 버튼 생성
if st.button('환영 메시지 보기'):
    # 버튼이 클릭되었을 때 메시지를 표시
    st.success(f'안녕하세요, {name}님! Streamlit 앱에 오신 것을 환영합니다.')

# 참고: st.write() 함수는 텍스트, 데이터프레임, 차트 등 다양한 것을 표시할 수 있습니다.
st.write('---')
st.write('이것은 구분선 아래의 추가 텍스트입니다.')
