import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- 頁面全域設定 ---
st.set_page_config(page_title="建築結構專業整合系統 Pro", layout="wide", initial_sidebar_state="expanded")

st.title("🏢 建築結構設計系統 Professional")
st.markdown("##### 集成 基地分析(V1) / 幾何規劃(V2) / 結構計算(V3) / 成本估算(V4)")
st.markdown("---")

# ==========================================
# 側邊欄：全域核心參數 (Global Parameters)
# 這些參數在所有分頁都會用到，所以固定在左邊
# ==========================================
with st.sidebar:
    st.header("🎛️ 核心參數控制")
    
    st.subheader("1. 基地規模")
    land_width = st.number_input("基地面寬 (m)", value=12.0, step=0.5)
    land_depth = st.number_input("基地深度 (m)", value=20.0, step=0.5)
    land_area = land_width * land_depth
    st.info(f"基地面積: {land_area:.2f} m² ({land_area/3.3058:.1f} 坪)")
    
    st.subheader("2. 量體規模")
    floors_above = st.number_input("地上樓層", value=7, min_value=1)
    floors_below = st.number_input("地下樓層", value=2, min_value=0)
    total_floors = floors_above + floors_below
    
    st.subheader("3. 結構網格")
    span_x = st.slider("X向柱距 (m)", 3.0, 12.0, 6.0)
    span_y = st.slider("Y向柱距 (m)", 3.0, 12.0, 5.0)

# --- 分頁導航 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 基地與法規 (Site)", 
    "📐 平面配置 (Layout)", 
    "🛡️ 載重分析 (Analysis)", 
    "💰 配筋與估價 (Cost)"
])

# ==========================================
# 分頁 1: 基地與使用者邏輯 (保留 V1 的地圖與詳細邏輯)
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🌍 地理環境設定")
        lat = st.number_input("緯度 (Latitude)", value=25.0330, format="%.4f")
        lon = st.number_input("經度 (Longitude)", value=121.5654, format="%.4f")
        
        st.subheader("👥 使用者需求邏輯")
        count_adult = st.number_input("一般成人", 0, 1000, 10)
        count_elder = st.number_input("高齡長者", 0, 1000, 2)
        count_disabled = st.number_input("身障/輪椅", 0, 1000, 0)
        count_child = st.number_input("幼童", 0, 1000, 0)
        
        # V1 的智慧邏輯判斷
        st.info("👇 系統自動生成的設計規範：")
        constraints = []
        if count_disabled > 0 or count_elder > 0:
            st.error("🚨 **無障礙規範啟動**：需配置坡道(1:12)、浴廁扶手、門寬>90cm。")
        else:
            st.write("- 無特殊無障礙需求")
            
        if count_child > 0:
            st.warning("👶 **幼童安全規範啟動**：欄杆防墜間隙<10cm、插座安全保護。")
        else:
            st.write("- 無特殊幼童防護需求")

    with col2:
        st.subheader("🗺️ 基地位置預覽")
        # V1 的地圖功能回歸
        map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
        st.map(map_data, zoom=15)
        
        st.subheader("📊 法規檢討")
        c1, c2 = st.columns(2)
        with c1:
            cov_ratio = st.slider("法定建蔽率 (%)", 30, 100, 60)
            max_footprint = land_area * (cov_ratio/100)
            st.metric("單層最大建築面積", f"{max_footprint:.1f} m²")
        with c2:
            vol_ratio = st.number_input("法定容積率 (%)", 100, 1000, 240)
            max_vol_area = land_area * (vol_ratio/100)
            st.metric("法定容積總樓地板", f"{max_vol_area:.1f} m²")

