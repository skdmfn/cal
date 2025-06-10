import streamlit as st
import json
import requests # Used for web requests, although not fully implemented for scrap yet
from bs4 import BeautifulSoup # Used for parsing HTML, though not fully implemented for scrap yet

# --- Configuration ---
# This file will store your engineering notes persistently.
DATA_FILE = 'engineering_notes.json'

st.set_page_config(
    page_title="공학 자료 관리 및 유틸리티",
    page_icon="⚙️",
    layout="centered"
)

st.title("⚙️ 공학 자료 관리 및 유틸리티")
st.markdown("---")

# --- Helper Functions for Data Persistence ---

def load_notes():
    """Loads saved notes from the JSON file."""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty list.
        return []
    except json.JSONDecodeError:
        # Handle cases where the JSON file might be empty or corrupted.
        st.error("저장된 자료 파일을 읽는 중 오류가 발생했습니다. 새롭게 시작합니다.")
        return []

def save_notes(notes):
    """Saves the current list of notes to the JSON file."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        # Use indent for readability in the JSON file.
        # ensure_ascii=False allows saving Korean characters directly.
        json.dump(notes, f, indent=4, ensure_ascii=False)

# Initialize notes in session state. This makes sure notes are loaded once
# when the app starts or refreshes, and then managed by Streamlit's session.
if 'notes' not in st.session_state:
    st.session_state.notes = load_notes()

# ------------------------------
# Feature 1: Engineering Unit Converter
# ------------------------------
st.header("1️⃣ 공학 단위 변환기")
st.write("다양한 공학 단위를 손쉽게 변환해 보세요.")

unit_category = st.selectbox("변환할 단위 종류 선택",
                             ["길이", "질량", "온도", "압력", "에너지"],
                             key="unit_category_select")

col1, col2 = st.columns(2)

with col1:
    value = st.number_input("변환할 값", min_value=0.0, value=1.0, key="input_value")
    
with col2:
    if unit_category == "길이":
        from_unit = st.selectbox("시작 단위", ["m", "cm", "mm", "km", "inch", "ft"], key="length_from")
        to_unit = st.selectbox("변환할 단위", ["m", "cm", "mm", "km", "inch", "ft"], key="length_to")
        # Conversion factors relative to 'm' (meter)
        conversions = {
            "m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0, "inch": 0.0254, "ft": 0.3048
        }
    elif unit_category == "질량":
        from_unit = st.selectbox("시작 단위", ["kg", "g", "mg", "ton", "lb"], key="mass_from")
        to_unit = st.selectbox("변환할 단위", ["kg", "g", "mg", "ton", "lb"], key="mass_to")
        # Conversion factors relative to 'kg' (kilogram)
        conversions = {
            "kg": 1.0, "g": 0.001, "mg": 0.000001, "ton": 1000.0, "lb": 0.453592
        }
    elif unit_category == "온도":
        from_unit = st.selectbox("시작 단위", ["°C", "°F", "K"], key="temp_from")
        to_unit = st.selectbox("변환할 단위", ["°C", "°F", "K"], key="temp_to")
        
        def convert_temperature(val, from_u, to_u):
            # Convert to Celsius first for intermediate calculation
            if from_u == "°C":
                celsius = val
            elif from_u == "°F":
                celsius = (val - 32) * 5/9
            elif from_u == "K":
                celsius = val - 273.15
            else:
                return val # Should not happen with selectbox

            # Convert from Celsius to target unit
            if to_u == "°C":
                return celsius
            elif to_u == "°F":
                return (celsius * 9/5) + 32
            elif to_u == "K":
                return celsius + 273.15
            return val # Should not happen

    elif unit_category == "압력":
        from_unit = st.selectbox("시작 단위", ["Pa", "kPa", "MPa", "bar", "psi", "atm"], key="pressure_from")
        to_unit = st.selectbox("변환할 단위", ["Pa", "kPa", "MPa", "bar", "psi", "atm"], key="pressure_to")
        # Conversion factors relative to 'Pa' (Pascal)
        conversions = {
            "Pa": 1.0, "kPa": 1000.0, "MPa": 1000000.0, "bar": 100000.0, "psi": 6894.76, "atm": 101325.0
        }
    elif unit_category == "에너지":
        from_unit = st.selectbox("시작 단위", ["J", "kJ", "cal", "kcal", "Wh", "kWh"], key="energy_from")
        to_unit = st.selectbox("변환할 단위", ["J", "kJ", "cal", "kcal", "Wh", "kWh"], key="energy_to")
        # Conversion factors relative to 'J' (Joule)
        conversions = {
            "J": 1.0, "kJ": 1000.0, "cal": 4.184, "kcal": 4184.0, "Wh": 3600.0, "kWh": 3600000.0
        }

try:
    if from_unit == to_unit:
        result = value # No conversion needed if units are the same
    elif unit_category == "온도":
        result = convert_temperature(value, from_unit, to_unit)
    else:
        # Convert 'value' from 'from_unit' to a base unit (e.g., Pa for pressure)
        value_in_base = value * conversions[from_unit]
        # Convert from base unit to 'to_unit'
        result = value_in_base / conversions[to_unit]
            
    st.write(f"변환 결과: **{result:.4f} {to_unit}**")

except Exception as e:
    st.error(f"단위 변환 중 오류가 발생했습니다. 입력 값을 확인해주세요. 오류: {e}")
    st.info("단위 변환은 선택된 카테고리 내에서만 가능합니다.")

st.markdown("---")

# ------------------------------
# Feature 2: Engineering Resource Search & Scrap
# ------------------------------
st.header("2️⃣ 공학 자료 검색 및 스크랩")
st.write("궁금한 공학 개념이나 자료를 검색하고, 필요한 정보를 스크랩하여 저장해 보세요.")

search_query = st.text_input(
    "검색할 공학 자료 키워드를 입력하세요 (예: '열역학 제1법칙', '파이썬 데이터 분석')",
    key="search_query_input"
)
search_button = st.button("자료 검색 및 스크랩 실행", key="search_button")

if search_button and search_query.strip() != "":
    st.info(f"'{search_query}'에 대한 자료를 검색 중입니다...")
    # Generate a Google search URL.
    # Note: For a true "scrap" feature, you'd need to fetch content
    # from the link, which can be complex due to website structures
    # and terms of service. This example simply provides the search link.
    Google Search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}+공학"
    st.markdown(f"**[Google에서 '{search_query}'(을)를 검색하기]({Google Search_url})**", unsafe_allow_html=True)
    st.write("위 링크를 클릭하여 필요한 자료를 찾으신 후, 아래 '나만의 공학 자료 저장소'에 내용을 저장해 주세요.")
elif search_button: # Only show error if button is clicked but query is empty
    st.warning("검색 키워드를 입력해 주세요.")

st.markdown("---")

# ------------------------------
# Feature 3: Personal Engineering Data Storage
# ------------------------------
st.header("3️⃣ 나만의 공학 자료 저장소")
st.write("자신만의 공학 지식과 자료를 체계적으로 저장하고 관리하세요.")

# Input fields for new notes
title = st.text_input("자료 제목을 입력하세요", key="note_title", placeholder="예: 푸리에 변환의 응용")
content = st.text_area("내용을 입력하세요", key="note_content", height=150, placeholder="여기에 자료 내용을 작성하세요...")
link = st.text_input("참고 링크(URL)를 입력하세요 (선택)", key="note_link", placeholder="예: https://www.example.com/공학자료")

# Save button
if st.button("새 자료 저장하기", key="save_note_button"):
    if title.strip() == "" or content.strip() == "":
        st.error("🚫 제목과 내용은 반드시 입력해야 합니다.")
    else:
        st.session_state.notes.append({
            "title": title,
            "content": content,
            "link": link
        })
        save_notes(st.session_state.notes) # Save updated notes to the JSON file
        st.success(f"✔️ '{title}' 자료가 성공적으로 저장되었습니다.")
        # Clear input fields after saving for better UX
        st.session_state.note_title = ""
        st.session_state.note_content = ""
        st.session_state.note_link = ""
        # Re-run the app to reflect changes (optional, but good practice for clearing inputs)
        st.rerun()

st.markdown("---")

# Displaying saved notes
st.subheader("📝 저장된 자료 목록")

if st.session_state.notes:
    # Option to clear all notes
    if st.button("모든 자료 삭제", key="clear_all_notes_button"):
        st.session_state.notes = []
        save_notes(st.session_state.notes)
        st.success("모든 자료가 삭제되었습니다.")
        st.rerun() # Refresh to show empty list

    for i, note in enumerate(st.session_state.notes):
        st.markdown(f"### {i+1}. {note['title']}")
        st.write(note['content'])
        if note['link'].strip() != "":
            st.markdown(f"[🔗 참고 링크]({note['link']})")
        
        # Add a delete button for each note
        if st.button(f"삭제 {note['title']}", key=f"delete_note_{i}"):
            st.session_state.notes.pop(i) # Remove the note from the list
            save_notes(st.session_state.notes) # Save the modified list
            st.success(f"'{note['title']}' 자료가 삭제되었습니다.")
            st.rerun() # Re-run the app to update the displayed list
        
        st.markdown("---")
else:
    st.info("아직 저장된 자료가 없습니다. 새로운 자료를 추가해 보세요!")

st.markdown("---")
st.info("💡 이 앱은 데이터를 'engineering_notes.json' 파일에 로컬로 저장합니다. 앱이 실행되는 동일한 폴더에 파일이 생성됩니다.")
