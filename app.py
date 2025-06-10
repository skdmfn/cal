import streamlit as st
import json
import requests # For fetching website content (optional, but good for scrap)
from bs4 import BeautifulSoup # For parsing HTML (optional)

# --- Configuration ---
DATA_FILE = 'engineering_notes.json' # Define the file to store data

st.title("⚙️ 공학 자료 관리 및 유틸리티")

# --- Function to load notes ---
def load_notes():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        st.error("Error decoding notes file. Starting with empty notes.")
        return []

# --- Function to save notes ---
def save_notes(notes):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=4, ensure_ascii=False)

# Initialize notes in session state if not already present
if 'notes' not in st.session_state:
    st.session_state.notes = load_notes()

# ------------------------------
# 기능 1: 단위 변환기
# ------------------------------
st.header("1️⃣ 공학 단위 변환기")

unit_category = st.selectbox("변환할 단위 종류 선택",
                             ["길이", "질량", "온도", "압력", "에너지"])

col1, col2 = st.columns(2)

with col1:
    value = st.number_input("변환할 값", min_value=0.0, value=1.0)
    
with col2:
    if unit_category == "길이":
        from_unit = st.selectbox("시작 단위", ["m", "cm", "mm", "km", "inch", "ft"])
        to_unit = st.selectbox("변환할 단위", ["m", "cm", "mm", "km", "inch", "ft"])
        conversions = {
            "m": {"cm": 100, "mm": 1000, "km": 0.001, "inch": 39.3701, "ft": 3.28084},
            "cm": {"m": 0.01, "mm": 10, "km": 0.00001, "inch": 0.393701, "ft": 0.0328084},
            "mm": {"m": 0.001, "cm": 0.1, "km": 0.000001, "inch": 0.0393701, "ft": 0.00328084},
            "km": {"m": 1000, "cm": 100000, "mm": 1000000, "inch": 39370.1, "ft": 3280.84},
            "inch": {"m": 0.0254, "cm": 2.54, "mm": 25.4, "km": 0.0000254, "ft": 0.0833333},
            "ft": {"m": 0.3048, "cm": 30.48, "mm": 304.8, "km": 0.0003048, "inch": 12}
        }
    elif unit_category == "질량":
        from_unit = st.selectbox("시작 단위", ["kg", "g", "mg", "ton", "lb"])
        to_unit = st.selectbox("변환할 단위", ["kg", "g", "mg", "ton", "lb"])
        conversions = {
            "kg": {"g": 1000, "mg": 1000000, "ton": 0.001, "lb": 2.20462},
            "g": {"kg": 0.001, "mg": 1000, "ton": 0.000001, "lb": 0.00220462},
            "mg": {"kg": 0.000001, "g": 0.001, "ton": 0.000000001, "lb": 0.00000220462},
            "ton": {"kg": 1000, "g": 1000000, "mg": 1000000000, "lb": 2204.62},
            "lb": {"kg": 0.453592, "g": 453.592, "mg": 453592, "ton": 0.000453592}
        }
    elif unit_category == "온도":
        from_unit = st.selectbox("시작 단위", ["°C", "°F", "K"])
        to_unit = st.selectbox("변환할 단위", ["°C", "°F", "K"])
        
        def convert_temperature(val, from_u, to_u):
            if from_u == "°C":
                if to_u == "°F": return (val * 9/5) + 32
                if to_u == "K": return val + 273.15
            elif from_u == "°F":
                if to_u == "°C": return (val - 32) * 5/9
                if to_u == "K": return (val - 32) * 5/9 + 273.15
            elif from_u == "K":
                if to_u == "°C": return val - 273.15
                if to_u == "°F": return (val - 273.15) * 9/5 + 32
            return val # Same unit
    elif unit_category == "압력":
        from_unit = st.selectbox("시작 단위", ["Pa", "kPa", "MPa", "bar", "psi", "atm"])
        to_unit = st.selectbox("변환할 단위", ["Pa", "kPa", "MPa", "bar", "psi", "atm"])
        conversions = {
            "Pa": {"kPa": 0.001, "MPa": 0.000001, "bar": 0.00001, "psi": 0.000145038, "atm": 0.00000986923},
            "kPa": {"Pa": 1000, "MPa": 0.001, "bar": 0.01, "psi": 0.145038, "atm": 0.00986923},
            "MPa": {"Pa": 1000000, "kPa": 1000, "bar": 10, "psi": 145.038, "atm": 9.86923},
            "bar": {"Pa": 100000, "kPa": 100, "MPa": 0.1, "psi": 14.5038, "atm": 0.986923},
            "psi": {"Pa": 6894.76, "kPa": 6.89476, "MPa": 0.00689476, "bar": 0.0689476, "atm": 0.068046},
            "atm": {"Pa": 101325, "kPa": 101.325, "MPa": 0.101325, "bar": 1.01325, "psi": 14.696}
        }
    elif unit_category == "에너지":
        from_unit = st.selectbox("시작 단위", ["J", "kJ", "cal", "kcal", "Wh", "kWh"])
        to_unit = st.selectbox("변환할 단위", ["J", "kJ", "cal", "kcal", "Wh", "kWh"])
        conversions = {
            "J": {"kJ": 0.001, "cal": 0.239006, "kcal": 0.000239006, "Wh": 0.000277778, "kWh": 0.000000277778},
            "kJ": {"J": 1000, "cal": 239.006, "kcal": 0.239006, "Wh": 0.277778, "kWh": 0.000277778},
            "cal": {"J": 4.184, "kJ": 0.004184, "kcal": 0.001, "Wh": 0.00116222, "kWh": 0.00000116222},
            "kcal": {"J": 4184, "kJ": 4.184, "cal": 1000, "Wh": 1.16222, "kWh": 0.00116222},
            "Wh": {"J": 3600, "kJ": 3.6, "cal": 859.845, "kcal": 0.859845, "kWh": 0.001},
            "kWh": {"J": 3600000, "kJ": 3600, "cal": 859845, "kcal": 859.845, "Wh": 1000}
        }

