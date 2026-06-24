import streamlit as st
import pandas as pd
import os
import random
from datetime import date

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
if not os.path.exists("documentos_ventas"): os.makedirs("documentos_ventas")

if 'correo_asesor' not in st.session_state: st.session_state.correo_asesor = None

if st.session_state.correo_asesor is None:
    st.title("🔐 Acceso al CRM Somos Telser")
    usuario_seleccionado = st.selectbox("Usuario:", ["", "ADMIN@SOMOSTELSER.COM", "ASESOR1@SOMOSTELSER.COM", "ASESOR2@SOMOSTELSER.COM", "ASESOR3@SOMOSTELSER.COM", "ASESOR4@SOMOSTELSER.COM"])
    if st.button("Ingresar al Portal") and usuario_seleccionado != "":
        st.session_state.correo_asesor = usuario_seleccionado
        st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_somostelser.png"): st.image("logo_somostelser.png", use_container_width=True)
    es_admin = st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM"
    st.markdown(f"**{'👑 Admin' if es_admin else '👤 Asesor'}:** `{st.session_state.correo_asesor}`")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.correo_asesor = None
        st.rerun()

# ==========================================
# 3. INTERFAZ
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
tab1, tab2 = st.tabs(["📝 Registrar Venta", "🔄 Actualizar Estado de Venta"])

with tab1:
    div = st.radio("Seleccione División:", ["Móvil", "Fijo"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
        archivo_adjunto = st.file_uploader("📂 Adjuntar documento:", type=["pdf", "jpg", "png"])
    with c2:
        estado = st.selectbox("Estado:", ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"])
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        valor = tarifas[servicio]
        guardar = st.button("💾 Guardar Venta", use_container_width=True)

    if guardar:
        if n_doc and nombre:
            ruta_archivo = "No aplica"
            if archivo_adjunto:
                ruta_archivo = f"documentos_ventas/{n_doc}_{archivo_adjunto.name}"
                with open(ruta_archivo, "wb") as f: f.write(archivo_adjunto.getbuffer())
            
            archivo = "crm_sistema_maestro.csv"
            df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()
            nueva_fila = pd.DataFrame([{
                'ID_VENTA': len(df_ex) + 1, 
                'ASESOR': st.session_state.correo_asesor, 
                'ESTADO': estado, 
                'CLIENTE': nombre, 
                'DIVISION': div, 
                'VALOR_TOTAL': valor, 
                'RUTA_DOC': ruta_archivo
            }])
            pd.concat([df_ex, nueva_fila]).to_csv(archivo, index=False)
            st.success("✅ Venta registrada correctamente.")
            st.rerun()
        else:
            st.error("⚠️ Faltan datos obligatorios.")

with tab2:
    st.subheader("🔄 Actualizar Seguimiento de Venta")
    if os.path.exists("crm_sistema_maestro.csv"):
        df_update = pd.read_csv("crm_sistema_maestro.csv")
        if not es_admin: df_update = df_update[df_update['ASESOR'] == st.session_state.correo_asesor]
        
        if not df_update.empty:
            opciones = df_update['ID_VENTA'].astype(str) + " - " + df_update['CLIENTE']
            sel = st.selectbox("Selecciona la venta:", opciones.tolist())
            id_v = int(sel.split(" - ")[0])
            nuevo_est = st.selectbox("Cambiar estado:", ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"])
            if st.button("🔄 Guardar Cambio"):
                df_update.loc[df_update['ID_VENTA'] == id_v, 'ESTADO'] = nuevo_est
                df_update.to_csv("crm_sistema_maestro.csv", index=False)
                st.success("✅ Actualizado.")
                st.rerun()
