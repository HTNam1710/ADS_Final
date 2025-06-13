import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from streamlit_echarts import st_echarts

import joblib
import numpy as np

st.set_page_config(layout="wide")

# Load dữ liệu
@st.cache_data
def load_data():
    return pd.read_csv("Data/Final/diem_chuan_full.csv")

df = load_data()
df["Điểm chuẩn"] = df["Điểm chuẩn"].fillna(0)

# Tabs chính
tab1, tab2, tab3 = st.tabs(["📊 Phân tích điểm chuẩn", "📚 Gợi ý chọn trường", "🎓 Gợi Ý Ngành Học"])

# --------------------------- TAB 1: Dashboard điểm chuẩn tổng quan ---------------------------
st.markdown('<div id="capture-this">', unsafe_allow_html=True)

with tab1:
    col_title, col_button = st.columns([5,1])
    
    # Tiêu đề và nút chụp ảnh
    with col_title:
        st.title("🎓 PHÂN TÍCH ĐIỂM CHUẨN ĐẠI HỌC TẠI VIỆT NAM (2018–2024)")

    # with col_button:
    #     st.write("")  # đẩy nút xuống
    #     components.html("""
    #         <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    #         <button id="screenshot-button" style="padding:8px 15px; font-size:14px; background-color:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer; margin-bottom:10px;">
    #             📸 Chụp ảnh
    #         </button>
    #         <script>
    #         document.getElementById("screenshot-button").addEventListener("click", function() {
    #             var content = document.getElementById('capture-this');  // chụp đúng vùng này
    #             html2canvas(content).then(function(canvas) {
    #                 var link = document.createElement('a');
    #                 link.download = 'dashboard_screenshot.png';
    #                 link.href = canvas.toDataURL();
    #                 link.click();
    #             }).catch(function(error) {
    #                 console.log('Screenshot error:', error);
    #             });
    #         });
    #         </script>
    #         """, height=100)



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
    
    # Load lat/lon
    df_latlon = pd.read_csv("Data/Final/school_latlon.csv")

    # Merge lat/lon vào df_filtered
    df_filtered_map = df_filtered.merge(df_latlon, on="Tên Trường", how="left")

    # Lọc các trường có lat/lon
    df_filtered_map_valid = df_filtered_map[df_filtered_map["Latitude"].notna() & df_filtered_map["Longitude"].notna()]

    with col_left:
        st.subheader("🗺️ Bản đồ")

        if not df_filtered_map_valid.empty:
            st.pydeck_chart(
                pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=pdk.ViewState(
                        latitude=16.047079,
                        longitude=108.206230,
                        zoom=5,
                        pitch=0,
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=df_filtered_map_valid,
                            get_position='[Longitude, Latitude]',
                            get_fill_color='[0, 128, 255, 160]',
                            get_radius=10000,
                            pickable=True,
                        )
                    ],
                    tooltip={
                        "html": "<b>Trường:</b> {Tên Trường} <br/>",
                        "style": {
                            "backgroundColor": "steelblue",
                            "color": "white",
                        }
                    }
                )
            )
        else:
            st.write("Không có dữ liệu bản đồ phù hợp.")

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
# --------------------------- TAB 2: Gợi ý chọn trường ---------------------------
with tab2:
    st.markdown("## 📚 THAM KHẢO TRƯỜNG PHÙ HỢP DỰA TRÊN DỮ LIỆU ĐIỂM CHUẨN NĂM 2024")

    # Init session state
    if "current_drill_path" not in st.session_state:
        st.session_state.current_drill_path = []
    if "clicked_node_temp" not in st.session_state:
        st.session_state.clicked_node_temp = None
    if "previous_selected_nhom" not in st.session_state:
        st.session_state.previous_selected_nhom = None
    if "reset_filters" not in st.session_state:
        st.session_state.reset_filters = False

    df_2024 = df[df["Năm"] == 2024].copy()

    # ==== Filter dòng trên cùng ====
    col1, col2, col3, col4 = st.columns(4)

    if st.session_state.reset_filters:
        selected_region = "All"
        selected_method = "All"
        selected_tohop = "All"
        selected_score_range = (float(df_2024["Điểm chuẩn"].min()), float(df_2024["Điểm chuẩn"].max()))
        st.session_state.reset_filters = False
    else:
        selected_region = col1.selectbox("Khu vực", ["All"] + sorted(df_2024["Khu vực"].dropna().unique()), key="region_tab2")
        selected_method = col2.selectbox("Phương thức", ["All"] + sorted(df_2024["Loại điểm"].dropna().unique()), key="method_tab2")
        selected_tohop = col3.selectbox("Tổ hợp", ["All"] + sorted(df_2024["Tổ hợp"].dropna().unique()), key="tohop_tab2")

        min_score = float(df_2024["Điểm chuẩn"].min())
        max_score = float(df_2024["Điểm chuẩn"].max())
        selected_score_range = col4.slider(
            "Điểm xét tuyển", min_value=min_score, max_value=max_score,
            value=(min_score, max_score), step=0.05, key="score_tab2"
        )

    # ==== Apply filter ====
    df_filtered = df_2024[
        (df_2024["Điểm chuẩn"] >= selected_score_range[0]) &
        (df_2024["Điểm chuẩn"] <= selected_score_range[1])
    ]
    if selected_region != "All":
        df_filtered = df_filtered[df_filtered["Khu vực"] == selected_region]
    if selected_method != "All":
        df_filtered = df_filtered[df_filtered["Loại điểm"] == selected_method]
    if selected_tohop != "All":
        df_filtered = df_filtered[df_filtered["Tổ hợp"] == selected_tohop]

    # ==== Filter nhóm ngành ====
    col_n1 = st.columns(1)[0]

    nhom_nganh_list = ["All"] + sorted(df_filtered["Nhóm ngành"].dropna().unique())
    selected_nhom = col_n1.selectbox("Nhóm ngành", nhom_nganh_list, key="nhom_nganh_selectbox")

    # ==== Reset drill path khi đổi nhóm ngành ====
    if st.session_state.previous_selected_nhom != selected_nhom:
        st.session_state.current_drill_path = []
        st.session_state.clicked_node_temp = None
        st.session_state.previous_selected_nhom = selected_nhom

    if selected_nhom == "All":
        df_nhom = df_filtered.copy()
    else:
        df_nhom = df_filtered[df_filtered["Nhóm ngành"] == selected_nhom]

    # ==== Show Metrics trên top ====
    df_drill_current = df_nhom.copy()
    if len(st.session_state.current_drill_path) >= 1:
        df_drill_current = df_drill_current[df_drill_current["Phân ngành"] == st.session_state.current_drill_path[0]]
    if len(st.session_state.current_drill_path) >= 2:
        df_drill_current = df_drill_current[df_drill_current["Tên Trường"] == st.session_state.current_drill_path[1]]
    if len(st.session_state.current_drill_path) >= 3:
        if st.session_state.current_drill_path[2].startswith("Điểm:"):
            # Chỉ giữ lại filter đến Tên Ngành hiện tại:
            selected_nganh = st.session_state.current_drill_path[2].split("(Tổ hợp")[0].replace("Điểm: ","").strip()
            # Lấy từ path[2-1]:
            selected_nganh = st.session_state.current_drill_path[2-1]
            df_drill_current = df_drill_current[df_drill_current["Tên Ngành"] == selected_nganh]
        else:
            df_drill_current = df_drill_current[df_drill_current["Tên Ngành"] == st.session_state.current_drill_path[2]]


    colm1, colm2, colm3, colm4 = st.columns(4)
    colm1.metric("Số phân ngành", df_drill_current["Phân ngành"].nunique())
    colm2.metric("Số ngành phù hợp", df_drill_current["Tên Ngành"].nunique())
    colm3.metric("Số trường", df_drill_current["Tên Trường"].nunique())
    colm4.metric("Điểm chuẩn trung bình", f"{df_drill_current['Điểm chuẩn'].mean():.2f}" if not df_drill_current.empty else "0.00")

    # ==== Breadcrumb + Button Reset ====
    st.markdown("### 🧭 Sankey:")

    col_breadcrumb = st.container()
    col_breadcrumb_cols = col_breadcrumb.columns(len(st.session_state.current_drill_path) + 1)

    if col_breadcrumb_cols[0].button("Số ngành phù hợp"):
        st.session_state.current_drill_path = []
        st.rerun()

    for i, node in enumerate(st.session_state.current_drill_path):
        if col_breadcrumb_cols[i+1].button(node):
            st.session_state.current_drill_path = st.session_state.current_drill_path[:i+1]
            st.rerun()

    if st.button("🔄 Reset toàn bộ"):
        st.session_state.current_drill_path = []
        st.session_state.clicked_node_temp = None
        st.session_state.previous_selected_nhom = "All"
        st.session_state.reset_filters = True
        st.rerun()

    # ==== Build Sankey ====
    from streamlit_echarts import st_echarts

    if df_nhom.empty:
        st.warning("Không có dữ liệu phù hợp để hiển thị Sankey.")
    else:
        sankey_nodes = []
        sankey_links = []
        node_names = set()

        def add_node(name):
            if name not in node_names:
                sankey_nodes.append({"name": name})
                node_names.add(name)

        curveness = 0.3 if df_nhom.shape[0] < 200 else 0.2
        TOP_N = 10
        drill_depth = len(st.session_state.current_drill_path)

        if drill_depth == 0:
            add_node("Số ngành phù hợp")
            phan_nganh_count = df_nhom.groupby("Phân ngành")["Tên Ngành"].nunique().reset_index()
            phan_nganh_count = phan_nganh_count.sort_values(by="Tên Ngành", ascending=False).head(TOP_N)
            for _, row in phan_nganh_count.iterrows():
                add_node(row["Phân ngành"])
                sankey_links.append({
                    "source": "Số ngành phù hợp",
                    "target": row["Phân ngành"],
                    "value": int(row["Tên Ngành"])
                })

        elif drill_depth == 1:
            selected_phan = st.session_state.current_drill_path[0]
            add_node("Số ngành phù hợp")
            add_node(selected_phan)
            sankey_links.append({
                "source": "Số ngành phù hợp",
                "target": selected_phan,
                "value": int(df_nhom[df_nhom["Phân ngành"] == selected_phan]["Tên Ngành"].nunique())
            })

            df_sub_phan = df_nhom[df_nhom["Phân ngành"] == selected_phan]
            truong_count = df_sub_phan.groupby("Tên Trường")["Tên Ngành"].nunique().reset_index()
            truong_count = truong_count.sort_values(by="Tên Ngành", ascending=False).head(TOP_N)

            for _, row_truong in truong_count.iterrows():
                add_node(row_truong["Tên Trường"])
                sankey_links.append({
                    "source": selected_phan,
                    "target": row_truong["Tên Trường"],
                    "value": int(row_truong["Tên Ngành"])
                })

        elif drill_depth == 2:
            selected_phan = st.session_state.current_drill_path[0]
            selected_truong = st.session_state.current_drill_path[1]

            add_node("Số ngành phù hợp")
            add_node(selected_phan)
            add_node(selected_truong)

            sankey_links.append({
                "source": "Số ngành phù hợp",
                "target": selected_phan,
                "value": int(df_nhom[df_nhom["Phân ngành"] == selected_phan]["Tên Ngành"].nunique())
            })
            sankey_links.append({
                "source": selected_phan,
                "target": selected_truong,
                "value": int(df_nhom[
                    (df_nhom["Tên Trường"] == selected_truong) & (df_nhom["Phân ngành"] == selected_phan)
                ]["Tên Ngành"].nunique())
            })

            df_sub_truong = df_nhom[
                (df_nhom["Tên Trường"] == selected_truong) & (df_nhom["Phân ngành"] == selected_phan)
            ]
            df_sub_truong_unique = df_sub_truong.drop_duplicates(subset=["Tên Ngành", "Tổ hợp", "Điểm chuẩn"])

            nganh_count = df_sub_truong_unique.groupby("Tên Ngành").size().reset_index(name="Số dòng")
            nganh_count = nganh_count.sort_values(by="Số dòng", ascending=False).head(TOP_N)

            for _, row_nganh in nganh_count.iterrows():
                add_node(row_nganh["Tên Ngành"])
                sankey_links.append({
                    "source": selected_truong,
                    "target": row_nganh["Tên Ngành"],
                    "value": int(row_nganh["Số dòng"])
                })

        elif drill_depth == 3:
            selected_phan = st.session_state.current_drill_path[0]
            selected_truong = st.session_state.current_drill_path[1]
            selected_nganh = st.session_state.current_drill_path[2]

            add_node("Số ngành phù hợp")
            add_node(selected_phan)
            add_node(selected_truong)
            add_node(selected_nganh)

            sankey_links.append({
                "source": "Số ngành phù hợp",
                "target": selected_phan,
                "value": int(df_nhom[df_nhom["Phân ngành"] == selected_phan]["Tên Ngành"].nunique())
            })
            sankey_links.append({
                "source": selected_phan,
                "target": selected_truong,
                "value": int(df_nhom[
                    (df_nhom["Tên Trường"] == selected_truong) & (df_nhom["Phân ngành"] == selected_phan)
                ]["Tên Ngành"].nunique())
            })
            sankey_links.append({
                "source": selected_truong,
                "target": selected_nganh,
                "value": int(df_nhom[
                    (df_nhom["Tên Ngành"] == selected_nganh) & (df_nhom["Tên Trường"] == selected_truong) & (df_nhom["Phân ngành"] == selected_phan)
                ]["Điểm chuẩn"].count())
            })

            df_sub_nganh = df_nhom[
                (df_nhom["Tên Ngành"] == selected_nganh) & (df_nhom["Tên Trường"] == selected_truong) & (df_nhom["Phân ngành"] == selected_phan)
            ]
            df_sub_nganh = df_sub_nganh.drop_duplicates(subset=["Tên Ngành", "Tổ hợp", "Điểm chuẩn"])

            for _, row in df_sub_nganh.iterrows():
                score_label = f"Điểm: {row['Điểm chuẩn']:.2f} (Tổ hợp {row['Tổ hợp']})"
                add_node(score_label)
                sankey_links.append({
                    "source": selected_nganh,
                    "target": score_label,
                    "value": 1
                })

        option = {
            "tooltip": {"trigger": "item", "triggerOn": "mousemove | click"},
            "series": [
                {
                    "type": "sankey",
                    "orient": "horizontal",
                    "layout": "sankey",
                    "layoutIterations": 32,
                    "nodeWidth": 20,
                    "nodeGap": 20,
                    "label": {
                        "show": True,
                        "fontSize": 12,
                        "color": "#fff",
                        "overflow": "truncate",
                        "width": 220
                    },
                    "data": sankey_nodes,
                    "links": sankey_links,
                    "emphasis": {"focus": "adjacency"},
                    "lineStyle": {
                        "color": "gradient",
                        "curveness": curveness
                    }
                }
            ]
        }

        events = {"click": "function(params) { return params.name; }"}
        clicked_node_temp = st_echarts(option, height="600px", events=events)

        if clicked_node_temp is not None:
            st.session_state.clicked_node_temp = clicked_node_temp

        # Process clicked node
        if st.session_state.clicked_node_temp is not None:
            node_name = st.session_state.clicked_node_temp
            path = st.session_state.current_drill_path

            if len(path) == 0 and node_name in list(df_nhom["Phân ngành"].dropna().unique()):
                st.session_state.current_drill_path = [node_name]
            elif len(path) == 1 and node_name in list(df_nhom["Tên Trường"].dropna().unique()) and (len(path) < 2 or node_name != path[1]):
                st.session_state.current_drill_path.append(node_name)
            elif len(path) == 2 and node_name in list(df_nhom["Tên Ngành"].dropna().unique()) and (len(path) < 3 or node_name != path[2]):
                st.session_state.current_drill_path.append(node_name)
            elif len(path) == 3 and node_name.startswith("Điểm:"):
                st.session_state.current_drill_path = []

            st.session_state.clicked_node_temp = None
            st.rerun()

    # ==== Tổ hợp môn + Thông tin nhóm ngành ====
    col_bot_left, col_bot_right = st.columns([3, 1])

    with col_bot_left:
        st.subheader("📚 Tổ hợp tuyển sinh phổ biến nhất")

        # Fix: check có cột Tổ hợp + df_drill_current không empty
        if not df_drill_current.empty and "Tổ hợp" in df_drill_current.columns:
            df_tohop = df_drill_current.copy()
            df_tohop["Tổ hợp"] = df_tohop["Tổ hợp"].str.split(";")
            df_tohop = df_tohop.explode("Tổ hợp").dropna()
            df_tohop["Tổ hợp"] = df_tohop["Tổ hợp"].str.strip()

            count_tohop = df_tohop["Tổ hợp"].value_counts().reset_index()
            count_tohop.columns = ["Tổ hợp", "Số ngành xét tuyển"]

            fig_bar = px.bar(count_tohop, x="Số ngành xét tuyển", y="Tổ hợp", orientation='h',
                            color="Số ngành xét tuyển", color_continuous_scale="Purples")
            fig_bar.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("Không có dữ liệu phù hợp.")

    with col_bot_right:
        st.subheader("ℹ️ Thông tin nhóm ngành")

        # Fix: show đúng Phân ngành hiện tại nếu có
        if len(st.session_state.current_drill_path) >= 1:
            nhom_display = st.session_state.current_drill_path[0]
        else:
            nhom_display = selected_nhom

        st.write(f"**Nhóm ngành:** {nhom_display}")

        if not df_drill_current.empty:
            st.metric("Điểm chuẩn cao nhất", f"{df_drill_current['Điểm chuẩn'].max():.2f}")
            st.metric("Điểm chuẩn thấp nhất", f"{df_drill_current['Điểm chuẩn'].min():.2f}")
        else:
            st.metric("Điểm chuẩn cao nhất", "0.00")
            st.metric("Điểm chuẩn thấp nhất", "0.00")

