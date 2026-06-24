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
# 2. CONFIGURACIÓN E IDENTIDAD
# ==========================================
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

if 'correo_asesor' not in st.session_state:
    st.session_state.correo_asesor = "ASESOR.B2B@SOMOSTELSER.COM"

with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_container_width=True)
    st.markdown(f"👤 **Asesor:** `{st.session_state.correo_asesor}`")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.correo_asesor = None
        st.rerun()

    # ASISTENTE DE PRECIOS INTELIGENTE
    st.markdown("---")
    st.subheader("🤖 Asistente de Precios")
    consulta = st.text_input("¿Qué oferta buscas?")
    if consulta:
        portafolio_total = {**PLANES_MOVIL, **PLANES_FIJO}
        resultados = {k: v for k, v in portafolio_total.items() if consulta.lower() in k.lower()}
        if resultados:
            for plan, precio in resultados.items():
                st.write(f"✅ *{plan}*: **${precio:,.0f}**")
        else:
            st.warning("No encontrado.")

    # DASHBOARD
    st.markdown("---")
    st.subheader("📊 Dashboard")
    if os.path.exists("crm_sistema_maestro.csv"):
        try:
            df_ventas = pd.read_csv("crm_sistema_maestro.csv")
            if 'DIVISION' in df_ventas.columns and not df_ventas.empty:
                st.bar_chart(df_ventas['DIVISION'].value_counts())
        except:
            st.info("Cargando datos...")
    else:
        st.info("Realiza una venta.")

# TÍTULOS
st.title("📡 Portal de Ventas Somos Telser")
st.subheader("Gestión Inteligente de Contratos B2B")
div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True)

# ==========================================
# 3. INTERFAZ Y AGENTE FINANCIERO
# ==========================================
with st.form("registro_full", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏢 Datos del Cliente")
        t_doc = st.selectbox("Tipo Doc:", ["NIT", "Cédula", "CE", "PPT"])
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
        dir = st.text_input("Dirección de instalación:")
        barrio = st.text_input("Barrio:")
        muni = st.text_input("Municipio / Departamento:")
        email_cli = st.text_input("Correo Electrónico del Cliente:")
        movil_cli = st.text_input("Móvil de Contacto:")
    with c2:
        st.subheader("👤 Representante Legal")
        nom_rep = st.text_input("Nombre del Rep. Legal:")
        cc_rep = st.text_input("Cédula Rep. Legal:")
        mail_rep = st.text_input("Correo Rep. Legal:")
