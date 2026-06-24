import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. PORTAFOLIO Y DATOS (JUNIO 2026)
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
st.set_page_config(page_title="CRM Somos Telser - Junio 2026", layout="wide")

if 'correo_asesor' not in st.session_state:
    st.session_state.correo_asesor = "ASESOR.B2B@SOMOSTELSER.COM"

# Barra lateral con control de sesión
with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_container_width=True)
    st.markdown(f"👤 **Asesor:** `{st.session_state.correo_asesor}`")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 3. INTERFAZ OPTIMIZADA
# ==========================================
st.title("🏢 Gestión Integral de Contratos B2B")

div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True)

with st.form("registro_full", clear_on_submit=True): # clear_on_submit limpia el formulario tras guardar
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏢 Datos del Cliente")
        n_doc = st.text_input("Número de Documento:", key="n_doc")
        nombre = st.text_input("Razón Social o Nombre:")
        dir = st.text_input("Dirección de instalación:")
        muni = st.text_input("Municipio / Departamento:")
    with c2:
        st.subheader("👤 Representante Legal")
        nom_rep = st.text_input("Nombre del Rep. Legal:")
        estado = st.selectbox("Estado del Proceso:", [
            "En proceso de firma", "Enviado", "Ingreso de pedido", 
            "Instalacion y aprovisionamiento", "Instalado", "Activado"
        ])
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Cantidad / Líneas:", min_value=1, value=1)

    valor = (tarifas[servicio] * lineas) * (1 - (30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0))))/100)
    st.info(f"💰 **Total estimado:** ${valor:,.0f} COP")
    
    submitted = st.form_submit_button("💾 Guardar Venta")

if submitted:
    if n_doc and nombre:
        nueva_fila = pd.DataFrame([{
            'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre, 'SERVICIO': servicio, 
            'VALOR_TOTAL': valor, 'ASESOR': st.session_state.correo_asesor
        }])
        archivo = "crm_sistema_maestro.csv"
        pd.concat([pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame(), nueva_fila]).to_csv(archivo, index=False)
        st.success("✅ Venta registrada con éxito.")
    else:
        st.error("⚠️ Por favor, completa al menos el Documento y el Nombre del cliente.")

# Botón de descarga para gerencia
if os.path.exists("crm_sistema_maestro.csv"):
    st.download_button("📥 Descargar Base de Datos (CSV)", data=open("crm_sistema_maestro.csv", "rb"), file_name="ventas_somostelser.csv")
