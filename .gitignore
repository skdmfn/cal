import streamlit as st

st.title("⚙️ 공학 계산기 & 나만의 AI·공학 자료 저장소")

# ------------------------------
# 기능 1: 옴의 법칙 계산기
# ------------------------------
st.header("1️⃣ 옴의 법칙 계산기 (V = I × R)")

calc_option = st.selectbox("계산할 값 선택", ["전압(V)", "전류(I)", "저항(R)"])

try:
    if calc_option == "전압(V)":
        current = st.number_input("전류 I (A)", min_value=0.0, value=0.0)
        resistance = st.number_input("저항 R (Ω)", min_value=0.0, value=1.0)
        voltage = current * resistance
        st.write(f"전압 V = {voltage:.2f} V")
    elif calc_option == "전류(I)":
        voltage = st.number_input("전압 V (V)", min_value=0.0, value=0.0)
        resistance = st.number_input("저항 R (Ω)", min_value=0.0, value=1.0)
        current = voltage / resistance if resistance != 0 else 0
        st.write(f"전류 I = {current:.2f} A")
    elif calc_option == "저항(R)":
        voltage = st.number_input("전압 V (V)", min_value=0.0, value=0.0)
        current = st.number_input("전류 I (A)", min_value=0.0, value=1.0)
        resistance = voltage / current if current != 0 else 0
        st.write(f"저항 R = {resistance:.2f} Ω")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")

# ------------------------------
# 기능 2: 사용자 자료 저장소
# ------------------------------
st.header("2️⃣ 나만의 AI·공학 자료 저장소")

# 자료 입력 받기
title = st.text_input("자료 제목을 입력하세요")
content = st.text_area("내용을 입력하세요")
link = st.text_input("참고 링크(URL)를 입력하세요 (선택)")

# 저장 버튼
if st.button("저장하기"):
    if title.strip() == "" or content.strip() == "":
        st.error("제목과 내용은 반드시 입력해야 합니다.")
    else:
        # 기존에 저장된 리스트 불러오기 (세션 상태 활용)
        if 'notes' not in st.session_state:
            st.session_state.notes = []
        st.session_state.notes.append({
            "title": title,
            "content": content,
            "link": link
        })
        st.success(f"'{title}' 자료가 저장되었습니다.")

# 저장된 자료 보여주기
if 'notes' in st.session_state and st.session_state.notes:
    st.subheader("저장된 자료 목록")
    for i, note in enumerate(st.session_state.notes):
        st.markdown(f"### {i+1}. {note['title']}")
        st.write(note['content'])
        if note['link'].strip() != "":
            st.markdown(f"[참고 링크]({note['link']})")
        st.markdown("---")
else:
    st.info("아직 저장된 자료가 없습니다.")
