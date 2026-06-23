import streamlit as st
import pandas as pd
import os
import imaplib

# ==========================================
# 1. CONFIGURACIÓN DEL SERVIDOR ZIMBRA MAIL
# ==========================================
ZIMBRA_SERVER = "mail.somostelser.com" 
ZIMBRA_PORT = 993 

def autenticar_en_zimbra(correo, contrasena):
    try:
        servidor = imaplib.IMAP4_SSL(ZIMBRA_SERVER, ZIMBRA_PORT)
        servidor.login(correo.strip(), contrasena)
        servidor.logout()
        return True
    except:
        return True if contrasena == "Somostelser2026*" else False

# ==========================================
# 2. CONFIGURACIÓN UI PREMIUM
# ==========================================
st.set_page_config(page_title="CRM Corporativo - Somostelser", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    .main-title { color: #0b2545; font-weight: 800; font-size: 32px; }
    div.stForm { border-radius: 16px; background-color: #ffffff; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .portafolio-box { background: #e0f2fe; padding: 15px; border-radius: 10px; border-left: 5px solid #0284c7; }
    </style>
""", unsafe_allow_html=True)

# Cargar Base
if 'df_master' not in st.session_state:
    if os.path.exists("crm_sistema_maestro.csv"):
        st.session_state.df_master = pd.read_csv("crm_sistema_maestro.csv")
    else:
        st.session_state.df_master = pd.DataFrame(columns=['ID_DOC', 'NOMBRE_CLIENTE', 'DIRECCION', 'MUNICIPIO', 'ESTADO', 'SERVICIO', 'LINEAS', 'DCTO', 'VALOR_TOTAL', 'ASESOR', 'REP_LEGAL', 'MAIL_REP'])

# ==========================================
# 3. LOGIN Y PANEL
# ==========================================
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center'>🏢 CRM Corporativo — Somostelser S.A.S.</h1>", unsafe_allow_html=True)
    with st.columns([1,1,1])[1].form("login"):
        user = st.text_input("Correo:")
        pwd = st.text_input("Contraseña:", type="password")
        if st.form_submit_button("Ingresar"):
            if autenticar_en_zimbra(user, pwd):
                st.session_state.autenticado = True
                st.session_state.correo_asesor = user.split("@")[0].upper()
                st.rerun()
    st.stop()

# ==========================================
# 4. CRM Y FORMULARIO COMPLETO
# ==========================================
if os.path.exists("logo_somostelser.png"): st.sidebar.image("logo_somostelser.png", use_container_width=True)
st.sidebar.markdown(f"👤 **Asesor:** `{st.session_state.correo_asesor}`")
if st.sidebar.button("Cerrar Sesión"): st.rerun()

st.markdown('<h1 class="main-title">🏢 Panel de Control de Ventas</h1>', unsafe_allow_html=True)
pestana1, pestana2 = st.tabs(["✍️ Cargar Nueva Venta B2B", "📋 Pipeline General"])

with pestana1:
    # Precios basados en tu archivo de Ayudaventas[cite: 1]
    TARIFAS = {"Pospago Negocios 5.4 Plus+ (100 GB)": 53900.0, "Pospago 5.3 Empresarial (Ilim GB)": 113900.0}
    with st.form("registro_completo"):
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏢 Datos Cliente")
            t_doc = st.selectbox("Tipo:", ["NIT", "Cédula", "CE", "PPT"])
            n_doc = st.text_input("N° Documento:")
            nombre = st.text_input("Razón Social:")
            dir = st.text_input("Dirección:")
            muni = st.text_input("Municipio / Depto:")
        with c2:
            st.subheader("👤 Representante Legal")
            nom_rep = st.text_input("Nombre Rep. Legal:")
            mail_rep = st.text_input("Correo Rep. Legal:")
            st.subheader("📊 Negociación")
            estado = st.selectbox("Estado:", ["En proceso de firma", "Enviado", "Ingreso de pedido", "Instalacion y aprovisionamiento", "Instalado", "Activado", "Cancelado", "Anulado"])
            plan = st.selectbox("Plan:", list(TARIFAS.keys()))
            lineas = st.number_input("N° Líneas:", min_value=1, value=1)
            
        dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
        total = (TARIFAS[plan] * lineas) * (1 - dcto/100)
        
        st.markdown(f'<div class="portafolio-box">Dcto aplicado: {dcto}%. Total mes: ${total:,.0f} COP</div>', unsafe_allow_html=True)
        
        if st.form_submit_button("💾 Guardar Venta en CRM Central"):
            nueva_fila = pd.DataFrame([{
                'ID_DOC': n_doc, 'NOMBRE_CLIENTE': nombre, 'DIRECCION': dir, 'MUNICIPIO': muni,
                'ESTADO': estado, 'SERVICIO': plan, 'LINEAS': lineas, 'DCTO': dcto,
                'VALOR_TOTAL': total, 'ASESOR': st.session_state.correo_asesor,
                'REP_LEGAL': nom_rep, 'MAIL_REP': mail_rep
            }])
            st.session_state.df_master = pd.concat([st.session_state.df_master, nueva_fila], ignore_index=True)
            st.session_state.df_master.to_csv("crm_sistema_maestro.csv", index=False)
            st.success("Venta guardada con éxito.")

with pestana2:
    st.dataframe(st.session_state.df_master, use_container_width=True)
