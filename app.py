import streamlit as st
import json

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
        return []
    except json.JSONDecodeError:
        st.error("⚠️ 저장된 자료 파일을 읽는 중 오류가 발생했습니다. 새롭게 시작합니다.")
        return []

def save_notes(notes):
    """Saves the current list of notes to the JSON file."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=4, ensure_ascii=False)

if 'notes' not in st.session_state:
    st.session_state.notes = load_notes()

if 'clear_inputs' not in st.session_state:
    st.session_state.clear_inputs = False

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
    value = st.number_input("변환할 값", min_value=0.0, value=1.0, format="%.6f", key="input_value")
    
with col2:
    if unit_category == "길이":
        from_unit = st.selectbox("시작 단위", ["m", "cm", "mm", "km", "inch", "ft"], key="length_from")
        to_unit = st.selectbox("변환할 단위", ["m", "cm", "mm", "km", "inch", "ft"], key="length_to")
        conversions = {
            "m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0, "inch": 0.0254, "ft": 0.3048
        }
    elif unit_category == "질량":
        from_unit = st.selectbox("시작 단위", ["kg", "g", "mg", "ton", "lb"], key="mass_from")
        to_unit = st.selectbox("변환할 단위", ["kg", "g", "mg", "ton", "lb"], key="mass_to")
        conversions = {
            "kg": 1.0, "g": 0.001, "mg": 0.000001, "ton": 1000.0, "lb": 0.453592
        }
    elif unit_category == "온도":
        from_unit = st.selectbox("시작 단위", ["°C", "°F", "K"], key="temp_from")
        to_unit = st.selectbox("변환할 단위", ["°C", "°F", "K"], key="temp_to")
        
        def convert_temperature(val, from_u, to_u):
            if from_u == "°C":
                celsius = val
            elif from_u == "°F":
                celsius = (val - 32) * 5/9
            elif from_u == "K":
                celsius = val - 273.15
            else: 
                return val 

            if to_u == "°C":
                return celsius
            elif to_u == "°F":
                return (celsius * 9/5) + 32
            elif to_u == "K":
                return celsius + 273.15
            else:
                return val

    elif unit_category == "압력":
        from_unit = st.selectbox("시작 단위", ["Pa", "kPa", "MPa", "bar", "psi", "atm"], key="pressure_from")
        to_unit = st.selectbox("변환할 단위", ["Pa", "kPa", "MPa", "bar", "psi", "atm"], key="pressure_to")
        conversions = {
            "Pa": 1.0, "kPa": 1000.0, "MPa": 1000000.0, "bar": 100000.0, "psi": 6894.76, "atm": 101325.0
        }
    elif unit_category == "에너지":
        from_unit = st.selectbox("시작 단위", ["J", "kJ", "cal", "kcal", "Wh", "kWh"], key="energy_from")
        to_unit = st.selectbox("변환할 단위", ["J", "kJ", "cal", "kcal", "Wh", "kWh"], key="energy_to")
        # CORRECTED: Energy conversion factors relative to 'J' (Joule)
        # This matches the structure of other unit categories for consistent conversion logic.
        conversions = {
            "J": 1.0,        # 1 Joule is 1 Joule
            "kJ": 1000.0,    # 1 kiloJoule is 1000 Joules
            "cal": 4.184,    # 1 calorie is 4.184 Joules (thermochemical calorie)
            "kcal": 4184.0,  # 1 kilocalorie is 4184 Joules
            "Wh": 3600.0,    # 1 Watt-hour is 3600 Joules
            "kWh": 3600000.0 # 1 kiloWatt-hour is 3,600,000 Joules
        }

try:
    if from_unit == to_unit:
        result = value
    elif unit_category == "온도": # Corrected the typo from "온度" to "온도"
        result = convert_temperature(value, from_unit, to_unit)
    else:
        value_in_base = value * conversions[from_unit]
        result = value_in_base / conversions[to_unit]
            
    st.markdown(f"**변환 결과:** `{value:.4f} {from_unit}` **=** `{result:.4f} {to_unit}`")

except KeyError:
    st.error("⚠️ 단위 변환 오류: 선택된 단위 조합에 대한 변환 정보를 찾을 수 없습니다. (내부 변환 계수 오류)")
except Exception as e:
    st.error(f"⚠️ 단위 변환 중 예상치 못한 오류가 발생했습니다. 입력 값을 확인해주세요. 오류: {e}")
    st.info("💡 단위 변환은 선택된 카테고리 내에서만 가능합니다.")

st.markdown("---")

# ------------------------------
# Feature 2: Personal Engineering Data Storage
# ------------------------------
st.header("2️⃣ 나만의 공학 자료 저장소")
st.write("자신만의 공학 지식과 자료를 체계적으로 저장하고 관리하세요.")

# Determine initial values for text inputs based on the clear_inputs flag
initial_title = ""
initial_content = ""
initial_link = ""

if st.session_state.clear_inputs:
    initial_title = ""
    initial_content = ""
    initial_link = ""
    st.session_state.clear_inputs = False # Reset flag immediately after using it

# Input fields for new notes
title = st.text_input("자료 제목을 입력하세요", value=initial_title, key="note_title", placeholder="예: 푸리에 변환의 응용 원리")
content = st.text_area("내용을 입력하세요", value=initial_content, height=150, key="note_content", placeholder="여기에 자료 내용을 자세히 작성하세요...")
link = st.text_input("참고 링크(URL)를 입력하세요 (선택)", value=initial_link, key="note_link", placeholder="예: https://www.k-engineer.com/resource")

def save_note_callback():
    """Callback function to handle saving and clearing inputs."""
    if st.session_state.note_title.strip() == "" or st.session_state.note_content.strip() == "":
        st.error("🚫 제목과 내용은 반드시 입력해야 합니다.")
    else:
        st.session_state.notes.append({
            "title": st.session_state.note_title,
            "content": st.session_state.note_content,
            "link": st.session_state.note_link
        })
        save_notes(st.session_state.notes)
        st.success(f"✔️ '{st.session_state.note_title}' 자료가 성공적으로 저장되었습니다.")
        
        st.session_state.clear_inputs = True
        st.rerun()

st.button("➕ 새 자료 저장하기", key="save_note_button", on_click=save_note_callback)

st.markdown("---")

st.subheader("📝 저장된 자료 목록")

if st.session_state.notes:
    def clear_all_notes_callback():
        st.session_state.notes = []
        save_notes(st.session_state.notes)
        st.success("모든 자료가 성공적으로 삭제되었습니다.")
        st.rerun()

    if st.button("🗑️ 모든 자료 삭제", key="clear_all_notes_button", on_click=clear_all_notes_callback):
        pass

    for i, note in enumerate(st.session_state.notes):
        st.markdown(f"### {i+1}. {note['title']}")
        st.write(note['content'])
        if note['link'].strip() != "":
            st.markdown(f"[🔗 참고 링크]({note['link']})")
        
        def delete_single_note_callback(index_to_delete):
            st.session_state.notes.pop(index_to_delete)
            save_notes(st.session_state.notes)
            st.success(f"자료가 삭제되었습니다.")
            st.rerun()

        st.button(f"삭제: '{note['title']}'", key=f"delete_note_{i}", on_click=delete_single_note_callback, args=(i,))
        
        st.markdown("---")
else:
    st.info("아직 저장된 자료가 없습니다. 새로운 자료를 추가해 보세요!")

st.markdown("---")
st.info("💡 이 앱은 데이터를 'engineering_notes.json' 파일에 로컬로 저장합니다. 앱이 실행되는 동일한 폴더에 파일이 생성됩니다.")