try:
    if unit_category == "온도":
        result = convert_temperature(value, from_unit, to_unit)
    else:
        # Convert value to base unit (e.g., meter for length)
        if from_unit != to_unit:
            base_value = value
            if from_unit != list(conversions.keys())[0]: # If not already base unit
                for unit, factor in conversions[from_unit].items():
                    if factor == 1: # Find base unit conversion factor (e.g., m->m is 1)
                        # This logic needs to be more robust, typically convert to a common base unit first
                        # For simplicity, if not directly convert, assume factor from the first unit in the list
                        if list(conversions.keys())[0] in conversions[from_unit]:
                            base_value = value * conversions[from_unit][list(conversions.keys())[0]]
                        else: # If base unit is not directly convertible from 'from_unit'
                            # This scenario means we need to find a common intermediary
                            # For simplicity, convert 'from_unit' to a common unit (e.g., the first unit in 'conversions')
                            # And then convert from that common unit to 'to_unit'
                            pass # Handled by the direct conversion below
            
            # Direct conversion
            if to_unit in conversions[from_unit]:
                result = value * conversions[from_unit][to_unit]
            elif from_unit in conversions[to_unit]: # If target unit can convert from source
                result = value / conversions[to_unit][from_unit]
            else: # If no direct path, try via a common base unit (e.g., first unit in conversions)
                # This part needs careful design for all unit systems to be fully robust.
                # For now, it defaults to the 'pass' and likely goes to 'st.error' or 'value' if conversion fails
                # A more robust system would convert 'from_unit' to a common base unit first, then to 'to_unit'.
                if from_unit != to_unit: # Only try complex conversion if units are different
                    # Example: from_unit -> base_unit -> to_unit
                    # Assuming the first key in conversions is a good 'base' for direct calculations
                    common_base_unit = list(conversions.keys())[0]
                    if from_unit == common_base_unit:
                        val_in_base = value
                    elif common_base_unit in conversions[from_unit]:
                         val_in_base = value * conversions[from_unit][common_base_unit]
                    elif from_unit in conversions[common_base_unit]: # If common base unit converts from 'from_unit'
                         val_in_base = value / conversions[common_base_unit][from_unit]
                    else: # Fallback if no easy path
                        val_in_base = value # Default to original if no conversion logic found

                    if to_unit == common_base_unit:
                        result = val_in_base
                    elif to_unit in conversions[common_base_unit]:
                        result = val_in_base * conversions[common_base_unit][to_unit]
                    elif common_base_unit in conversions[to_unit]:
                        result = val_in_base / conversions[to_unit][common_base_unit]
                    else:
                        result = value # No conversion path found, default to original
                else:
                    result = value # Same unit, no conversion needed
        else:
            result = value # Same unit, no conversion needed
            
    st.write(f"변환 결과: **{result:.4f} {to_unit}**")

