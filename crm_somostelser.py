import streamlit as st
import pandas as pd
import os
import imaplib

# ==========================================
# 1. PORTAFOLIO Y DATOS (JUNIO 2026)
# ==========================================
PLANES_MOVIL = {
    "Pospago Fidelización Negocios 4.9 Plus+ (60 GB)": 55000.0,
    "Pospago Negocios 5.4 Plus+ (100 GB)": 65000.0,
    "Pospago 5.3 Empresarial (Ilim GB)": 113900.0
}

PLANES_FIJO = {
    "Internet Business 300 Mbps": 88880.0,
    "Internet Business 500 Mbps": 115000.0,
    "Internet Business 700 Mbps": 180001.0,
    "Full Tigo Business Seguro 500Mbps": 144000.0
}

# ==========================================
# 2. CONFIGURACIÓN Y SEGURIDAD
# ==========================================
def autenticar_en_zimbra(correo, contrasena):
    return True if contrasena == "Somostelser2026*" else False

st.set_page_config(page_title="CRM Somos Telser - Junio 2026", layout="wide")

if 'df_master' not in st.session_state:
    if os.path.exists("crm_sistema_maestro.csv"):
        st.session_state.df_master = pd.read_csv("crm_sistema_maestro.csv")
    else:
        st.session_state.df_master = pd.DataFrame(columns=[
            'DIVISION', 'ID_DOC', 'NOMBRE_CLIENTE', 'DIRECCION', 'MUNICIPIO', 
            'ESTADO', 'SERVICIO', 'LINEAS', 'VALOR_TOTAL', 'ASESOR', 
            'REP_LEGAL', 'MAIL_REP'
        ])

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center; color:#0b2545;'>🏢 CRM Corporativo Somos Telser</h1>", unsafe_allow_html=True)
    with st.columns([1,1,1])[1].form("login"):
        user = st.text_input("Correo Corporativo:")
        pwd = st.text_input("Contraseña:", type="password")
        if st.form_submit_button("Ingresar al Sistema"):
            if autenticar_en_zimbra(user, pwd):
                st.session_state.autenticado = True
                st.session_state.correo_asesor = user.split("@")[0].upper()
                st.rerun()
    st.stop()

# ==========================================
# 3. INTERFAZ PRINCIPAL
# ==========================================
if st.sidebar.button("Cerrar Sesión"): 
    st.session_state.autenticado = False
    st.rerun()

st.title("🏢 Panel de Gestión de Contratos B2B")
pestana1, pestana2 = st.tabs(["✍️ Cargar Venta", "📋 Pipeline Maestro"])

with pestana1:
    # FILTRO DE DIVISIÓN REACTIVO
    div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio")
    
    with st.form("registro_total"):
        col_cli, col_rep = st.columns(2)
        with col_cli:
            st.subheader("Datos Cliente")
            t_doc = st.selectbox("Tipo:", ["NIT", "Cédula", "CE", "PPT"])
            n_doc = st.text_input("Documento:")
            nombre = st.text_input("Razón Social:")
            dir = st.text_input("Dirección:")
            muni = st.text_input("Municipio:")
        with col_rep:
            st.subheader("Rep. Legal")
            nom_rep = st.text_input("Nombre:")
            mail_rep = st.text_input("Correo:")
            estado = st.selectbox("Estado:", ["En proceso de firma", "Enviado", "Ingreso de pedido", "Instalacion y aprovisionamiento", "Instalado", "Activado", "Cancelado", "Anulado"])
            
        st.subheader("Detalle Comercial")
        
        # Lógica dinámica según división
        tarifas_activas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        
        c_plan, c_lineas = st.columns(2)
        with c_plan:
            servicio = st.selectbox("Servicio:", list(tarifas_activas.keys()))
        with c_lineas:
            lineas = st.number_input("Cantidad / Líneas:", min_value=1, value=1)
            
        # Cálculo de descuento según volumen de líneas[cite: 1]
        dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
        valor = (tarifas_activas[servicio] * lineas) * (1 - dcto/100)
        
        st.info(f"💰 Resumen: {div} | Servicio: {servicio} | Dcto aplicado: {dcto}% | Total estimado: ${valor:,.0f} COP")
        
        if st.form_submit_button("💾 Guardar Registro Completo"):
            nueva_fila = pd.DataFrame([{
                'DIVISION': div, 'ID_DOC': n_doc, 'NOMBRE_CLIENTE': nombre, 'DIRECCION': dir, 
                'MUNICIPIO': muni, 'ESTADO': estado, 'SERVICIO': servicio, 'LINEAS': lineas, 
                'VALOR_TOTAL': valor, 'ASESOR': st.session_state.correo_asesor, 
                'REP_LEGAL': nom_rep, 'MAIL_REP': mail_rep
            }])
            st.session_state.df_master = pd.concat([st.session_state.df_master, nueva_fila], ignore_index=True)
            st.session_state.df_master.to_csv("crm_sistema_maestro.csv", index=False)
            st.success("✅ Venta registrada correctamente bajo estándares Junio 2026.")

with pestana2:
    st.dataframe(st.session_state.df_master, use_container_width=True)
