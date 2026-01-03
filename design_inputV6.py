import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- 頁面全域設定 ---
st.set_page_config(page_title="建築全流程整合系統 (Master)", layout="wide", initial_sidebar_state="expanded")

st.title("🏢 建築全流程整合系統 Master Edition")
st.markdown("##### 整合：基地氣候(V1+V5) / 平面規劃(V2) / 結構安全(V3) / 總體估價(V4)")
st.markdown("---")

# ==========================================
# 側邊欄：全域核心參數 (Global Control)
# ==========================================
with st.sidebar:
    st.header("🎛️ 核心參數控制")
    
    st.subheader("1. 基地設定")
    # 緯度連動氣候判斷
    lat = st.number_input("基地緯度 (Latitude)", value=25.03, step=1.0, help="正=北緯, 負=南緯, 影響建材建議")
    lon = st.number_input("基地經度 (Longitude)", value=121.56, step=0.01)
    
    land_width = st.number_input("基地面寬 (m)", value=12.0, step=0.5)
    land_depth = st.number_input("基地深度 (m)", value=20.0, step=0.5)
    land_area = land_width * land_depth
    st.info(f"基地面積: {land_area:.1f} m²")
    
    st.subheader("2. 建築規模")
    floors = st.number_input("總樓層數", value=7, min_value=1)
    
    st.subheader("3. 結構網格")
    span_x = st.slider("X向柱距 (m)", 3.0, 12.0, 6.0)
    span_y = st.slider("Y向柱距 (m)", 3.0, 12.0, 5.0)

# --- 核心邏輯函數 ---
def get_climate_zone(latitude):
    """V5 核心：依據緯度判斷氣候帶與對策"""
    abs_lat = abs(latitude)
    if abs_lat < 23.5:
        return "熱帶 (Tropical)", "🔥 高溫多濕", "遮陽、隔熱、通風", "Low-E 雙層玻璃", "淺色 (反射熱)"
    elif abs_lat < 40:
        return "溫帶 (Subtropical)", "🌤️ 四季分明", "適度保溫、季節性遮陽", "雙層中空玻璃", "中性色"
    else:
        return "寒帶 (Cold)", "❄️ 寒冷乾燥", "高度氣密、加強保溫、吸熱", "三層氣密窗", "深色 (吸熱)"

# 執行氣候判斷
climate_zone, climate_desc, strategy, rec_glass, rec_color = get_climate_zone(lat)

# --- 分頁導航 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 基地氣候與建材 (V1+V5)", 
    "📐 平面配置 (V2)", 
    "🛡️ 結構分析 (V3)", 
    "💰 配筋與總估價 (V4)"
])

# ==========================================
# Tab 1: 基地氣候與建材 (V1 + V5 深度整合)
# ==========================================
with tab1:
    col_site, col_mat = st.columns([1, 1])
    
    # --- 左欄：V1 基地與使用者需求 ---
    with col_site:
        st.subheader("🌍 地理與使用者分析")
        
        # 1. 地圖 (V1)
        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=13)
        
        # 2. 使用者邏輯 (V1)
        st.write("#### 使用者需求檢核")
        has_disabled = st.checkbox("包含身障/高齡使用者", value=True)
        has_child = st.checkbox("包含幼童使用者", value=False)
        
        tags = []
        if has_disabled: tags.append("🚨 無障礙坡道 (1:12)")
        if has_child: tags.append("👶 防墜欄杆 (>110cm)")
        if abs(lat) < 23.5: tags.append("☀️ 遮陽百葉")
        if abs(lat) > 40: tags.append("🔥 室內暖氣系統")
        
        st.info("設計規範自動生成：\n" + "\n".join([f"- {t}" for t in tags]))

    # --- 右欄：V5 氣候建材決策 ---
    with col_mat:
        st.subheader("🧱 氣候適應性建材決策")
        
        # 1. 氣候診斷 (V5)
        st.success(f"📍 位於 **{climate_zone}** ({lat}°)\n\n特徵：{climate_desc}\n\n策略：{strategy}")
        
        # 2. 建材選擇 (V5)
        st.write("#### 外殼建材選用")
        
        # 玻璃選項與參數
        glass_opts = {
            "一般單層玻璃": {"cost": 1500, "u": 5.8, "note": "便宜但耗能"},
            "雙層中空玻璃": {"cost": 3000, "u": 2.8, "note": "標準隔音隔熱"},
            "Low-E 節能玻璃": {"cost": 4500, "u": 1.6, "note": "熱帶推薦 (擋輻射)"},
            "三層氣密玻璃": {"cost": 6500, "u": 0.8, "note": "寒帶推薦 (防凍)"}
        }
        # 智慧預設值
        def_idx = 2 if abs(lat)<23.5 else (3 if abs(lat)>40 else 1)
        sel_glass = st.selectbox("開窗玻璃系統", list(glass_opts.keys()), index=def_idx)
        
        # 外牆選項
        wall_opts = {
            "一般塗料": {"cost": 1000},
            "隔熱塗料": {"cost": 1800},
            "乾掛石材(含保溫)": {"cost": 8500},
            "金屬包板": {"cost": 6500}
        }
        sel_wall = st.selectbox("外牆裝修材質", list(wall_opts.keys()), index=1)
        
        # 3. 節能評分
        u_val = glass_opts[sel_glass]['u']
        score = 100 - (u_val * 12)
        # 氣候修正
        if abs(lat) > 40 and u_val > 2.0: score -= 20 # 寒帶用爛玻璃扣分
        if abs(lat) < 23.5 and "Low-E" not in sel_glass: score -= 10 # 熱帶沒用Low-E扣分
        
        st.metric("外殼節能評分 (EEWH)", f"{score:.1f} 分", delta="依據 U-Value 計算")
        
        # 4. 外牆造價計算 (存為變數供 Tab4 使用)
        perimeter = (land_width + land_depth) * 2
        area_facade = perimeter * 3.2 * floors * 0.7 # 70% 實牆
        area_window = perimeter * 3.2 * floors * 0.3 # 30% 開窗
        cost_facade_total = (area_facade * wall_opts[sel_wall]['cost']) + (area_window * glass_opts[sel_glass]['cost'])
        
        st.caption(f"外牆預算預估: ${cost_facade_total/10000:.1f} 萬")

