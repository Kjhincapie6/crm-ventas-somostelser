import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. PORTAFOLIO Y DATOS
# ==========================================
PLANES_MOVIL = {
    "Pospago Negocios 4.9 Plus+ (60 GB)": 44900.0,
    "Pospago Negocios 5.4 Plus+ (100 GB)": 53900.0,
    "Pospago 5.3 Empresarial (Ilim GB)": 113900.0,
    "Plan Datos Tigo Empresarial 6.9 (30 GB)": 38300.0,
    "Plan Datos Tigo Empresarial 6.10 (60 GB)": 47900.0,
    "Plan Datos Tigo Empresarial 6.11 (110 GB)": 57900.0,
    "Plan Datos Tigo Empresarial 6.12 (Ilim GB)": 113900.0,
    "Plan Datos Tigo Empresarial 6.8 FULL TIGO (Ilim GB)": 54900.0
}

PLANES_FIJO = {
    "Internet Business 300 Mbps (HFC/FTTx)": 88880.0,
    "Internet Business 500 Mbps (HFC/FTTx)": 115000.0,
    "Internet Business 700 Mbps (HFC/FTTx)": 180001.0,
    "Internet Full Tigo Business 500 Mbps": 144000.0,
    "Internet Full Tigo Business 700 Mbps": 174000.0,
    "Internet Full Tigo Business 1000 Mbps": 274000.0
}

# ==========================================
# 2. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

# (Sidebar simplificado)
with st.sidebar:
    st.subheader("📊 Dashboard")
    if os.path.exists("crm_sistema_maestro.csv"):
        try:
            df = pd.read_csv("crm_sistema_maestro.csv")
            if not df.empty:
                st.bar_chart(df['DIVISION'].value_counts())
        except: st.caption("Cargando...")

# ==========================================
# 3. INTERFAZ Y AGENTE FINANCIERO
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
div = st.radio("Seleccione División:", ["Móvil", "Fijo"], horizontal=True)
tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO

with st.form("registro_full", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
    with c2:
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Líneas:", min_value=1, value=1)
        
        # AQUÍ ESTÁ EL CAMBIO: El cálculo ocurre en tiempo real al cambiar los widgets
        dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
        valor_calculado = (tarifas[servicio] * lineas) * (1 - dcto/100)
        
        st.info(f"💰 **Total: ${valor_calculado:,.0f} COP** (Dcto: {dcto}%)")
        guardar = st.form_submit_button("💾 Guardar Venta")

if guardar:
    if n_doc and nombre:
        archivo = "crm_sistema_maestro.csv"
        df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()
        nueva_fila = pd.DataFrame([{
            'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre,
            'SERVICIO': servicio, 'VALOR_TOTAL': valor_calculado
        }])
        pd.concat([df_ex, nueva_fila]).to_csv(archivo, index=False)
        st.success("✅ Venta registrada.")
        st.rerun()
    else:
        st.error("⚠️ Faltan datos.")
