import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# --- 1. SLOVNÍK PŘEKLADŮ (Pressure Drop Solution Designer) ---
lang_dict = {
    "Čeština": {
        "title": "🔍 Pressure Drop Solution Designer",
        "subtitle": "Kalkulátor poklesu tlaku dle zvoleného technického řešení",
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
        "btn": "🚀 GENEROVAT ANALÝZU ŘEŠENÍ",
        "report": "Technický report",
        "xlabel": "Průtok [l/min]",
        "ylabel": "Tlaková ztráta [kPa]",
        "col_name": "Název",
        "col_type": "Typ",
        "col_conf": "Konfigurace",
        "col_loss": "Ztráta [kPa]",
        "col_diff": "Rozdíl k Var 1"
    },
    "Deutsch": {
        "title": "🔍 Pressure Drop Solution Designer",
        "subtitle": "Druckverlust-Rechner nach technischer Lösung",
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
        "btn": "🚀 LÖSUNGSANALYSE GENERIEREN",
        "report": "Technischer Bericht",
        "xlabel": "Durchfluss [l/min]",
        "ylabel": "Druckverlust [kPa]",
        "col_name": "Name",
        "col_type": "Typ",
        "col_conf": "Konfiguration",
        "col_loss": "Verlust [kPa]",
        "col_diff": "Unterschied zu Var 1"
    },
    "English": {
        "title": "🔍 Pressure Drop Solution Designer",
        "subtitle": "Pressure drop calculator by technical solution",
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
        "btn": "🚀 GENERATE SOLUTION ANALYSIS",
        "report": "Technical Report",
        "xlabel": "Flow rate [l/min]",
        "ylabel": "Pressure drop [kPa]",
        "col_name": "Name",
        "col_type": "Type",
        "col_conf": "Configuration",
        "col_loss": "Loss [kPa]",
        "col_diff": "Diff to Var 1"
    },
    "Română": {
        "title": "🔍 Pressure Drop Solution Designer",
        "subtitle": "Calculator cădere de presiune conform soluției tehnice",
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
        "btn": "🚀 GENEREAZĂ ANALIZA SOLUȚIEI",
        "report": "Raport tehnic",
        "xlabel": "Debit [l/min]",
        "ylabel": "Cădere de presiune [kPa]",
        "col_name": "Nume",
        "col_type": "Tip",
        "col_conf": "Configurație",
        "col_loss": "Pierdere [kPa]",
        "col_diff": "Dif. față de Var 1"
    }
}

# --- 2. NASTAVENÍ STRÁNKY A SIDEBARU ---
st.set_page_config(page_title="Pressure Drop Solution Designer", layout="wide")

with st.sidebar:
    # Zobrazení LOGA (soubor logo.png musí být na GitHubu)
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.caption("ℹ️ Nahrajte 'logo.png' pro zobrazení loga firmy.")
    
    st.header("🌐 Language / Jazyk")
    sel_lang = st.selectbox("Select language / Vyberte jazyk", list(lang_dict.keys()))
    L = lang_dict[sel_lang]
    
    st.divider()
    st.header(L["fluid_params"])
    fluid_name = st.text_input(L["fluid_name"], "G12+ Specifikace")
    temp_val = st.number_input(L["temp"], value=22.0, step=0.1)
    
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        dens_input = st.number_input(L["density"], value=1060.0, step=0.1)
    with col_d2:
        dens_unit_val = st.selectbox(L["unit"], ["kg/m³", "g/cm³"])
    
    visc_val = st.number_input(L["viscosity"], value=0.0030, format="%.4f", step=0.0001)
    
    st.header(L["geometry"])
    length_val = st.number_input(L["length"], value=500.0, step=0.01)
    flow_max_val = st.slider(L["flow_max"], 0.5, 100.0, 25.0, 0.5)

# Přepočet hustoty
final_density = dens_input * 1000 if dens_unit_val == "g/cm³" else dens_input

# --- 3. HLAVNÍ OBSAH (ZÁHLAVÍ) ---
st.title(L["title"])
st.markdown(f"#### {L['subtitle']}")
st.divider()

# --- 4. KONFIGURACE VARIANT ---
st.subheader(L["config"])
cols = st.columns(4)
variants_list = []

