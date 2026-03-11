import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# --- SLOVNÍK PŘEKLADŮ ---
lang_dict = {
    "Čeština": {
        "title": "📊 Hydraulický srovnávač",
        "subtitle": "Nástroj pro porovnání tlakových ztrát: Hladká vs. Vlnitá trubka",
        "fluid_params": "💧 Parametry média",
        "fluid_name": "Název kapaliny",
        "temp": "Teplota měření [°C]",
        "density": "Hustota",
        "unit": "Jednotka",
        "viscosity": "Viskozita [Pa·s]",
        "geometry": "📏 Společná geometrie",
        "length": "Délka trasy [mm]",
        "flow_max": "Maximální sledovaný průtok [l/min]",
        "config": "Konfigurace variant",
        "variant": "Varianta",
        "label": "Název/Poznámka",
        "type": "Typ",
        "smooth": "Hladká",
        "corrugated": "Vlnitá",
        "in_diam": "Vnitřní Ø [mm]",
        "max_diam": "Maximální Ø [mm]",
        "pitch": "Rozteč [mm]",
        "not_req": "Parametry vlnovce nejsou vyžadovány.",
        "btn": "🚀 SPOČÍTAT A GENEROVAT GRAF",
        "report": "Report",
        "xlabel": "Průtok [l/min]",
        "ylabel": "Tlaková ztráta [kPa]",
        "col_name": "Název",
        "col_type": "Typ",
        "col_conf": "Konfigurace",
        "col_loss": "Ztráta [kPa]",
        "col_diff": "Rozdíl k Var 1"
    },
    "Deutsch": {
        "title": "📊 Hydraulik-Vergleichsrechner",
        "subtitle": "Werkzeug zum Vergleich von Druckverlusten: Glattrohr vs. Wellrohr",
        "fluid_params": "💧 Medienparameter",
        "fluid_name": "Flüssigkeitsname",
        "temp": "Messtemperatur [°C]",
        "density": "Dichte",
        "unit": "Einheit",
        "viscosity": "Viskosität [Pa·s]",
        "geometry": "📏 Gemeinsame Geometrie",
        "length": "Leitungslänge [mm]",
        "flow_max": "Maximaler Durchfluss [l/min]",
        "config": "Variantenkonfiguration",
        "variant": "Variante",
        "label": "Name/Notiz",
        "type": "Typ",
        "smooth": "Glatt",
        "corrugated": "Wellig",
        "in_diam": "Innen-Ø [mm]",
        "max_diam": "Maximal-Ø [mm]",
        "pitch": "Teilung [mm]",
        "not_req": "Wellrohrparameter nicht erforderlich.",
        "btn": "🚀 BERECHNEN UND GRAFIK ERZEUGEN",
        "report": "Bericht",
        "xlabel": "Durchfluss [l/min]",
        "ylabel": "Druckverlust [kPa]",
        "col_name": "Name",
        "col_type": "Typ",
        "col_conf": "Konfiguration",
        "col_loss": "Verlust [kPa]",
        "col_diff": "Unterschied zu Var 1"
    },
    "English": {
        "title": "📊 Hydraulic Comparator",
        "subtitle": "Pressure drop comparison tool: Smooth vs. Corrugated pipe",
        "fluid_params": "💧 Fluid Parameters",
        "fluid_name": "Fluid Name",
        "temp": "Measurement Temp [°C]",
        "density": "Density",
        "unit": "Unit",
        "viscosity": "Viscosity [Pa·s]",
        "geometry": "📏 Common Geometry",
        "length": "Route Length [mm]",
        "flow_max": "Max Flow Rate [l/min]",
        "config": "Variant Configuration",
        "variant": "Variant",
        "label": "Name/Note",
        "type": "Type",
        "smooth": "Smooth",
        "corrugated": "Corrugated",
        "in_diam": "Inner Ø [mm]",
        "max_diam": "Maximum Ø [mm]",
        "pitch": "Pitch [mm]",
        "not_req": "Corrugation parameters not required.",
        "btn": "🚀 CALCULATE AND GENERATE GRAPH",
        "report": "Report",
        "xlabel": "Flow rate [l/min]",
        "ylabel": "Pressure drop [kPa]",
        "col_name": "Name",
        "col_type": "Type",
        "col_conf": "Configuration",
        "col_loss": "Loss [kPa]",
        "col_diff": "Diff to Var 1"
    },
    "Română": {
        "title": "📊 Comparator Hidraulic",
        "subtitle": "Instrument comparare căderi de presiune: Teavă Netedă vs. Ondulată",
        "fluid_params": "💧 Parametri Fluid",
        "fluid_name": "Numele fluidului",
        "temp": "Temp. de măsurare [°C]",
        "density": "Densitate",
        "unit": "Unitate",
        "viscosity": "Vâscozitate [Pa·s]",
        "geometry": "📏 Geometrie Comună",
        "length": "Lungime traseu [mm]",
        "flow_max": "Debit maxim [l/min]",
        "config": "Configurare Variante",
        "variant": "Varianta",
        "label": "Nume/Notă",
        "type": "Tip",
        "smooth": "Netedă",
        "corrugated": "Ondulată",
        "in_diam": "Ø Interior [mm]",
        "max_diam": "Ø Maxim [mm]",
        "pitch": "Pas [mm]",
        "not_req": "Parametrii de ondulare nu sunt necesari.",
        "btn": "🚀 CALCULEAZĂ ȘI GENEREAZĂ GRAFICUL",
        "report": "Raport",
        "xlabel": "Debit [l/min]",
        "ylabel": "Cădere de presiune [kPa]",
        "col_name": "Nume",
        "col_type": "Tip",
        "col_conf": "Configurație",
        "col_loss": "Pierdere [kPa]",
        "col_diff": "Dif. față de Var 1"
    }
}

