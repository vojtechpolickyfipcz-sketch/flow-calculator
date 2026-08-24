app_code = '''import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- DATABÁZE PRO STATISTIKY POUŽITÍ ---
DB_FILE = "analytics.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            month_year TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_calculation():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now()
    month_year = now.strftime("%Y-%m")
    c.execute("INSERT INTO calculations (timestamp, month_year) VALUES (?, ?)", (now, month_year))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_FILE)
    total_count = pd.read_sql_query("SELECT COUNT(*) as count FROM calculations", conn).iloc[0]["count"]
    
    current_month_str = datetime.now().strftime("%Y-%m")
    curr_month_count = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM calculations WHERE month_year = ?", 
        conn, 
        params=(current_month_str,)
    ).iloc[0]["count"]
    
    monthly_df = pd.read_sql_query(
        "SELECT month_year as 'Měsíc', COUNT(*) as 'Počet analýz' FROM calculations GROUP BY month_year ORDER BY month_year DESC", 
        conn
    )
    conn.close()
    return total_count, curr_month_count, monthly_df

init_db()

# --- VZHLED STRÁNKY ---
st.set_page_config(page_title="Hydraulický Srovnávač 4.2", layout="wide")

# Vlastní CSS: Šířka sidebaru a zákaz zvětšovacího tlačítka u obrázků
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 405px;
            max-width: 405px;
        }
        /* Skrytí tlačítka pro zvětšení obrázku (fullscreen) */
        button[title="View fullscreen"],
        [data-testid="StyledFullScreenButton"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- HLAVNÍ HLAVIČKA ---
st.title("📊 Pressure drop calculator: Hladká vs. Vlnitá trubka")
st.markdown("Nástroj pro porovnání tlakových ztrát s možností vlastního pojmenování variant. Cílem kalkulátoru je najít řešení a vidět dopad aplikace vlnitých profilů a jejich vliv na zvýšení odporu.")

# --- SIDEBAR (LEVÝ SLOUPEC) ---
with st.sidebar:
    # 1. Logo FIP (zmenšené na 2/3 bez možnosti zvětšení)
    LOGO_FILE = "fip-logo-f-member-of-line-01-04.png"
    if os.path.exists(LOGO_FILE):
        logo_c1, logo_c2, logo_c3 = st.columns([1, 6, 1])
        with logo_c2:
            st.image(LOGO_FILE, width=220)
    else:
        st.markdown("### 🏢 **FIP**")
    
    st.divider()

    # 2. Parametry média
    st.header("💧 Parametry média")
    fluid_name = st.text_input("Název kapaliny", "G12+ Specifikace")
    temp = st.number_input("Teplota měření [°C]", value=22.0, step=0.1)
    
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        dens_val = st.number_input("Hustota", value=1060.0, step=0.1)
    with col_d2:
        dens_unit = st.selectbox("Jednotka", ["kg/m³", "g/cm³"])
    
    visc = st.number_input("Viskozita [Pa·s]", value=0.0030, format="%.4f", step=0.0001)
    
    # 3. Společná geometrie
    st.header("📏 Společná geometrie")
    length = st.number_input("Délka trasy [mm]", value=500.0, step=0.01)
    flow_max = st.slider("Maximální sledovaný průtok [l/min]", 0.5, 100.0, 25.0, 0.5)

    st.divider()

    # 4. Počítadlo využití kalkulátoru
    st.header("📈 Využití kalkulátoru")
    total_c, curr_m_c, monthly_data = get_stats()
    
    stat_c1, stat_c2 = st.columns(2)
    with stat_c1:
        st.metric(label="Tento měsíc", value=curr_m_c)
    with stat_c2:
        st.metric(label="Celkem", value=total_c)
        
    with st.expander("📅 Přehled po měsících"):
        if not monthly_data.empty:
            st.dataframe(monthly_data, use_container_width=True, hide_index=True)
        else:
            st.caption("Zatím nebyly provedeny žádné výpočty.")

final_density = dens_val * 1000 if dens_unit == "g/cm³" else dens_val

# --- HLAVNÍ ČÁST: 4 VARIANTY ---
st.subheader("Konfigurace variant")
cols = st.columns(4)
variants = []

for i in range(4):
    with cols[i]:
        st.info(f"Varianta {i+1}")
        v_label = st.text_input(f"Název/Poznámka", value=f"Varianta {i+1}", key=f"lab{i}", help="Pojmenujte variantu pro legendu grafu (např. NW12 Sinus)")
        v_type = st.selectbox(f"Typ", ["Hladká", "Vlnitá"], index=(1 if i > 0 else 0), key=f"t{i}")
        d_min = st.number_input(f"Vnitřní Ø [mm]", value=12.0, step=0.01, key=f"dmin{i}")
        
        if v_type == "Vlnitá":
            d_max = st.number_input(f"Maximální Ø [mm]", value=15.0, step=0.01, key=f"dmax{i}")
            pitch = st.selectbox(f"Rozteč [mm]", [3.1, 3.3, 3.7, 4.0, 4.65], index=2, key=f"p{i}")
        else:
            d_max = d_min
            pitch = 3.7
            st.write("---")
            st.caption("Parametry vlnovce nejsou vyžadovány.")
            
        variants.append({"label": v_label, "type": v_type, "d_min": d_min, "d_max": d_max, "pitch": pitch})

# --- VÝPOČETNÍ LOGIKA ---
def calculate_dp(v_cfg, flow_list):
    flow_m3s = flow_list / (60 * 1000)
    d_m = v_cfg['d_min'] / 1000
    v_vel = flow_m3s / (np.pi * (d_m/2)**2)
    Re = (final_density * v_vel * d_m) / visc
    l_smooth = np.array([(64/r if r < 2300 else 0.3164/r**0.25) for r in Re])
    
    if v_cfg['type'] == "Vlnitá":
        rel_rough = (v_cfg['d_max'] - v_cfg['d_min']) / (2 * v_cfg['d_min'])
        corr = 1 + (rel_rough * 12) * (0.004 / (v_cfg['pitch']/1000))
        l_final = l_smooth * max(corr, 3.2)
    else:
        l_final = l_smooth
        
    dp_pa = l_final * ((length/1000) / d_m) * (final_density * v_vel**2 / 2)
    return dp_pa / 1000

# --- VÝSTUPY ---
if st.button("🚀 SPOČÍTAT A GENEROVAT GRAF", use_container_width=True):
    log_calculation()
    
    flow_axis = np.linspace(0.1, flow_max, 100)
    fig, ax = plt.subplots(figsize=(10, 5))
    results = []

    for i, v in enumerate(variants):
        dp_curve = calculate_dp(v, flow_axis)
        ax.plot(flow_axis, dp_curve, lw=2.5, label=v['label'])
        results.append({
            "Název": v['label'],
            "Typ": v['type'],
            "Konfigurace": f"Ø{v['d_min']:.2f}" if v['type'] == "Hladká" else f"Ø{v['d_min']:.2f}/Ø{v['d_max']:.2f} p{v['pitch']}",
            "Ztráta [kPa]": dp_curve[-1]
        })

    ax.set_title(f"Report: {fluid_name} @ {temp}°C")
    ax.set_xlabel("Průtok [l/min]")
    ax.set_ylabel("Tlaková ztráta [kPa]")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)

    # Tabulka
    df = pd.DataFrame(results)
    ref_val = df.iloc[0]["Ztráta [kPa]"]
    df["Ztráta [kPa]"] = df["Ztráta [kPa]"].map('{:.3f}'.format)
    df["Rozdíl k Var 1"] = df["Ztráta [kPa]"].astype(float).apply(lambda x: f"{((x/ref_val)-1)*100:+.2f} %" if ref_val > 0 else "0.00 %")
    st.table(df)
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

from google.colab import files
files.download("app.py")
