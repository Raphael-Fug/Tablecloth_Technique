import streamlit as st
import sqlite3
import time
from datetime import datetime

# Khởi tạo kết nối database
conn = sqlite3.connect('ideas.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    idea TEXT
)
''')
conn.commit()

# Khởi tạo session state
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

def get_ideas_by_group(group_id):
    cursor.execute("SELECT idea FROM ideas WHERE group_id = ?", (group_id,))
    return [row[0] for row in cursor.fetchall()]

def get_all_unique_ideas():
    cursor.execute("SELECT DISTINCT idea FROM ideas")
    return [row[0] for row in cursor.fetchall()]

def display_ideas_box(title, ideas, is_center=False):
    box_class = "center-box" if is_center else "idea-box"
    
    # Tạo HTML cho danh sách ý tưởng
    ideas_html = ""
    if ideas:
        ideas_html = "".join([f"<li>{idea}</li>" for idea in ideas])
    else:
        ideas_html = "<li>Chưa có ý tưởng nào.</li>"
    
    # Tạo HTML cho toàn bộ ô
    box_html = f"""
    <div class="{box_class}">
        <div class="box-title">{title}</div>
        <ul class="idea-list">
            {ideas_html}
        </ul>
    </div>
    """
    
    st.markdown(box_html, unsafe_allow_html=True)

# CSS để tạo ô hiển thị giống như trong hình
st.markdown("""
<style>
    .idea-box {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        background-color: #f9f9f9;
        height: 200px;
        overflow-y: auto;
        margin: 10px 0;
    }
    .center-box {
        border: 2px solid #000;
        border-radius: 5px;
        padding: 15px;
        background-color: white;
        height: 350px;
        overflow-y: auto;
        margin: 0 auto;
        position: relative;
        top: 30px; /* Di chuyển ô xuống một chút */
    }
    .box-title {
        color: #555;
        font-size: 16px;
        margin-bottom: 10px;
    }
    .idea-list {
        list-style-type: disc;
        padding-left: 20px;
        margin: 0;
    }
    .idea-list li {
        margin-bottom: 5px;
        white-space: pre-wrap; /* Cho phép hiển thị nhiều dòng */
    }
    .auto-refresh {
        font-size: 12px;
        color: #888;
        text-align: center;
        margin-top: 5px;
    }
    .last-update {
        font-size: 12px;
        color: #888;
        text-align: right;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Tạo sidebar
mode = st.sidebar.selectbox("Chọn chế độ", ["Nhập ý kiến (Nhóm)", "Trình chiếu (Tổng hợp)"])

# Kiểm tra xem đã đến lúc refresh chưa
current_time = datetime.now()
time_diff = (current_time - st.session_state.last_refresh).total_seconds()
if time_diff >= 10 and mode == "Trình chiếu (Tổng hợp)":
    st.session_state.last_refresh = current_time
    st.rerun()

if mode == "Nhập ý kiến (Nhóm)":
    st.header("Nhập ý kiến của nhóm của bạn")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        group = st.selectbox("Chọn nhóm", [1, 2, 3, 4, 5])
    
    idea_key = "idea_input" + str(time.time()) if st.session_state.clear_input else "idea_input"
    idea = st.text_area("Nhập ý kiến", height=150, key=idea_key)
    
    if st.session_state.clear_input:
        st.session_state.clear_input = False
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Thêm ý tưởng", use_container_width=True):
            if idea:
                cursor.execute("INSERT INTO ideas (group_id, idea) VALUES (?, ?)", (group, idea))
                conn.commit()
                st.success("Ý tưởng đã được thêm!")
                st.session_state.clear_input = True
                st.rerun()
            else:
                st.warning("Vui lòng nhập ý tưởng.")

elif mode == "Trình chiếu (Tổng hợp)":
    # Hiển thị thông báo tự động cập nhật
    st.markdown('<div class="auto-refresh">Tự động cập nhật mỗi 10 giây</div>', unsafe_allow_html=True)
    
    # Lấy dữ liệu từ database
    ideas1 = get_ideas_by_group(1)
    ideas2 = get_ideas_by_group(2)
    ideas3 = get_ideas_by_group(3)
    ideas4 = get_ideas_by_group(4)
    ideas5 = get_ideas_by_group(5)
    all_ideas = get_all_unique_ideas()
    
    container = st.container()
    
    # Tạo khoảng trống ở trên
    container.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Hàng 1: Nhóm 1, Nhóm 2 và Nhóm 5
    row1 = container.columns([1, 2, 1])
    
    with row1[0]:
        display_ideas_box("Nhóm 1...", ideas1)
        
    with row1[2]:
        display_ideas_box("Nhóm 2...", ideas2)
    
    with row1[1]:
        display_ideas_box("Tổng hợp sẽ hiển thị ở đây...", all_ideas, is_center=True)
    
    container.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    row2 = container.columns([1, 1, 1])
    
    with row2[0]:
        display_ideas_box("Nhóm 3...", ideas3)
        
    with row2[1]:
        display_ideas_box("Nhóm 4...", ideas4)
        
    with row2[2]:
        display_ideas_box("Nhóm 5...", ideas5)

    current_time = datetime.now()
    st.markdown(f'<div class="last-update">Cập nhật lần cuối: {current_time.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

    # Căn giữa nút xóa dữ liệu
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Xóa toàn bộ dữ liệu", use_container_width=True):
            cursor.execute("DELETE FROM ideas")  # Xóa toàn bộ dữ liệu trong bảng ideas
            conn.commit()
            st.success("Đã xóa toàn bộ dữ liệu!")
            st.rerun()

# Thêm dữ liệu demo trong sidebar
if st.sidebar.checkbox("Thêm dữ liệu demo"):
    demo_idea = st.sidebar.text_area("Nhập ý tưởng mẫu", height=100)
    demo_group = st.sidebar.selectbox("Chọn nhóm mẫu", [1, 2, 3, 4, 5])
    
    if st.sidebar.button("Thêm ý tưởng mẫu"):
        if demo_idea:
            cursor.execute("INSERT INTO ideas (group_id, idea) VALUES (?, ?)", (demo_group, demo_idea))
            conn.commit()
            st.sidebar.success("Đã thêm ý tưởng mẫu!")
        else:
            st.sidebar.warning("Vui lòng nhập ý tưởng mẫu.")