except Exception as e:
    st.error(f"단위 변환 중 오류가 발생했습니다. 값을 확인해주세요. 오류: {e}")
    st.info("단위 변환은 동일한 카테고리 내에서만 가능합니다.")

st.markdown("---")

# ------------------------------
# 기능 2: 공학 자료 검색 및 스크랩
# ------------------------------
st.header("2️⃣ 공학 자료 검색 및 스크랩")

search_query = st.text_input("검색할 공학 자료 키워드를 입력하세요 (예: '열역학 제1법칙', '파이썬 데이터 분석')", key="search_query_input")
search_button = st.button("자료 검색 및 스크랩")

if search_button and search_query.strip() != "":
    st.info(f"'{search_query}'에 대한 자료를 검색 중입니다...")
    # 실제 검색 엔진 API (예: Google Custom Search API, Bing Web Search API 등)를 연동하거나
    # 간단하게 구글 검색 링크를 제공하는 방식으로 구현할 수 있습니다.
    # 여기서는 간단하게 구글 검색 링크를 생성합니다.
    Google Search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}+공학"
    st.markdown(f"**[Google에서 '{search_query}'(을)를 검색하기]({Google Search_url})**", unsafe_allow_html=True)
    st.write("위 링크를 클릭하여 필요한 자료를 찾으신 후, 아래 '나만의 공학 자료 저장소'에 내용을 저장해 주세요.")

st.markdown("---")

# ------------------------------
# 기능 3: 나만의 공학 자료 저장소
# ------------------------------
st.header("3️⃣ 나만의 공학 자료 저장소")

# 자료 입력 받기
title = st.text_input("자료 제목을 입력하세요", key="note_title")
content = st.text_area("내용을 입력하세요", key="note_content")
link = st.text_input("참고 링크(URL)를 입력하세요 (선택)", key="note_link")

# 저장 버튼
if st.button("저장하기", key="save_button"):
    if title.strip() == "" or content.strip() == "":
        st.error("제목과 내용은 반드시 입력해야 합니다.")
    else:
        st.session_state.notes.append({
            "title": title,
            "content": content,
            "link": link
        })
        save_notes(st.session_state.notes) # Save updated notes to file
        st.success(f"'{title}' 자료가 저장되었습니다.")
        # Clear input fields after saving
        st.session_state.note_title = ""
        st.session_state.note_content = ""
        st.session_state.note_link = ""

# 저장된 자료 보여주기
st.subheader("저장된 자료 목록")
if st.session_state.notes:
    for i, note in enumerate(st.session_state.notes):
        st.markdown(f"### {i+1}. {note['title']}")
        st.write(note['content'])
        if note['link'].strip() != "":
            st.markdown(f"[참고 링크]({note['link']})")
        st.markdown("---")
else:
    st.info("아직 저장된 자료가 없습니다.")