# ==========================================
# Tab 2: 平面配置 (V2 完整版)
# ==========================================
with tab2:
    st.subheader("📐 結構平面配置 (Grid Layout)")
    
    t2_c1, t2_c2 = st.columns([3, 1])
    
    with t2_c1:
        # V2 繪圖引擎
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 基地框
        site = patches.Rectangle((0,0), land_width, land_depth, linewidth=2, edgecolor='red', fill=False, linestyle='--')
        ax.add_patch(site)
        
        # 計算柱位
        nx = int(land_width // span_x) + 1
        ny = int(land_depth // span_y) + 1
        # 強制邏輯
        if (nx-1)*span_x < land_width*0.8: nx += 1
        if (ny-1)*span_y < land_depth*0.8: ny += 1
        
        xs = np.linspace(0, land_width-0.6, nx)
        ys = np.linspace(0, land_depth-0.6, ny)
        
        total_cols = 0
        for x in xs:
            for y in ys:
                # 柱子
                ax.add_patch(patches.Rectangle((x, y), 0.6, 0.6, facecolor='#555', edgecolor='black'))
                total_cols += 1
                # 樑線
                if x > 0: ax.plot([x-span_x+0.6, x], [y+0.3, y+0.3], 'b-', alpha=0.3)
                if y > 0: ax.plot([x+0.3, x+0.3], [y-span_y+0.6, y], 'b-', alpha=0.3)
                
        ax.set_xlim(-2, land_width+2)
        ax.set_ylim(-2, land_depth+2)
        ax.set_aspect('equal')
        st.pyplot(fig)
        
    with t2_c2:
        st.metric("總柱數", total_cols)
        actual_sx = land_width/(nx-1)
        actual_sy = land_depth/(ny-1)
        st.metric("X向淨跨距", f"{actual_sx:.2f} m")
        st.metric("Y向淨跨距", f"{actual_sy:.2f} m")
        
        if max(actual_sx, actual_sy) > 8.0:
            st.error("⚠️ 跨距過大 (>8m)")
        elif max(actual_sx, actual_sy) < 4.0:
            st.warning("⚠️ 跨距過密 (<4m)")
        else:
            st.success("✅ 跨距適中")

# ==========================================
# Tab 3: 結構分析 (V3 完整版 - 紅綠燈)
# ==========================================
with tab3:
    st.subheader("🛡️ 結構載重與安全檢核")
    
    # 參數輸入
    c1, c2, c3 = st.columns(3)
    with c1:
        fc = st.selectbox("混凝土強度 f'c", [210, 280, 350, 420], index=1)
        col_w = st.slider("柱寬 (cm)", 50, 120, 60, step=10)
        col_d = st.slider("柱深 (cm)", 50, 120, 60, step=10)
    
    # 計算
    trib_area = actual_sx * actual_sy
    total_load = (trib_area * 900 * floors) / 1000.0 # Ton
    capacity = (0.65 * 0.85 * fc * col_w * col_d) / 1000.0 # Ton
    ratio = total_load / capacity
    is_safe = ratio < 1.0
    
    with c2:
        st.metric("最不利柱載重 (Pu)", f"{total_load:.1f} ton")
        st.metric("柱容許強度 (Pn)", f"{capacity:.1f} ton")
    
    with c3:
        if is_safe:
            st.success(f"✅ 安全 (D/C: {ratio:.2f})")
        else:
            st.error(f"❌ 危險 (D/C: {ratio:.2f})")
            st.write("建議：1.加大柱子 2.提高強度 3.縮小柱距")
            
    # V3 經典紅綠燈圖
    st.write("#### 結構應力分佈圖")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.add_patch(patches.Rectangle((0,0), land_width, land_depth, fill=False, edgecolor='#aaa'))
    
    center_x, center_y = xs[len(xs)//2], ys[len(ys)//2]
    
    for x in xs:
        for y in ys:
            # 只有中間柱顯示真實危險度，邊柱簡化設為安全(綠)
            if x == center_x and y == center_y:
                color = 'green' if is_safe else 'red'
                if not is_safe: ax2.text(x, y+0.8, "FAIL", color='red', ha='center', fontsize=8, fontweight='bold')
            else:
                color = 'green'
            ax2.add_patch(patches.Rectangle((x, y), col_w/100, col_d/100, facecolor=color, edgecolor='black'))
            
    ax2.set_xlim(-1, land_width+1); ax2.set_ylim(-1, land_depth+1)
    ax2.set_aspect('equal'); ax2.axis('off')
    st.pyplot(fig2)

# ==========================================
# Tab 4: 配筋與估價 (V4 + V5成本整合)
# ==========================================
with tab4:
    st.subheader("💰 專案總體估價")
    
    if not is_safe:
        st.error("⚠️ 請先解決 Tab 3 的結構安全問題，才能進行估價。")
    else:
        c_detail, c_cost = st.columns([1, 1])
        
        with c_detail:
            st.info("🔧 柱斷面配筋詳圖")
            # 配筋計算
            rebar_size = st.selectbox("主筋規格", ["#6", "#7", "#8", "#10"], index=2)
            bar_area = {"#6":2.87, "#7":3.87, "#8":5.07, "#10":7.94}[rebar_size]
            num_bars = int(np.ceil((col_w*col_d*0.01)/bar_area))
            if num_bars < 4: num_bars = 4
            if num_bars % 2 != 0: num_bars += 1
            
            # V4 斷面圖
            fig3, ax3 = plt.subplots(figsize=(4, 4))
            ax3.add_patch(patches.Rectangle((0,0), col_w, col_d, facecolor='#ddd', edgecolor='black'))
            ax3.add_patch(patches.Rectangle((4,4), col_w-8, col_d-8, fill=False, edgecolor='blue', linestyle='--'))
            # 簡單畫四個角
            ax3.scatter([4, col_w-4, col_w-4, 4], [4, 4, col_d-4, col_d-4], c='red', s=100)
            ax3.text(col_w/2, col_d/2, f"{num_bars}-{rebar_size}", ha='center', color='red', fontweight='bold', fontsize=15)
            ax3.axis('off'); ax3.set_xlim(-5, col_w+5); ax3.set_ylim(-5, col_d+5)
            st.pyplot(fig3)

        with c_cost:
            st.info("💵 成本計算書")
            p_conc = st.number_input("混凝土單價", value=2500)
            p_steel = st.number_input("鋼筋單價", value=28000)
            
            # 結構算量
            vol_total = (land_area * floors * 0.25) + (col_w/100*col_d/100 * 3.2 * total_cols * floors)
            weight_steel = vol_total * 0.18 # ton
            cost_structure = (vol_total * p_conc) + (weight_steel * p_steel)
            
            # 整合 V1+V5 的外牆造價
            grand_total = cost_structure + cost_facade_total
            
            # 顯示報表
            df = pd.DataFrame({
                "分項工程": ["結構體工程 (混凝土+鋼筋)", "外牆與門窗工程 (Tab1選材)", "總計"],
                "預估費用": [f"${cost_structure:,.0f}", f"${cost_facade_total:,.0f}", f"${grand_total:,.0f}"]
            })
            st.table(df)
            
            st.success(f"🏆 全案總造價： NT$ {grand_total/10000:,.1f} 萬")
            st.metric("單坪造價", f"NT$ {grand_total/(land_area*floors/3.3058):,.0f} /坪")