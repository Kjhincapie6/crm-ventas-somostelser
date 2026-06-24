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
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="centered")

st.title("📡 Portal de Ventas Somos Telser")
st.subheader("Gestión de Contratos B2B")

div = st.radio("División:", ["Móvil", "Fijo"], horizontal=True)
tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO

# ==========================================
# 3. FORMULARIO DE REGISTRO
# ==========================================
with st.form("registro", clear_on_submit=True):
    n_doc = st.text_input("NIT / Documento:")
    nombre = st.text_input("Razón Social o Nombre:")
    servicio = st.selectbox("Plan:", list(tarifas.keys()))
    lineas = st.number_input("Cantidad / Líneas:", min_value=1, value=1)
    
    valor_final = tarifas[servicio] * lineas
    st.info(f"💰 **Total: ${valor_final:,.0f} COP**")
    
    guardar = st.form_submit_button("💾 Guardar Venta")

if guardar:
    if n_doc and nombre:
        archivo = "crm_sistema_maestro.csv"
        df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()
        nueva_fila = pd.DataFrame([{
            'NIT': n_doc, 'CLIENTE': nombre, 'SERVICIO': servicio, 'VALOR': valor_final
        }])
        pd.concat([df_ex, nueva_fila]).to_csv(archivo, index=False)
        st.success("✅ Venta registrada.")
    else:
        st.error("⚠️ Faltan datos.")