for i in range(4):
    with cols[i]:
        st.info(f"{L['variant']} {i+1}")
        v_label_val = st.text_input(L["label"], value=f"{L['variant']} {i+1}", key=f"lab{i}")
        
        v_type_sel = st.selectbox(L["type"], [L["smooth"], L["corrugated"]], index=(1 if i > 0 else 0), key=f"t{i}")
        v_type_internal = "Vlnitá" if v_type_sel == L["corrugated"] else "Hladká"
        
        d_min_val = st.number_input(L["in_diam"], value=12.0, step=0.01, key=f"dmin{i}")
        
        if v_type_internal == "Vlnitá":
            d_max_val = st.number_input(L["max_diam"], value=15.0, step=0.01, key=f"dmax{i}")
            pitch_val = st.selectbox(L["pitch"], [3.1, 3.3, 3.7, 4.0, 4.65], index=2, key=f"p{i}")
        else:
            d_max_val = d_min_val
            pitch_val = 3.7
            st.write("---")
            st.caption(L["not_req"])
            
        variants_list.append({
            "label": v_label_val, 
            "type": v_type_internal, 
            "d_min": d_min_val, 
            "d_max": d_max_val, 
            "pitch": pitch_val
        })

# --- 5. FYZIKÁLNÍ JÁDRO ---
def calculate_dp(v_cfg, flows):
    flow_m3s = flows / (60 * 1000)
    d_m = v_cfg['d_min'] / 1000
    v_vel = flow_m3s / (np.pi * (d_m/2)**2)
    # Re výpočet (ošetření dělení nulou u viskozity)
    safe_visc = visc_val if visc_val > 0 else 0.000001
    Re = (final_density * v_vel * d_m) / safe_visc
    
    # Lambda - Laminární / Turbulentní
    l_smooth = np.array([(64/r if r < 2300 else 0.3164/r**0.25) for r in Re])
    
    if v_cfg['type'] == "Vlnitá":
        rel_rough = (v_cfg['d_max'] - v_cfg['d_min']) / (2 * v_cfg['d_min'])
        # Korekční faktor pro vlnovce
        corr = 1 + (rel_rough * 12) * (0.004 / (v_cfg['pitch']/1000))
        l_final = l_smooth * max(corr, 3.2)
    else:
        l_final = l_smooth
        
    dp_pa = l_final * ((length_val/1000) / d_m) * (final_density * v_vel**2 / 2)
    return dp_pa / 1000 # Výstup v kPa

# --- 6. VÝSTUPY (GRAF A TABULKA) ---
st.divider()
if st.button(L["btn"], use_container_width=True):
    flow_axis = np.linspace(0.1, flow_max_val, 100)
    fig, ax = plt.subplots(figsize=(12, 6))
    results_data = []

    for i, v in enumerate(variants_list):
        dp_curve = calculate_dp(v, flow_axis)
        ax.plot(flow_axis, dp_curve, lw=3, label=v['label'])
        
        results_data.append({
            L["col_name"]: v['label'],
            L["col_type"]: L["corrugated"] if v['type'] == "Vlnitá" else L["smooth"],
            L["col_conf"]: f"Ø{v['d_min']:.2f}" if v['type'] == "Hladká" else f"Ø{v['d_min']:.2f}/Ø{v['d_max']:.2f} p{v['pitch']}",
            "raw_loss": dp_curve[-1]
        })

    ax.set_title(f"{L['report']}: {fluid_name} @ {temp_val}°C", fontsize=14, fontweight='bold')
    ax.set_xlabel(L["xlabel"])
    ax.set_ylabel(L["ylabel"])
    ax.legend()
    ax.grid(True, alpha=0.3, linestyle='--')
    
    st.pyplot(fig)

    # Příprava tabulky
    df = pd.DataFrame(results_data)
    ref_val = df.iloc[0]["raw_loss"]
    
    df[L["col_loss"]] = df["raw_loss"].map('{:.3f}'.format)
    df[L["col_diff"]] = df["raw_loss"].apply(lambda x: f"{((x/ref_val)-1)*100:+.2f} %" if ref_val > 0 else "0.00 %")
    
    # Zobrazení bez pomocného sloupce
    st.table(df[[L["col_name"], L["col_type"], L["col_conf"], L["col_loss"], L["col_diff"]]])