# ==========================================
# 分頁 2: 結構平面配置 (保留 V2 的繪圖與警告)
# ==========================================
with tab2:
    st.subheader("📐 結構平面配置預覽")
    
    col_layout, col_info = st.columns([3, 1])
    
    with col_layout:
        # V2 的繪圖引擎
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 畫基地紅框
        site_rect = patches.Rectangle((0, 0), land_width, land_depth, 
                                      linewidth=2, edgecolor='red', facecolor='none', linestyle='--', label='基地範圍')
        ax.add_patch(site_rect)
        
        # 計算柱位
        nx = int(land_width // span_x) + 1
        ny = int(land_depth // span_y) + 1
        # 強制邏輯：避免最後跨距太小
        if (nx-1)*span_x < land_width*0.8: nx += 1
        if (ny-1)*span_y < land_depth*0.8: ny += 1
        
        xs = np.linspace(0, land_width - 0.6, nx) # 預設0.6m柱寬做圖
        ys = np.linspace(0, land_depth - 0.6, ny)
        
        total_cols = 0
        for x in xs:
            for y in ys:
                # 畫柱子
                col_p = patches.Rectangle((x, y), 0.6, 0.6, facecolor='#444444', edgecolor='black')
                ax.add_patch(col_p)
                total_cols += 1
                # 畫樑線 (示意)
                if x > 0: ax.plot([x-span_x+0.6, x], [y+0.3, y+0.3], color='blue', alpha=0.3, linewidth=1)
                if y > 0: ax.plot([x+0.3, x+0.3], [y-span_y+0.6, y], color='blue', alpha=0.3, linewidth=1)

        ax.set_xlim(-2, land_width + 2)
        ax.set_ylim(-2, land_depth + 2)
        ax.set_aspect('equal')
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.set_title(f"結構平面圖 (Grid Plan) - {land_width}m x {land_depth}m")
        st.pyplot(fig)
        
    with col_info:
        st.write("#### 配置統計")
        st.metric("總柱數", f"{total_cols} 支")
        st.metric("X向實際跨距", f"{land_width/(nx-1):.2f} m")
        st.metric("Y向實際跨距", f"{land_depth/(ny-1):.2f} m")
        
        st.write("#### 設計建議")
        actual_span = max(land_width/(nx-1), land_depth/(ny-1))
        if actual_span > 8.0:
            st.error("⚠️ 跨距過大 (>8m)！建議增加柱子或改用鋼骨(SC)。")
        elif actual_span < 4.0:
            st.warning("⚠️ 跨距過密 (<4m)，影響空間使用。")
        else:
            st.success("✅ 跨距適中 (RC結構)。")

# ==========================================
# 分頁 3: 結構安全檢核 (保留 V3 的互動紅綠燈)
# ==========================================
with tab3:
    st.subheader("🛡️ 結構載重與安全性檢核")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("🛠️ 1. 材料與斷面設定")
        fc = st.selectbox("混凝土強度 f'c", [210, 280, 350, 420], index=1)
        col_w = st.slider("柱寬 (cm)", 50, 120, 60, step=10)
        col_d = st.slider("柱深 (cm)", 50, 120, 60, step=10)
    
    # 計算核心
    trib_area = span_x * span_y
    # 載重：(靜載重600 + 活載重200) * 樓層數 * 面積
    total_load_ton = (trib_area * 900 * total_floors) / 1000.0
    # 強度：0.65 * 0.85 * fc * Ag
    col_ag = col_w * col_d
    capacity_ton = (0.65 * 0.85 * fc * col_ag) / 1000.0
    ratio = total_load_ton / capacity_ton
    is_safe = ratio < 1.0
    
    with c2:
        st.warning("⚖️ 2. 載重分析 (最不利柱)")
        st.metric("單柱負擔面積", f"{trib_area:.1f} m²")
        st.metric("總垂直載重 (Pu)", f"{total_load_ton:.1f} ton", f"{total_floors}層樓加總")
        
    with c3:
        if is_safe:
            st.success("✅ 3. 安全性判定：通過")
            st.metric("柱容許強度 (Pn)", f"{capacity_ton:.1f} ton")
            st.markdown(f"**應力比：{ratio:.2f}**")
            st.progress(ratio)
        else:
            st.error("❌ 3. 安全性判定：失敗")
            st.metric("柱容許強度 (Pn)", f"{capacity_ton:.1f} ton")
            st.markdown(f"**應力比：{ratio:.2f}** (超過 1.0)")
            st.progress(1.0)
            st.write("👉 建議：加大柱尺寸 或 提高混凝土強度")

    st.markdown("---")
    # V3 的視覺化紅綠燈圖
    st.write("#### 🔍 結構平面應力圖 (Stress Map)")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    site_rect = patches.Rectangle((0, 0), land_width, land_depth, fill=False, edgecolor='#aaa')
    ax2.add_patch(site_rect)
    
    center_x = xs[len(xs)//2]
    center_y = ys[len(ys)//2]
    
    for x in xs:
        for y in ys:
            # 中央柱最危險，顯示真實狀態
            if x == center_x and y == center_y:
                color = 'green' if is_safe else 'red'
                ax2.text(x, y+0.5, "Critical", color='red', ha='center', fontsize=8)
            else:
                # 邊柱通常負擔較小，這裡簡化假設邊柱只有一半載重
                color = 'green' 
            
            rect = patches.Rectangle((x, y), col_w/100, col_d/100, facecolor=color, edgecolor='black')
            ax2.add_patch(rect)
    
    ax2.set_xlim(-1, land_width+1)
    ax2.set_ylim(-1, land_depth+1)
    ax2.set_aspect('equal')
    ax2.axis('off') # 不顯示座標軸比較乾淨
    ax2.set_title("紅燈=危險, 綠燈=安全")
    st.pyplot(fig2)

# ==========================================
# 分頁 4: 配筋與估價 (保留 V4 的斷面圖與詳細算表)
# ==========================================
with tab4:
    st.subheader("💰 配筋詳圖與造價估算")
    
    if not is_safe:
        st.error("⚠️ 前一步驟「結構檢核」未通過，請先修正結構設計（加大柱子）後再來估價。")
    else:
        col_detail, col_cost = st.columns(2)
        
        with col_detail:
            st.info("🔧 柱斷面配筋設計")
            rebar_size = st.selectbox("主筋號數", ["#6 (D19)", "#7 (D22)", "#8 (D25)", "#10 (D32)"], index=2)
            
            # 計算鋼筋支數
            bar_areas = {"#6 (D19)": 2.87, "#7 (D22)": 3.87, "#8 (D25)": 5.07, "#10 (D32)": 7.94}
            one_area = bar_areas[rebar_size]
            min_steel = col_ag * 0.01 # 1%
            num_bars = int(np.ceil(min_steel / one_area))
            if num_bars < 4: num_bars = 4
            if num_bars % 2 != 0: num_bars += 1
            
            # V4 的斷面圖繪製
            fig3, ax3 = plt.subplots(figsize=(5, 5))
            # 混凝土
            ax3.add_patch(patches.Rectangle((0,0), col_w, col_d, facecolor='#dddddd', edgecolor='black', linewidth=2))
            # 箍筋
            ax3.add_patch(patches.Rectangle((4,4), col_w-8, col_d-8, fill=False, edgecolor='blue', linestyle='--'))
            # 鋼筋點 (示意畫4角+文字)
            corners = [(4,4), (col_w-4, 4), (col_w-4, col_d-4), (4, col_d-4)]
            for c in corners:
                ax3.add_patch(patches.Circle(c, 1.5, color='red'))
            
            ax3.text(col_w/2, col_d/2, f"{num_bars} - {rebar_size}", ha='center', va='center', fontsize=20, color='red', fontweight='bold')
            ax3.set_xlim(-5, col_w+5)
            ax3.set_ylim(-5, col_d+5)
            ax3.axis('off')
            st.pyplot(fig3)
            st.success(f"配筋結果：需配置 {num_bars} 根 {rebar_size} (鋼筋比 {(num_bars*one_area/col_ag)*100:.2f}%)")

        with col_cost:
            st.info("💵 工程造價預算書")
            price_c = st.number_input("混凝土單價 ($/m³)", value=2500)
            price_s = st.number_input("鋼筋單價 ($/ton)", value=28000)
            
            # 精細算量
            # 1. 結構混凝土量 (柱+樑板)
            # 假設樓板厚15cm + 樑佔比 = 平均厚度 25cm
            vol_slab = land_area * total_floors * 0.25
            vol_col = (col_w/100 * col_d/100) * 3.2 * total_cols * total_floors
            total_vol = vol_slab + vol_col
            
            # 2. 鋼筋量 (經驗值 180kg/m3)
            total_steel_ton = (total_vol * 180) / 1000.0
            
            # 3. 總價
            cost_total = (total_vol * price_c) + (total_steel_ton * price_s)
            
            # 顯示報表
            df_cost = pd.DataFrame({
                "項目": ["混凝土工程", "鋼筋工程", "結構體總計"],
                "數量": [f"{total_vol:.1f} m³", f"{total_steel_ton:.1f} ton", "-"],
                "預估費用": [f"${total_vol*price_c:,.0f}", f"${total_steel_ton*price_s:,.0f}", f"${cost_total:,.0f}"]
            })
            st.table(df_cost)
            
            st.write("---")
            st.metric("工程總造價", f"NT$ {cost_total/10000:,.1f} 萬")
            unit_cost = cost_total / (land_area * total_floors / 3.3058)
            st.metric("單坪造價 (參考)", f"NT$ {unit_cost:,.0f} /坪")