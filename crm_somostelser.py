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
# 2. CONFIGURACIÓN E IDENTIDAD (LOGIN)
# ==========================================
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

CONTRASENA_MAESTRA = "Telser2026"

if 'correo_asesor' not in st.session_state: st.session_state.correo_asesor = None
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- PANTALLA DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🔐 Acceso al CRM Somos Telser")
    usuario_seleccionado = st.selectbox("Usuario:", ["", "ADMIN@SOMOSTELSER.COM", "ASESOR1@SOMOSTELSER.COM", "ASESOR2@SOMOSTELSER.COM", "ASESOR3@SOMOSTELSER.COM", "ASESOR4@SOMOSTELSER.COM"])
    pass_input = st.text_input("Contraseña:", type="password")
    
    if st.button("Ingresar al Portal"):
        if usuario_seleccionado != "" and pass_input == CONTRASENA_MAESTRA:
            st.session_state.correo_asesor = usuario_seleccionado
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("⚠️ Usuario o contraseña incorrectos")
    st.stop()

# --- SIDEBAR (SI YA INICIÓ SESIÓN) ---
with st.sidebar:
    if os.path.exists("logo_somostelser.png"): st.image("logo_somostelser.png", use_container_width=True)
    
    es_admin = st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM"
    rol = "👑 Admin" if es_admin else "👤 Asesor"
    st.markdown(f"**{rol}:** `{st.session_state.correo_asesor}`")
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.correo_asesor = None
        st.session_state.autenticado = False
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

    st.markdown("---")
    st.subheader("🤖 Asistente de Ofertas")
    consulta = st.text_input("Buscar precio:", placeholder="Ej: 500Mbps, 60GB")
    if consulta:
        portafolio = {**PLANES_MOVIL, **PLANES_FIJO}
        res = {k: v for k, v in portafolio.items() if consulta.lower() in k.lower()}
        if res:
            seleccion = st.selectbox("Resultados:", list(res.keys()))
            st.metric(label="Precio Sugerido", value=f"${res[seleccion]:,.0f} COP")
        else: st.warning("Sin resultados.")

    st.markdown("---")
    st.subheader("📊 Dashboard")
    if os.path.exists("crm_sistema_maestro.csv"):
        try:
            df = pd.read_csv("crm_sistema_maestro.csv")
            if not es_admin and 'ASESOR' in df.columns: df = df[df['ASESOR'] == st.session_state.correo_asesor]
            if 'DIVISION' in df.columns and not df.empty:
                st.metric("💰 Ingresos Totales", f"${df['VALOR_TOTAL'].sum():,.0f} COP")
                st.bar_chart(df['DIVISION'].value_counts())
                if es_admin:
                    st.download_button("📥 Exportar CRM a Excel", data=df.to_csv(index=False).encode('utf-8'), file_name='CRM_Ventas_SomosTelser.csv', mime='text/csv')
        except: st.caption("Cargando...")

# ==========================================
# 3. INTERFAZ Y AGENTE FINANCIERO
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
st.subheader("Gestión Inteligente de Contratos B2B")
tab1, tab2 = st.tabs(["📝 Registrar Venta", "🔄 Actualizar Estado de Venta"])

with tab1:
    div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏢 Datos del Cliente")
        t_doc = st.selectbox("Tipo Doc:", ["NIT", "CV", "CE", "PPT"])
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
    with c2:
        st.subheader("📊 Estado y Plan")
        estado = st.selectbox("Estado:", ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"])
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        guardar = st.button("💾 Guardar Venta", use_container_width=True)

    if guardar:
        if n_doc and nombre:
            archivo = "crm_sistema_maestro.csv"
            df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()
            nueva_fila = pd.DataFrame([{'ID_VENTA': len(df_ex)+1, 'ASESOR': st.session_state.correo_asesor, 'ESTADO': estado, 'CLIENTE': nombre, 'VALOR_TOTAL': tarifas[servicio]}])
            pd.concat([df_ex, nueva_fila]).to_csv(archivo, index=False)
            st.success("✅ Venta registrada.")
            st.rerun()

with tab2:
    st.subheader("🔄 Actualizar Seguimiento")
    if os.path.exists("crm_sistema_maestro.csv"):
        df_up = pd.read_csv("crm_sistema_maestro.csv")
        if not es_admin: df_up = df_up[df_up['ASESOR'] == st.session_state.correo_asesor]
        if not df_up.empty:
            sel = st.selectbox("Selecciona venta:", df_up['ID_VENTA'].astype(str) + " - " + df_up['CLIENTE'])
            id_v = int(sel.split(" - ")[0])
            nuevo_est = st.selectbox("Nuevo Estado:", ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"])
            if st.button("🔄 Guardar Cambio"):
                df_up.loc[df_up['ID_VENTA'] == id_v, 'ESTADO'] = nuevo_est
                df_up.to_csv("crm_sistema_maestro.csv", index=False)
                st.rerun()
