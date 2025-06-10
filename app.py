import streamlit as st
import json
import requests # 웹 요청에 사용 (스크랩 기능 확장 시 활용)
from bs4 import BeautifulSoup # HTML 파싱에 사용 (스크랩 기능 확장 시 활용)

# --- 설정 ---
# 이 파일에 공학 자료들이 영구적으로 저장됩니다.
DATA_FILE = 'engineering_notes.json'

st.set_page_config(
    page_title="공학 자료 관리 및 유틸리티",
    page_icon="⚙️",
    layout="centered" # "wide"로 변경 시 넓은 화면 사용
)

st.title("⚙️ 공학 자료 관리 및 유틸리티")
st.markdown("---")

# --- 데이터 영속성을 위한 헬퍼 함수 ---

def load_notes():
    """JSON 파일에서 저장된 자료들을 불러옵니다."""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 파일이 없으면 빈 리스트 반환 (앱 최초 실행 시)
        return []
    except json.JSONDecodeError:
        # JSON 파일이 비어있거나 손상된 경우 오류 처리 및 빈 리스트 반환
        st.error("⚠️ 저장된 자료 파일을 읽는 중 오류가 발생했습니다. 새롭게 시작합니다.")
        return []

def save_notes(notes):
    """현재 자료 리스트를 JSON 파일에 저장합니다."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        # 가독성을 위해 들여쓰기(indent=4) 적용
        # ensure_ascii=False로 한글 깨짐 방지
        json.dump(notes, f, indent=4, ensure_ascii=False)

# 세션 상태에 'notes'가 없으면, 파일을 로드하여 초기화합니다.
# 이는 앱이 시작되거나 새로고침될 때 한 번만 실행됩니다.
if 'notes' not in st.session_state:
    st.session_state.notes = load_notes()

# ------------------------------
# 기능 1: 공학 단위 변환기
# ------------------------------
st.header("1️⃣ 공학 단위 변환기")
st.write("다양한 공학 단위를 손쉽게 변환해 보세요.")

unit_category = st.selectbox("변환할 단위 종류 선택",
                             ["길이", "질량", "온도", "압력", "에너지"],
                             key="unit_category_select")

col1, col2 = st.columns(2)

with col1:
    # `format="%.6f"`를 사용하여 소수점 입력 및 표시 정밀도 향상
    value = st.number_input("변환할 값", min_value=0.0, value=1.0, format="%.6f", key="input_value")
    
with col2:
    if unit_category == "길이":
        from_unit = st.selectbox("시작 단위", ["m", "cm", "mm", "km", "inch", "ft"], key="length_from")
        to_unit = st.selectbox("변환할 단위", ["m", "cm", "mm", "km", "inch", "ft"], key="length_to")
        # 각 단위의 기준 단위(여기서는 미터 'm')에 대한 환산 계수 (1 단위 = X 미터)
        conversions = {
            "m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0, "inch": 0.0254, "ft": 0.3048
        }
    elif unit_category == "질량":
        from_unit = st.selectbox("시작 단위", ["kg", "g", "mg", "ton", "lb"], key="mass_from")
        to_unit = st.selectbox("변환할 단위", ["kg", "g", "mg", "ton", "lb"], key="mass_to")
        # 각 단위의 기준 단위(여기서는 킬로그램 'kg')에 대한 환산 계수
        conversions = {
            "kg": 1.0, "g": 0.001, "mg": 0.000001, "ton": 1000.0, "lb": 0.453592
        }
    elif unit_category == "온도":
        from_unit = st.selectbox("시작 단위", ["°C", "°F", "K"], key="temp_from")
        to_unit = st.selectbox("변환할 단위", ["°C", "°F", "K"], key="temp_to")
        
        def convert_temperature(val, from_u, to_u):
            # 모든 온도를 섭씨(Celsius)로 변환하여 중간 계산
            if from_u == "°C":
                celsius = val
            elif from_u == "°F":
                celsius = (val - 32) * 5/9
            elif from_u == "K":
                celsius = val - 273.15
            else: 
                return val # 오류 방지용 (실제로는 selectbox로 인해 발생X)

            # 섭씨에서 목표 단위로 변환
            if to_u == "°C":
                return celsius
            elif to_u == "°F":
                return (celsius * 9/5) + 32
            elif to_u == "K":
                return celsius + 273.15
            else:
                return val # 오류 방지용

    elif unit_category == "압력":
        from_unit = st.selectbox("시작 단위", ["Pa", "kPa", "MPa", "bar", "psi", "atm"], key="pressure_from")
        to_unit = st.selectbox("변환할 단위", ["Pa", "kPa", "MPa", "bar", "psi", "atm"], key="pressure_to")
        # 각 단위의 기준 단위(여기서는 파스칼 'Pa')에 대한 환산 계수
        conversions = {
            "Pa": 1.0, "kPa": 1000.0, "MPa": 1000000.0, "bar": 100000.0, "psi": 6894.76, "atm": 101325.0
        }
    elif unit_category == "에너지":
        from_unit = st.selectbox("시작 단위", ["J", "kJ", "cal", "kcal", "Wh", "kWh"], key="energy_from")
        to_unit = st.selectbox("변환할 단위", ["J", "kJ", "cal", "kcal", "Wh", "kWh"], key="energy_to")
        # 각 단위의 기준 단위(여기서는 줄 'J')에 대한 환산 계수
        conversions = {
            "J": 1.0, "kJ": 1000.0, "cal": 4.184, "kcal": 4184.0, "Wh": 3600.0, "kWh": 3600000.0
        }

try:
    if from_unit == to_unit:
        result = value # 단위가 같으면 변환 불필요
    elif unit_category == "온도":
        result = convert_temperature(value, from_unit, to_unit)
    else:
        # 입력 값을 기준 단위로 변환 (예: 길이의 경우 미터로)
        value_in_base = value * conversions[from_unit]
        # 기준 단위 값을 목표 단위로 변환
        result = value_in_base / conversions[to_unit]
            
    st.markdown(f"**변환 결과:** `{value:.4f} {from_unit}` **=** `{result:.4f} {to_unit}`")

except KeyError:
    st.error("⚠️ 단위 변환 오류: 선택된 단위 조합에 대한 변환 정보를 찾을 수 없습니다. (내부 변환 계수 오류)")
except Exception as e:
    st.error(f"⚠️ 단위 변환 중 예상치 못한 오류가 발생했습니다. 입력 값을 확인해주세요. 오류: {e}")
    st.info("💡 단위 변환은 선택된 카테고리 내에서만 가능합니다.")

st.markdown("---")

# ------------------------------
# 기능 2: 공학 자료 검색 및 스크랩
# ------------------------------
st.header("2️⃣ 공학 자료 검색 및 스크랩")
st.write("궁금한 공학 개념이나 자료를 검색하고, 필요한 정보를 스크랩하여 저장해 보세요.")

search_query = st.text_input(
    "검색할 공학 자료 키워드를 입력하세요 (예: '열역학 제1법칙', '파이썬 데이터 분석')",
    key="search_query_input",
    placeholder="검색할 키워드를 입력하세요"
)
search_button = st.button("자료 검색 및 스크랩 실행", key="search_button")

if search_button:
    if search_query.strip() != "":
        st.info(f"🔍 '{search_query}'에 대한 자료를 검색 중입니다...")
        # CORRECTED: Changed 'Google Search_url' to 'Google Search_url'
        Google Search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}+공학"
        st.markdown(f"**[Google에서 '{search_query}'(을)를 검색하기]({Google Search_url})**", unsafe_allow_html=True)
        st.write("⬆️ 위 링크를 클릭하여 필요한 자료를 찾으신 후, 아래 '나만의 공학 자료 저장소'에 내용을 저장해 주세요.")
    else:
        st.warning("⚠️ 검색 키워드를 입력해 주세요.")

st.markdown("---")

# ------------------------------
# 기능 3: 나만의 공학 자료 저장소
# ------------------------------
st.header("3️⃣ 나만의 공학 자료 저장소")
st.write("자신만의 공학 지식과 자료를 체계적으로 저장하고 관리하세요.")

title = st.text_input("자료 제목을 입력하세요", key="note_title", placeholder="예: 푸리에 변환의 응용 원리")
content = st.text_area("내용을 입력하세요", key="note_content", height=150, placeholder="여기에 자료 내용을 자세히 작성하세요...")
link = st.text_input("참고 링크(URL)를 입력하세요 (선택)", key="note_link", placeholder="예: https://www.k-engineer.com/resource")

if st.button("➕ 새 자료 저장하기", key="save_note_button"):
    if title.strip() == "" or content.strip() == "":
        st.error("🚫 제목과 내용은 반드시 입력해야 합니다.")
    else:
        st.session_state.notes.append({
            "title": title,
            "content": content,
            "link": link
        })
        save_notes(st.session_state.notes) # 업데이트된 자료를 JSON 파일에 저장
        st.success(f"✔️ '{title}' 자료가 성공적으로 저장되었습니다.")
        # 사용자 경험 향상을 위해 입력 필드 초기화
        st.session_state.note_title = ""
        st.session_state.note_content = ""
        st.session_state.note_link = ""
        st.rerun() # 앱을 다시 실행하여 입력 필드를 비우고 목록을 업데이트

st.markdown("---")

st.subheader("📝 저장된 자료 목록")

if st.session_state.notes:
    # 모든 자료 삭제 버튼
    if st.button("🗑️ 모든 자료 삭제", key="clear_all_notes_button"):
        st.session_state.notes = [] # 세션 상태에서 모든 자료 제거
        save_notes(st.session_state.notes) # 파일에서도 삭제 내용 반영
        st.success("모든 자료가 성공적으로 삭제되었습니다.")
        st.rerun() # 빈 목록을 보여주기 위해 새로고침

    # 각 자료를 반복하며 표시 및 삭제 버튼 추가
    for i, note in enumerate(st.session_state.notes):
        st.markdown(f"### {i+1}. {note['title']}")
        st.write(note['content'])
        if note['link'].strip() != "":
            st.markdown(f"[🔗 참고 링크]({note['link']})")
        
        # 각 자료에 대한 개별 삭제 버튼
        # 고유한 key를 사용하여 Streamlit 오류 방지
        if st.button(f"삭제: '{note['title']}'", key=f"delete_note_{i}"):
            st.session_state.notes.pop(i) # 리스트에서 해당 자료 제거
            save_notes(st.session_state.notes) # 수정된 리스트를 파일에 저장
            st.success(f"'{note['title']}' 자료가 삭제되었습니다.")
            st.rerun() # 목록 업데이트를 위해 새로고침
        
        st.markdown("---")
else:
    st.info("아직 저장된 자료가 없습니다. 새로운 자료를 추가해 보세요!")

st.markdown("---")
st.info("💡 이 앱은 데이터를 'engineering_notes.json' 파일에 로컬로 저장합니다. 앱이 실행되는 동일한 폴더에 파일이 생성됩니다.")
