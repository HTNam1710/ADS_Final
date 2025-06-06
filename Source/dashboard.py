import streamlit as st
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
import pydeck as pdk
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# Load dữ liệu
@st.cache_data
def load_data():
    return pd.read_csv("Data/Final/diem_chuan_full.csv")

df = load_data()
df["Điểm chuẩn"] = df["Điểm chuẩn"].fillna(0)

# Tabs chính
tab1, tab2 = st.tabs(["📊 Phân tích điểm chuẩn", "📚 Gợi ý chọn trường"])

# --------------------------- TAB 1: Dashboard điểm chuẩn tổng quan ---------------------------
st.markdown('<div id="capture-this">', unsafe_allow_html=True)

with tab1:
    col_title, col_button = st.columns([5,1])
    
    # Tiêu đề và nút chụp ảnh
    with col_title:
        st.title("🎓 PHÂN TÍCH ĐIỂM CHUẨN ĐẠI HỌC TẠI VIỆT NAM (2018–2024)")

    with col_button:
        st.write("")  # đẩy nút xuống
        components.html("""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
            <button id="screenshot-button" style="padding:8px 15px; font-size:14px; background-color:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer; margin-bottom:10px;">
                📸 Chụp ảnh
            </button>
            <script>
            document.getElementById("screenshot-button").addEventListener("click", function() {
                var content = document.getElementById('capture-this');  // chụp đúng vùng này
                html2canvas(content).then(function(canvas) {
                    var link = document.createElement('a');
                    link.download = 'dashboard_screenshot.png';
                    link.href = canvas.toDataURL();
                    link.click();
                }).catch(function(error) {
                    console.log('Screenshot error:', error);
                });
            });
            </script>
            """, height=100)



    # Filter line 1: 6 columns đều nhau
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        years = sorted(df["Năm"].dropna().unique())
        default_index = years.index(2024) if 2024 in years else len(years) - 1
        selected_year = st.selectbox("Năm", years, index=default_index)

    with col2:
        regions = ["All"] + sorted(df["Khu vực"].dropna().unique())
        selected_region = st.selectbox("Khu vực", regions)

    with col3:
        selected_method = st.multiselect("Phương thức tuyển sinh", df["Loại điểm"].dropna().unique(), default=None)

    with col4:
        nhom_nganh_options = ["All"] + sorted(df["Nhóm ngành"].dropna().unique())
        selected_nhom_nganh = st.selectbox("Ngành", nhom_nganh_options)

    with col5:
        if selected_nhom_nganh == "All":
            phan_nganh_options = ["All"] + sorted(df["Phân ngành"].dropna().unique())
        else:
            phan_nganh_options = ["All"] + sorted(df[df["Nhóm ngành"] == selected_nhom_nganh]["Phân ngành"].dropna().unique())

        selected_phan_nganh = st.selectbox("Phân ngành", phan_nganh_options)

    with col6:
        if selected_phan_nganh == "All":
            ten_nganh_options = ["All"] + sorted(df["Tên Ngành"].dropna().unique())
        else:
            ten_nganh_options = ["All"] + sorted(df[df["Phân ngành"] == selected_phan_nganh]["Tên Ngành"].dropna().unique())

        selected_ten_nganh = st.selectbox("Tên ngành", ten_nganh_options)

    # Lọc dữ liệu
    df_filtered = df[df["Năm"] == selected_year]

    if selected_region != "All":
        df_filtered = df_filtered[df_filtered["Khu vực"] == selected_region]

    if selected_nhom_nganh != "All":
        df_filtered = df_filtered[df_filtered["Nhóm ngành"] == selected_nhom_nganh]

    if selected_phan_nganh != "All":
        df_filtered = df_filtered[df_filtered["Phân ngành"] == selected_phan_nganh]

    if selected_ten_nganh != "All":
        df_filtered = df_filtered[df_filtered["Tên Ngành"] == selected_ten_nganh]

    if selected_method:
        df_filtered = df_filtered[df_filtered["Loại điểm"].isin(selected_method)]

    # Tính toán chỉ số
    avg_year = df_filtered["Điểm chuẩn"].mean() if not df_filtered.empty else 0
    max_score = df_filtered["Điểm chuẩn"].max() if not df_filtered.empty else 0
    min_score = df_filtered["Điểm chuẩn"].min() if not df_filtered.empty else 0

    # Hiển thị chỉ số (3 metrics)
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Điểm chuẩn trung bình {selected_year}", f"{avg_year:.2f}")
    col2.metric("Điểm chuẩn cao nhất", f"{max_score:.2f}")
    col3.metric("Điểm chuẩn thấp nhất", f"{min_score:.2f}")

    # Bố cục: Map bên trái - Biểu đồ bên phải
    col_left, col_right = st.columns([1.2, 2])

    with col_left:
        st.subheader("🗺️ Bản đồ")
        st.pydeck_chart(
            pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=pdk.ViewState(
                    latitude=16.047079,
                    longitude=108.206230,
                    zoom=5,
                    pitch=0,
                ),
                layers=[],
            )
        )

    with col_right:
        # Top 5 trường có điểm chuẩn cao nhất
        st.subheader("🏫 Top 5 trường có điểm chuẩn cao nhất")
        if not df_filtered.empty:
            # 1. Groupby max
            top5_max = df_filtered.groupby("Tên Trường")["Điểm chuẩn"].max().reset_index()
            # 2. Merge lại để lấy Tên Ngành ứng với điểm đó
            top5_max = pd.merge(top5_max, df_filtered[["Tên Trường", "Tên Ngành", "Điểm chuẩn"]],
                                on=["Tên Trường", "Điểm chuẩn"], how="left").drop_duplicates(subset=["Tên Trường"])
            # 3. Sort và vẽ
            top5_max = top5_max.sort_values(by="Điểm chuẩn", ascending=False).head(5)
            fig_max = px.bar(top5_max, x="Điểm chuẩn", y="Tên Trường", orientation='h',
                            color="Điểm chuẩn", hover_data=["Tên Ngành", "Điểm chuẩn"],
                            color_continuous_scale="Blues", title="Top 5 trường có điểm chuẩn cao nhất")
            fig_max.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_max, use_container_width=True)
        else:
            st.write("Không có dữ liệu phù hợp.")

        # Top 5 trường có điểm chuẩn thấp nhất
        st.subheader("🏫 Top 5 trường có điểm chuẩn thấp nhất")
        if not df_filtered.empty:
            top5_min = df_filtered.groupby("Tên Trường")["Điểm chuẩn"].min().reset_index()
            top5_min = pd.merge(top5_min, df_filtered[["Tên Trường", "Tên Ngành", "Điểm chuẩn"]],
                                on=["Tên Trường", "Điểm chuẩn"], how="left").drop_duplicates(subset=["Tên Trường"])
            top5_min = top5_min.sort_values(by="Điểm chuẩn", ascending=True).head(5)
            fig_min = px.bar(top5_min, x="Điểm chuẩn", y="Tên Trường", orientation='h',
                            color="Điểm chuẩn", hover_data=["Tên Ngành", "Điểm chuẩn"],
                            color_continuous_scale="Reds", title="Top 5 trường có điểm chuẩn thấp nhất")
            fig_min.update_layout(yaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_min, use_container_width=True)
        else:
            st.write("Không có dữ liệu phù hợp.")

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------- TAB 2: Gợi ý chọn trường (để mở rộng sau) ---------------------------
with tab2:
    st.info("🚧 Tính năng gợi ý ngành/trường dựa vào 2024 và mức điểm các bạn dự định sẽ thi sẽ được xây dựng tiếp.")
