import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. CATÁLOGO MANUAL DE PLANES (JUNIO 2026)
# ==========================================
# Planes Móviles manuales
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

# Planes Fijos manuales
PLANES_FIJO = {
    "Internet Business 300 Mbps (HFC/FTTx)": 88880.0,
    "Internet Business 500 Mbps (HFC/FTTx)": 115000.0,
    "Internet Business 700 Mbps (HFC/FTTx)": 180001.0,
    "Internet Full Tigo Business 500 Mbps": 144000.0,
    "Internet Full Tigo Business 700 Mbps": 174000.0,
    "Internet Full Tigo Business 1000 Mbps": 274000.0
}

# ==========================================
# 2. INTERFAZ Y LÓGICA REACTIVA
# ==========================================
st.set_page_config(page_title="CRM Somos Telser - Junio 2026", layout="wide")

# Inicializar Base
if 'df_master' not in st.session_state:
    if os.path.exists("crm_sistema_maestro.csv"):
        st.session_state.df_master = pd.read_csv("crm_sistema_maestro.csv")
    else:
        st.session_state.df_master = pd.DataFrame(columns=[
            'DIVISION', 'ID_DOC', 'NOMBRE_CLIENTE', 'ESTADO', 'SERVICIO', 
            'VALOR_TOTAL', 'ASESOR', 'MUNICIPIO'
        ])

st.title("🏢 Panel de Gestión de Contratos B2B - Somos Telser")

# Selector de División
div = st.radio("Seleccione División de Negocio:", ["Móvil", "Fijo"], key="div_radio")

with st.form("registro_total"):
    # Datos de Cliente y Rep. Legal
    c1, c2 = st.columns(2)
    with c1:
        n_doc = st.text_input("N° Documento:")
        nombre = st.text_input("Razón Social:")
        muni = st.text_input("Municipio:")
    with c2:
        nom_rep = st.text_input("Nombre Rep. Legal:")
        estado = st.selectbox("Estado del Proceso:", [
            "En proceso de firma", "Enviado", "Ingreso de pedido", 
            "Instalacion y aprovisionamiento", "Instalado", "Activado", 
            "Cancelado", "Anulado"
        ])
    
    st.subheader("Detalle Comercial Manual")
    
    # Selector Dinámico de Planes
    tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
    servicio = st.selectbox("Seleccione el plan específico:", list(tarifas.keys()))
    lineas = st.number_input("Cantidad / Líneas:", min_value=1, value=1)
    
    # Cálculo manual de descuento
    dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
    valor = (tarifas[servicio] * lineas) * (1 - dcto/100)
    
    st.info(f"💰 Resumen: {div} | Plan: {servicio} | Dcto aplicado: {dcto}% | Total: ${valor:,.0f} COP")
    
    if st.form_submit_button("💾 Guardar Registro"):
        nueva_fila = pd.DataFrame([{
            'DIVISION': div, 'ID_DOC': n_doc, 'NOMBRE_CLIENTE': nombre, 
            'ESTADO': estado, 'SERVICIO': servicio, 'VALOR_TOTAL': valor, 
            'ASESOR': "ASESOR_ACTUAL", 'MUNICIPIO': muni
        }])
        st.session_state.df_master = pd.concat([st.session_state.df_master, nueva_fila], ignore_index=True)
        st.session_state.df_master.to_csv("crm_sistema_maestro.csv", index=False)
        st.success("✅ Venta registrada con éxito según portafolio.")

st.dataframe(st.session_state.df_master, use_container_width=True)
