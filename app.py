app_code = '''import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- GOOGLE SHEETS KONFIGURACE PRO TRVALÉ UKLÁDÁNÍ ---
# Vložte sem URL vaší veřejně editovatelné Google tabulky
SHEET_URL = "https://docs.google.com/spreadsheets/d/VASE_ID_TABULKY/edit"

def log_calculation():
    """Zapíše nový řádek do Google Tabulky."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_existing = conn.read(spreadsheet=SHEET_URL, ttl=0)
        
        now = datetime.now()
        new_row = pd.DataFrame([{
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "month_year": now.strftime("%Y-%m")
        }])
        
        if df_existing is None or df_existing.empty:
            updated_df = new_row
        else:
            updated_df = pd.concat([df_existing, new_row], ignore_index=True)
            
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
    except Exception as e:
        st.sidebar.warning(f"Chyba zápisu do Google Sheets: {e}")

def get_stats():
    """Načte data z Google Tabulky a spočítá statistiky."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=SHEET_URL, ttl=2)
        
        if df is None or df.empty or "month_year" not in df.columns:
            return 0, 0, pd.DataFrame(columns=["Měsíc", "Počet analýz"])
        
        # Očištění od prázdných řádků
        df = df.dropna(subset=["month_year"])
        total_count = len(df)
        
        current_month_str = datetime.now().strftime("%Y-%m")
        curr_month_count = len(df[df["month_year"] == current_month_str])
        
        monthly_df = df["month_year"].value_counts().reset_index()
        monthly_df.columns = ["Měsíc", "Počet analýz"]
        monthly_df = monthly_df.sort_values(by="Měsíc", ascending=False)
        
        return total_count, curr_month_count, monthly_df
    except Exception:
        return 0, 0, pd.DataFrame(columns=["Měsíc", "Počet analýz"])

# --- VZHLED STRÁNKY ---
st.set_page_config(page_title="Hydraulický Srovnávač 4.2", layout="wide")

# Vlastní CSS: Šířka sidebaru, skrytí fullscreenu a styl tlačítek jazyků
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 405px;
            max-width: 405px;
        }
        button[title="View fullscreen"],
        [data-testid="StyledFullScreenButton"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }
        div[data-testid="stHorizontalBlock"] button {
            padding: 2px 6px !important;
            font-size: 13px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if "current_lang" not in st.session_state:
    st.session_state["current_lang"] = "cs"

# --- JAZYKOVÉ SLOVNÍKY ---
TRANSLATIONS = {
    "cs": {
        "title": "📊 Kalkulátor tlakových ztrát: Hladká vs. Vlnitá trubka",
        "subtitle": "Nástroj pro porovnání tlakových ztrát s možností vlastního pojmenování variant. Cílem kalkulátoru je najít řešení a vidět dopad aplikace vlnitých profilů a jejich vliv na zvýšení odporu.",
        "btn_manual": "❓ Nápověda / Manuál",
        "param_media": "💧 Parametry média",
        "fluid_name": "Název kapaliny",
        "temp": "Teplota měření [°C]",
        "density": "Hustota",
        "density_unit": "Jednotka",
        "viscosity": "Viskozita [Pa·s]",
        "geom_header": "📏 Společná geometrie",
        "length": "Délka trasy [mm]",
        "flow_max": "Maximální sledovaný průtok [l/min]",
        "usage_header": "📈 Využití kalkulátoru",
        "this_month": "Tento měsíc",
        "total_calc": "Celkem",
        "monthly_overview": "📅 Přehled po měsících",
        "no_calc": "Zatím nebyly provedeny žádné výpočty.",
        "col_month": "Měsíc",
        "col_count": "Počet analýz",
        "var_header": "Konfigurace variant",
        "var_title": "Varianta",
        "var_name": "Název/Poznámka",
        "var_name_help": "Pojmenujte variantu pro legendu grafu (např. NW12 Sinus)",
        "var_type": "Typ",
        "type_smooth": "Hladká",
        "type_corrugated": "Vlnitá",
        "d_min": "Vnitřní Ø [mm]",
        "d_max": "Maximální Ø [mm]",
        "pitch": "Rozteč [mm]",
        "smooth_note": "Parametry vlnovce nejsou vyžadovány.",
        "calc_btn": "🚀 SPOČÍTAT A GENEROVAT GRAF",
        "graph_flow": "Průtok [l/min]",
        "graph_dp": "Tlaková ztráta [kPa]",
        "res_name": "Název",
        "res_type": "Typ",
        "res_cfg": "Konfigurace",
        "res_loss": "Ztráta [kPa]",
        "res_diff": "Rozdíl k Var 1",
        "manual_body": """
### 1. 🎯 Úvod a k čemu aplikace slouží
Hydraulický Srovnávač je interaktivní webový nástroj určený pro rychlý výpočet a porovnání tlakových ztrát ($\\Delta p$) při proudění kapalin v potrubí. Umožňuje přímo porovnat chování hladkých trubek a trubek s vlnovcovým profilem.

---

### 2. ⚡ Rychlý postup práce
* **[1. Levý panel]** Zadejte vlastnosti kapaliny (hustota, viskozita, teplota) a společnou délku trasy.
* **[2. Hlavní plocha]** Nakonfigurujte až 4 porovnávané varianty (typ profilu, průměry, rozteč vln).
* **[3. Tlačítko]** Klikněte na velké tlačítko **🚀 SPOČÍTAT A GENEROVAT GRAF**.
* **[4. Vyhodnocení]** Zkontrolujte průběh křivek v grafu a procentuální srovnání v tabulce.

---

### 3. ⚙️ Detailní popis parametrů a vstupů
* **Název kapaliny:** Identifikační název kapaliny v záhlaví grafu.
* **Viskozita [Pa·s]:** Dynamická viskozita kapaliny (voda $\\approx 0.0010$, chladicí směsi vyšší).
* **Vnitřní Ø ($d_{min}$):** Světlost / vnitřní průměr (u vlnovce vnitřní pata profilu).
* **Maximální Ø ($d_{max}$):** Vnější průměr vlny (vrchol profilu vlnovce).
* **Rozteč ($p$):** Osová vzdálenost mezi jednotlivými vlnami profilu.

---

### 4. 📊 Interpretace výstupů
* **Graf tlakové ztráty:** Znázorňuje závislost tlakového odporu [kPa] na průtoku [l/min].
* **Porovnávací tabulka:** Nabízí přesné hodnoty při maximálním průtoku a procentuální rozdíl vztažený k Variantě 1.
        """
    },
    "en": {
        "title": "📊 Pressure Drop Calculator: Smooth vs. Corrugated Tube",
        "subtitle": "Tool for comparing pressure drops with custom variant naming. The goal is to evaluate the impact of corrugated profiles and increased resistance.",
        "btn_manual": "❓ Help / Manual",
        "param_media": "💧 Fluid Parameters",
        "fluid_name": "Fluid Name",
        "temp": "Measuring Temp [°C]",
        "density": "Density",
        "density_unit": "Unit",
        "viscosity": "Viscosity [Pa·s]",
        "geom_header": "📏 Common Geometry",
        "length": "Tube Length [mm]",
        "flow_max": "Max Monitored Flow [l/min]",
        "usage_header": "📈 Calculator Usage",
        "this_month": "This Month",
        "total_calc": "Total",
        "monthly_overview": "📅 Monthly Overview",
        "no_calc": "No calculations performed yet.",
        "col_month": "Month",
        "col_count": "Analyses Count",
        "var_header": "Variant Configuration",
        "var_title": "Variant",
        "var_name": "Name/Note",
        "var_name_help": "Name the variant for the chart legend (e.g., NW12 Sinus)",
        "var_type": "Type",
        "type_smooth": "Smooth",
        "type_corrugated": "Corrugated",
        "d_min": "Inner Ø [mm]",
        "d_max": "Max Ø [mm]",
        "pitch": "Pitch [mm]",
        "smooth_note": "Corrugation parameters not required.",
        "calc_btn": "🚀 CALCULATE AND GENERATE CHART",
        "graph_flow": "Flow Rate [l/min]",
        "graph_dp": "Pressure Drop [kPa]",
        "res_name": "Name",
        "res_type": "Type",
        "res_cfg": "Configuration",
        "res_loss": "Loss [kPa]",
        "res_diff": "Diff to Var 1",
        "manual_body": """
### 1. 🎯 Purpose and Overview
The Hydraulic Comparator is an interactive web tool for quick calculation and comparison of pressure drops ($\\Delta p$) in fluid piping.

---

### 2. ⚡ Quick Workflow
* **[1. Sidebar]** Enter fluid properties and total length.
* **[2. Main Screen]** Configure up to 4 variants.
* **[3. Button]** Click **🚀 CALCULATE AND GENERATE CHART**.
* **[4. Evaluation]** Review curves and summary table.
        """
    },
    "de": {
        "title": "📊 Druckverlust-Rechner: Glattrohr vs. Wellrohr",
        "subtitle": "Werkzeug zum Vergleichen von Druckverlusten mit individueller Variantenbenennung.",
        "btn_manual": "❓ Hilfe / Handbuch",
        "param_media": "💧 Medienparameter",
        "fluid_name": "Name des Mediums",
        "temp": "Messtemperatur [°C]",
        "density": "Dichte",
        "density_unit": "Einheit",
        "viscosity": "Viskosität [Pa·s]",
        "geom_header": "📏 Gemeinsame Geometrie",
        "length": "Leitungslänge [mm]",
        "flow_max": "Max. Durchfluss [l/min]",
        "usage_header": "📈 Rechner-Nutzung",
        "this_month": "Diesen Monat",
        "total_calc": "Gesamt",
        "monthly_overview": "📅 Monatsübersicht",
        "no_calc": "Bisher keine Berechnungen durchgeführt.",
        "col_month": "Monat",
        "col_count": "Anzahl Analysen",
        "var_header": "Variantenkonfiguration",
        "var_title": "Variante",
        "var_name": "Name/Notiz",
        "var_name_help": "Benennen Sie die Variante für die Diagrammlegende",
        "var_type": "Typ",
        "type_smooth": "Glatt",
        "type_corrugated": "Gewellt",
        "d_min": "Innen-Ø [mm]",
        "d_max": "Maximaler Ø [mm]",
        "pitch": "Teilung [mm]",
        "smooth_note": "Wellrohrparameter nicht erforderlich.",
        "calc_btn": "🚀 BERECHNEN UND DIAGRAMM ERSTELLEN",
        "graph_flow": "Durchfluss [l/min]",
        "graph_dp": "Druckverlust [kPa]",
        "res_name": "Name",
        "res_type": "Typ",
        "res_cfg": "Konfiguration",
        "res_loss": "Verlust [kPa]",
        "res_diff": "Diff. zu Var 1",
        "manual_body": """
### 1. 🎯 Einführung
Interaktives Werkzeug zur schnellen Berechnung und zum Vergleich von Druckverlusten ($\\Delta p$) in Rohrleitungen.

---

### 2. ⚡ Kurzanleitung
* **[1. Seitenleiste]** Mediendaten und Rohrlänge eingeben.
* **[2. Hauptbereich]** Bis zu 4 Varianten konfigurieren.
* **[3. Ausführen]** Auf **🚀 BERECHNEN** klicken.
* **[4. Ergebnis]** Diagramm und Vergleichstabelle auswerten.
        """
    },
    "ro": {
        "title": "📊 Calculator Cădere de Presiune: Tub Neted vs. Ondulat",
        "subtitle": "Instrument pentru compararea căderilor de presiune cu denumirea personalizată a variantelor.",
        "btn_manual": "❓ Ajutor / Manual",
        "param_media": "💧 Parametri Fluid",
        "fluid_name": "Nume Fluid",
        "temp": "Temp. Măsurare [°C]",
        "density": "Densitate",
        "density_unit": "Unitate",
        "viscosity": "Vâscozitate [Pa·s]",
        "geom_header": "📏 Geometrie Comună",
        "length": "Lungime Traseu [mm]",
        "flow_max": "Debit Maxim Urmărit [l/min]",
        "usage_header": "📈 Utilizare Calculator",
        "this_month": "Luna Aceasta",
        "total_calc": "Total",
        "monthly_overview": "📅 Prezentare Lunară",
        "no_calc": "Nu au fost efectuate calcule încă.",
        "col_month": "Lună",
        "col_count": "Număr Analize",
        "var_header": "Configurare Variante",
        "var_title": "Varianta",
        "var_name": "Nume/Notă",
        "var_name_help": "Denumiți varianta pentru legenda graficului",
        "var_type": "Tip",
        "type_smooth": "Neted",
        "type_corrugated": "Ondulat",
        "d_min": "Ø Interior [mm]",
        "d_max": "Ø Maxim [mm]",
        "pitch": "Pas Ondulație [mm]",
        "smooth_note": "Parametrii de ondulare nu sunt necesari.",
        "calc_btn": "🚀 CALCULEAZĂ ȘI GENEREAZĂ GRAFIC",
        "graph_flow": "Debit [l/min]",
        "graph_dp": "Cădere de Presiune [kPa]",
        "res_name": "Nume",
        "res_type": "Tip",
        "res_cfg": "Configurație",
        "res_loss": "Pierdere [kPa]",
        "res_diff": "Dif. față de Var 1",
        "manual_body": """
### 1. 🎯 Scop și Utilizare
Instrument interactiv pentru calculul rapid și compararea căderilor de presiune ($\\Delta p$) în conducte.

---

### 2. ⚡ Pași de Lucru
* **[1. Panou Stânga]** Introduceți proprietățile fluidului și lungimea conductei.
* **[2. Ecran Principal]** Configurați până la 4 variante.
* **[3. Buton]** Apăsați pe **🚀 CALCULEAZĂ**.
* **[4. Evaluare]** Vizualizați graficul și tabelul rezumat.
        """
    },
    "es": {
        "title": "📊 Calculadora de Caída de Presión: Tubo Liso vs. Corrugado",
        "subtitle": "Herramienta para comparar pérdidas de presión con personalización de nombres de variantes.",
        "btn_manual": "❓ Ayuda / Manual",
        "param_media": "💧 Parámetros del Fluido",
        "fluid_name": "Nombre del Fluido",
        "temp": "Temp. de Medición [°C]",
        "density": "Densidad",
        "density_unit": "Unidad",
        "viscosity": "Viscosidad [Pa·s]",
        "geom_header": "📏 Geometría Común",
        "length": "Longitud de Tubería [mm]",
        "flow_max": "Flujo Máximo [l/min]",
        "usage_header": "📈 Uso de la Calculadora",
        "this_month": "Este Mes",
        "total_calc": "Total",
        "monthly_overview": "📅 Resumen Mensual",
        "no_calc": "Aún no se han realizado cálculos.",
        "col_month": "Mes",
        "col_count": "Cantidad de Análisis",
        "var_header": "Configuración de Variantes",
        "var_title": "Variante",
        "var_name": "Nombre/Nota",
        "var_name_help": "Nombre de la variante para la leyenda del gráfico",
        "var_type": "Tipo",
        "type_smooth": "Liso",
        "type_corrugated": "Corrugado",
        "d_min": "Ø Interior [mm]",
        "d_max": "Ø Máximo [mm]",
        "pitch": "Paso [mm]",
        "smooth_note": "No se requieren parámetros de corrugación.",
        "calc_btn": "🚀 CALCULAR Y GENERAR GRÁFICA",
        "graph_flow": "Flujo [l/min]",
        "graph_dp": "Caída de Presión [kPa]",
        "res_name": "Nombre",
        "res_type": "Tipo",
        "res_cfg": "Configuración",
        "res_loss": "Pérdida [kPa]",
        "res_diff": "Dif. vs Var 1",
        "manual_body": """
### 1. 🎯 Introducción
Herramienta interactiva para calcular y comparar pérdidas de presión ($\\Delta p$) en tuberías.

---

### 2. ⚡ Flujo de Trabajo
* **[1. Panel Lateral]** Ingrese las propiedades del fluido y la longitud total.
* **[2. Pantalla Principal]** Configure hasta 4 variantes independientes.
* **[3. Botón]** Haga clic en **🚀 CALCULAR**.
* **[4. Resultados]** Revise las curvas en la gráfica y la tabla resumen.
        """
    }
}

# --- DIALOGOVÉ OKNO PRO NÁPOVĚDU ---
@st.dialog("Manual", width="large")
def show_manual(lang_code):
    st.markdown(TRANSLATIONS[lang_code]["manual_body"])

# --- HLAVIČKA: TITULEK VLEVO, VOLBA JAZYKŮ A NÁPOVĚDA VPRAVO ---
top_left, top_right = st.columns([4.2, 1.8])

with top_right:
    f_cols = st.columns(5)
    flags = [
        ("🇨🇿", "CZ", "cs"),
        ("🇬🇧", "EN", "en"),
        ("🇩🇪", "DE", "de"),
        ("🇷🇴", "RO", "ro"),
        ("🇲🇽", "ES", "es")
    ]
    
    for idx, (emoji, code_label, lang_id) in enumerate(flags):
        with f_cols[idx]:
            btn_type = "primary" if st.session_state["current_lang"] == lang_id else "secondary"
            if st.button(f"{emoji} {code_label}", key=f"btn_lang_{lang_id}", type=btn_type, use_container_width=True):
                st.session_state["current_lang"] = lang_id
                st.rerun()

    lang = st.session_state["current_lang"]
    t = TRANSLATIONS[lang]

    if st.button(t["btn_manual"], use_container_width=True):
        show_manual(lang)

with top_left:
    st.title(t["title"])

st.markdown(t["subtitle"])

# --- SIDEBAR (LEVÝ SLOUPEC) ---
with st.sidebar:
    # 1. Logo FIP (zmenšené bez fullscreenu)
    LOGO_FILE = "fip-logo-f-member-of-line-01-04.png"
    if os.path.exists(LOGO_FILE):
        logo_c1, logo_c2, logo_c3 = st.columns([1, 6, 1])
        with logo_c2:
            st.image(LOGO_FILE, width=220)
    else:
        st.markdown("### 🏢 **FIP**")
    
    st.divider()

    # 2. Parametry média
    st.header(t["param_media"])
    fluid_name = st.text_input(t["fluid_name"], "G12+ Specifikace")
    temp = st.number_input(t["temp"], value=22.0, step=0.1)
    
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        dens_val = st.number_input(t["density"], value=1060.0, step=0.1)
    with col_d2:
        dens_unit = st.selectbox(t["density_unit"], ["kg/m³", "g/cm³"])
    
    visc = st.number_input(t["viscosity"], value=0.0030, format="%.4f", step=0.0001)
    
    # 3. Společná geometrie
    st.header(t["geom_header"])
    length = st.number_input(t["length"], value=500.0, step=0.01)
    flow_max = st.slider(t["flow_max"], 0.5, 100.0, 25.0, 0.5)

    st.divider()

    # 4. Počítadlo využití kalkulátoru
    st.header(t["usage_header"])
    total_c, curr_m_c, monthly_data = get_stats()
    
    stat_c1, stat_c2 = st.columns(2)
    with stat_c1:
        st.metric(label=t["this_month"], value=curr_m_c)
    with stat_c2:
        st.metric(label=t["total_calc"], value=total_c)
        
    with st.expander(t["monthly_overview"]):
        if not monthly_data.empty:
            monthly_data.columns = [t["col_month"], t["col_count"]]
            st.dataframe(monthly_data, use_container_width=True, hide_index=True)
        else:
            st.caption(t["no_calc"])

final_density = dens_val * 1000 if dens_unit == "g/cm³" else dens_val

# --- HLAVNÍ ČÁST: 4 VARIANTY ---
st.subheader(t["var_header"])
cols = st.columns(4)
variants = []

for i in range(4):
    with cols[i]:
        st.info(f"{t['var_title']} {i+1}")
        v_label = st.text_input(t["var_name"], value=f"{t['var_title']} {i+1}", key=f"lab{i}", help=t["var_name_help"])
        
        type_options = [t["type_smooth"], t["type_corrugated"]]
        v_type_sel = st.selectbox(t["var_type"], type_options, index=(1 if i > 0 else 0), key=f"t{i}")
        is_corrugated = (v_type_sel == t["type_corrugated"])
        
        d_min = st.number_input(t["d_min"], value=12.0, step=0.01, key=f"dmin{i}")
        
        if is_corrugated:
            d_max = st.number_input(t["d_max"], value=15.0, step=0.01, key=f"dmax{i}")
            pitch = st.selectbox(t["pitch"], [3.1, 3.3, 3.7, 4.0, 4.65], index=2, key=f"p{i}")
        else:
            d_max = d_min
            pitch = 3.7
            st.write("---")
            st.caption(t["smooth_note"])
            
        variants.append({"label": v_label, "is_corrugated": is_corrugated, "type_label": v_type_sel, "d_min": d_min, "d_max": d_max, "pitch": pitch})

# --- VÝPOČETNÍ LOGIKA ---
def calculate_dp(v_cfg, flow_list):
    flow_m3s = flow_list / (60 * 1000)
    d_m = v_cfg['d_min'] / 1000
    v_vel = flow_m3s / (np.pi * (d_m/2)**2)
    Re = (final_density * v_vel * d_m) / visc
    l_smooth = np.array([(64/r if r < 2300 else 0.3164/r**0.25) for r in Re])
    
    if v_cfg['is_corrugated']:
        rel_rough = (v_cfg['d_max'] - v_cfg['d_min']) / (2 * v_cfg['d_min'])
        corr = 1 + (rel_rough * 12) * (0.004 / (v_cfg['pitch']/1000))
        l_final = l_smooth * max(corr, 3.2)
    else:
        l_final = l_smooth
        
    dp_pa = l_final * ((length/1000) / d_m) * (final_density * v_vel**2 / 2)
    return dp_pa / 1000

# --- VÝSTUPY ---
if st.button(t["calc_btn"], use_container_width=True):
    log_calculation()
    
    flow_axis = np.linspace(0.1, flow_max, 100)
    fig, ax = plt.subplots(figsize=(10, 5))
    results = []

    for i, v in enumerate(variants):
        dp_curve = calculate_dp(v, flow_axis)
        ax.plot(flow_axis, dp_curve, lw=2.5, label=v['label'])
        results.append({
            t["res_name"]: v['label'],
            t["res_type"]: v['type_label'],
            t["res_cfg"]: f"Ø{v['d_min']:.2f}" if not v['is_corrugated'] else f"Ø{v['d_min']:.2f}/Ø{v['d_max']:.2f} p{v['pitch']}",
            t["res_loss"]: dp_curve[-1]
        })

    ax.set_title(f"Report: {fluid_name} @ {temp}°C")
    ax.set_xlabel(t["graph_flow"])
    ax.set_ylabel(t["graph_dp"])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)

    # Tabulka
    df = pd.DataFrame(results)
    loss_col = t["res_loss"]
    ref_val = df.iloc[0][loss_col]
    df[loss_col] = df[loss_col].map('{:.3f}'.format)
    df[t["res_diff"]] = df[loss_col].astype(float).apply(lambda x: f"{((x/ref_val)-1)*100:+.2f} %" if ref_val > 0 else "0.00 %")
    st.table(df)
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

# Aktualizace requirements.txt s knihovnou pro Google Sheets
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("streamlit\nnumpy\nmatplotlib\npandas\nst-gsheets-connection\n")

from google.colab import files
files.download("app.py")
files.download("requirements.txt")
