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
# 2. CONFIGURACIÓN E IDENTIDAD (SISTEMA DE LOGIN)
# ==========================================
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

if not os.path.exists("documentos_ventas"): os.makedirs("documentos_ventas")

if 'correo_asesor' not in st.session_state:
    st.session_state.correo_asesor = None

# --- PANTALLA DE ACCESO ---
if st.session_state.correo_asesor is None:
    st.title("🔐 Acceso al CRM Somos Telser")
    usuario_seleccionado = st.selectbox("Usuario:", ["", "ADMIN@SOMOSTELSER.COM", "ASESOR1@SOMOSTELSER.COM", "ASESOR2@SOMOSTELSER.COM"])
    if st.button("Ingresar al Portal") and usuario_seleccionado != "":
        st.session_state.correo_asesor = usuario_seleccionado
        st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    es_admin = st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM"
    st.markdown(f"**{'👑 Admin' if es_admin else '👤 Asesor'}:** `{st.session_state.correo_asesor}`")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.correo_asesor = None
        st.rerun()

    st.markdown("---")
    st.subheader("🔔 Tareas Pendientes")
    if os.path.exists("crm_sistema_maestro.csv"):
        df_tasks = pd.read_csv("crm_sistema_maestro.csv")
        if 'FECHA_SEGUIMIENTO' in df_tasks.columns:
            df_tasks['FECHA_SEGUIMIENTO'] = pd.to_datetime(df_tasks['FECHA_SEGUIMIENTO'])
            hoy = pd.Timestamp(date.today())
            pendientes = df_tasks[(df_tasks['FECHA_SEGUIMIENTO'] <= hoy) & (~df_tasks['ESTADO'].isin(['Activado', 'Anulado']))]
            if not es_admin: pendientes = pendientes[pendientes['ASESOR'] == st.session_state.correo_asesor]
            for _, row in pendientes.iterrows(): st.warning(f"📞 {row['CLIENTE']} | {row['TIPO_SEGUIMIENTO']}")
            else: st.success("¡Todo al día!")

# ==========================================
# 3. INTERFAZ
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
tab1, tab2 = st.tabs(["📝 Registrar Venta", "🔄 Actualizar Seguimiento"])

with tab1:
    div = st.radio("Seleccione División:", ["Móvil", "Fijo"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏢 Datos del Cliente")
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
        # --- Campo de documento ---
        uploaded_file = st.file_uploader("📂 Adjuntar documento:", type=["pdf", "jpg", "png"])
    with c2:
        st.subheader("📊 Estado, Plan y Seguimiento")
        estado = st.selectbox("Estado:", ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"])
        fecha_seg = st.date_input("📅 Fecha de Seguimiento:", value=date.today())
        tipo_seg = st.selectbox("Tipo de Acción:", ["Llamada", "Visita Presencial", "Envío Correo", "Seguimiento WhatsApp"])
        
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Líneas:", min_value=1, value=1)
        valor = (tarifas[servicio] * lineas) * (1 - (30 if lineas >= 9 else 25 if lineas >= 6 else 20 if lineas >= 3 else 10 if lineas == 2 else 0)/100)
        guardar = st.button("💾 Guardar Venta", use_container_width=True)

    if guardar:
        ruta_archivo = "No aplica"
        if uploaded_file:
            ruta_archivo = f"documentos_ventas/{n_doc}_{uploaded_file.name}"
            with open(ruta_archivo, "wb") as f: f.write(uploaded_file.getbuffer())
        
        archivo = "crm_sistema_maestro.csv"
        df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()
        nueva_fila = pd.DataFrame([{
            'ID_VENTA': len(df_ex) + 1, 'ASESOR': st.session_state.correo_asesor, 'ESTADO': estado,
            'DOCUMENTO_RUTA': ruta_archivo, 'FECHA_SEGUIMIENTO': fecha_seg, 'TIPO_SEGUIMIENTO': tipo_seg,
            'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre, 'SERVICIO': servicio, 'VALOR_TOTAL': valor, 
            'BITACORA': "", 'ESTADO_FINANCIERO': ("APROBADO" if valor >= 35000 else "REVISION")
        }])
        pd.concat([df_ex, nueva_fila]).to_csv(archivo, index=False)
        st.success("✅ Venta registrada.")
        st.rerun()

with tab2:
    if os.path.exists("crm_sistema_maestro.csv"):
        df_up = pd.read_csv("crm_sistema_maestro.csv")
        if not es_admin: df_up = df_up[df_up['ASESOR'] == st.session_state.correo_asesor]
        
        if not df_up.empty:
            venta_idx = st.selectbox("Selecciona venta:", df_up['ID_VENTA'].astype(str) + " - " + df_up['CLIENTE'])
            id_v = int(venta_idx.split(" - ")[0])
            nuevo_est = st.selectbox("Cambiar estado a:", ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"])
            if st.button("🔄 Actualizar"):
                df_up.loc[df_up['ID_VENTA'] == id_v, 'ESTADO'] = nuevo_est
                df_up.to_csv("crm_sistema_maestro.csv", index=False)
                st.success("✅ Actualizado.")
                st.rerun()