# --------------------------- TAB 3: Gợi ý ngành học phù hợp ---------------------------
reduced_df = pd.read_csv('model/reduced_df.csv')

# Mapping ngành → list các trường có ngành đó
major_to_schools = (
    reduced_df.groupby('Tên ngành trúng tuyển')['Tên trường trúng tuyển']
    .apply(lambda x: list(pd.unique(x)))
    .to_dict()
)

with tab3:
    st.markdown("## 🎓 GỢI Ý NGÀNH HỌC PHÙ HỢP")
    st.markdown("#### ✨ Hệ thống sẽ gợi ý các ngành học phù hợp dựa trên điểm bạn nhập vào các môn thi tốt nghiệp THPT.")
    st.markdown("---")

    # Load model & encoder & feature_cols
    clf = joblib.load('model/clf_multilabel.pkl')
    mlb = joblib.load('model/mlb_majors.pkl')
    feature_cols = joblib.load('model/score.pkl')

    # Thứ tự môn
    ordered_subjects = [
        'Toán', 'Văn', 'Ngoại ngữ',
        'Lí', 'Hóa', 'Sinh',
        'Sử', 'Địa', 'GDCD'
    ]

    # ==== Form nhập điểm ====
    with st.form("score_form"):
        st.write("### ✏️ Nhập điểm các môn (thang điểm 10):")

        input_data = []

        num_cols = 3
        for i in range(0, len(ordered_subjects), num_cols):
            cols = st.columns(num_cols)
            for j, subject in enumerate(ordered_subjects[i:i+num_cols]):
                with cols[j]:
                    score = st.number_input(
                        f"{subject}",
                        min_value=0.0, max_value=10.0, value=5.0, step=0.1,
                        key=f"{subject}_input"
                    )
                    input_data.append(score)

        # Chọn số ngành muốn gợi ý
        top_n = st.slider("Số ngành muốn gợi ý (Top N):", min_value=1, max_value=10, value=5, step=1)

        # Submit button
        submit_button = st.form_submit_button("🚀 Dự đoán ngành phù hợp")

    # ==== Dự đoán khi submit form ====
    if submit_button:
        with st.spinner("⏳ Đang phân tích và gợi ý ngành phù hợp..."):
            X_input = np.array(input_data).reshape(1, -1)
            # predict_proba: lấy xác suất từng ngành
            y_pred_proba = np.array([est.predict_proba(X_input)[:,1] for est in clf.estimators_]).T[0]

            # Lấy top N ngành có xác suất cao nhất
            top_indices = y_pred_proba.argsort()[::-1][:top_n]
            top_scores = y_pred_proba[top_indices]
            top_majors = mlb.classes_[top_indices]

        st.markdown("---")
        st.success(f"🎓 Top {top_n} ngành học gợi ý dành cho bạn:")

        # # ==== Giải thích cách tính độ phù hợp ====
        # st.markdown("""
        # ### ❓ Cách hiểu "độ phù hợp", "bias" và "đóng góp từng môn":

        # - Mỗi ngành có 1 mô hình Logistic Regression riêng.
        # - Công thức:  
        # `score_raw = Tổng đóng góp các môn + bias`
        # - Độ phù hợp = `sigmoid(score_raw) = 1 / (1 + exp(-score_raw))`
        # - **Bias** = ngưỡng ban đầu của ngành:
        #     - Nếu âm → ngành mặc định khó phù hợp → cần đóng góp các môn tốt để được chọn.
        #     - Nếu dương → ngành mặc định dễ phù hợp hơn.
        # - **Vì sao bias của nhiều ngành trong model này thường âm?**
        #     - Đây là bài toán **multi-label** với rất nhiều ngành (~345 ngành).
        #     - Trong dữ liệu, mỗi học sinh chỉ trúng tuyển 1–2 ngành → các ngành còn lại là 0.
        #     - Do đó, khi học mô hình, Logistic Regression sẽ học rằng **mặc định P(y=1) của đa số ngành là rất thấp** → bias sẽ bị đẩy về âm → tránh predict sai dương cho các ngành không phù hợp.
        # - **Hệ số môn**: trọng số của mỗi môn do mô hình học từ dữ liệu, phản ánh mức độ và chiều hướng ảnh hưởng của môn lên độ phù hợp với ngành:
        #     - Hệ số dương → môn càng cao → càng giúp tăng độ phù hợp.
        #     - Hệ số âm → môn càng cao → càng làm giảm độ phù hợp.
        # - Đóng góp môn = `Điểm môn × Hệ số môn` → tác động thực tế của môn vào việc chọn ngành.
        # - **Model luôn chọn ngành có độ phù hợp (P(y=1)) cao nhất, không chỉ dựa vào bias.**

        # """)

        # ==== Hiển thị từng ngành + giải thích ====
        def highlight_contrib(val):
            color = 'green' if val > 0 else 'red'
            return f'color: {color}'

        for i, (major, score, idx) in enumerate(zip(top_majors, top_scores, top_indices)):
            # ==== Chọn trường phù hợp với ngành ====
            schools = major_to_schools.get(major, [])
            if schools:
                # Ưu tiên: lấy trường xuất hiện nhiều nhất trong reduced_df cho ngành này
                selected_school = pd.Series(schools).value_counts().idxmax()
            else:
                selected_school = "Không rõ trường"

            # ==== Hiển thị Trường + Ngành + độ phù hợp ====
            st.markdown(f"### {i+1}. **{selected_school} - {major}** &nbsp; _({score:.2%} độ phù hợp)_")

            # ==== Phần giải thích như cũ ====
            estimator = clf.estimators_[idx]
            coef = estimator.coef_[0]
            intercept = estimator.intercept_[0]
            contributions = X_input[0] * coef

            explain_df = pd.DataFrame({
                'Môn': ordered_subjects,
                'Điểm môn': X_input[0],
                'Hệ số trọng số': coef,
                'Đóng góp vào ngành': contributions
            })

            st.markdown("**🧐 Đóng góp từng môn:**")
            st.table(explain_df.style.format({
                'Điểm môn': '{:.1f}',
                'Hệ số trọng số': '{:+.2f}',
                'Đóng góp vào ngành': '{:+.2f}'
            }).applymap(highlight_contrib, subset=['Đóng góp vào ngành']))

            st.markdown(f"*Bias ngành (intercept): {intercept:+.2f}*")
            st.markdown("---")