# Nastavení vzhledu stránky
st.set_page_config(page_title="Hydraulic Comparator 4.3", layout="wide")

# --- VÝBĚR JAZYKA ---
with st.sidebar:
    st.header("🌐 Language / Jazyk")
    sel_lang = st.selectbox("Select language / Vyberte jazyk", ["Čeština", "Deutsch", "English", "Română"])
    L = lang_dict[sel_lang] # Aktuální slovník překladů

st.title(L["title"])
st.markdown(L["subtitle"])

# --- SIDEBAR: SPOLEČNÉ PARAMETRY ---
with st.sidebar:
    st.divider()
    st.header(L["fluid_params"])
    fluid_name = st.text_input(L["fluid_name"], "G12+ Specifikace")
    temp = st.number_input(L["temp"], value=22.0, step=0.1)
    
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        dens_val = st.number_input(L["density"], value=1060.0, step=0.1)
    with col_d2:
        dens_unit = st.selectbox(L["unit"], ["kg/m³", "g/cm³"])
    
    visc = st.number_input(L["viscosity"], value=0.0030, format="%.4f", step=0.0001)
    
    st.header(L["geometry"])
    length = st.number_input(L["length"], value=500.0, step=0.01)
    flow_max = st.slider(L["flow_max"], 0.5, 100.0, 25.0, 0.5)

final_density = dens_val * 1000 if dens_unit == "g/cm³" else dens_val

# --- HLAVNÍ ČÁST: 4 VARIANTY ---
st.subheader(L["config"])
cols = st.columns(4)
variants = []

for i in range(4):
    with cols[i]:
        st.info(f"{L['variant']} {i+1}")
        v_label = st.text_input(f"{L['label']}", value=f"{L['variant']} {i+1}", key=f"lab{i}")
        
        v_type_sel = st.selectbox(L["type"], [L["smooth"], L["corrugated"]], index=(1 if i > 0 else 0), key=f"t{i}")
        # Mapování zpět na interní klíče
        v_type = "Vlnitá" if v_type_sel == L["corrugated"] else "Hladká"
        
        d_min = st.number_input(L["in_diam"], value=12.0, step=0.01, key=f"dmin{i}")
        
        if v_type == "Vlnitá":
            d_max = st.number_input(L["max_diam"], value=15.0, step=0.01, key=f"dmax{i}")
            pitch = st.selectbox(L["pitch"], [3.1, 3.3, 3.7, 4.0, 4.65], index=2, key=f"p{i}")
        else:
            d_max = d_min
            pitch = 3.7
            st.write("---")
            st.caption(L["not_req"])
            
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
if st.button(L["btn"], use_container_width=True):
    flow_axis = np.linspace(0.1, flow_max, 100)
    fig, ax = plt.subplots(figsize=(10, 5))
    results = []

    for i, v in enumerate(variants):
        dp_curve = calculate_dp(v, flow_axis)
        ax.plot(flow_axis, dp_curve, lw=2.5, label=v['label'])
        results.append({
            L["col_name"]: v['label'],
            L["col_type"]: L["corrugated"] if v['type'] == "Vlnitá" else L["smooth"],
            L["col_conf"]: f"Ø{v['d_min']:.2f}" if v['type'] == "Hladká" else f"Ø{v['d_min']:.2f}/Ø{v['d_max']:.2f} p{v['pitch']}",
            L["col_loss"]: dp_curve[-1]
        })

    ax.set_title(f"{L['report']}: {fluid_name} @ {temp}°C")
    ax.set_xlabel(L["xlabel"])
    ax.set_ylabel(L["ylabel"])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)

    # Tabulka
    df = pd.DataFrame(results)
    ref_val = df.iloc[0][L["col_loss"]]
    df[L["col_loss"]] = df[L["col_loss"]].map('{:.3f}'.format)
    df[L["col_diff"]] = df[L["col_loss"]].astype(float).apply(lambda x: f"{((x/ref_val)-1)*100:+.2f} %" if ref_val > 0 else "0.00 %")
    st.table(df)
