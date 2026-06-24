import streamlit as st
import pandas as pd
import os
import random

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

if 'correo_asesor' not in st.session_state:
    st.session_state.correo_asesor = None

# --- PANTALLA DE ACCESO ---
if st.session_state.correo_asesor is None:
    st.title("🔐 Acceso al CRM Somos Telser")
    st.write("Por favor, selecciona tu perfil para ingresar:")
    
    usuario_seleccionado = st.selectbox("Usuario:", [
        "", 
        "ADMIN@SOMOSTELSER.COM", 
        "ASESOR1@SOMOSTELSER.COM", 
        "ASESOR2@SOMOSTELSER.COM"
    ])
    
    if st.button("Ingresar al Portal") and usuario_seleccionado != "":
        st.session_state.correo_asesor = usuario_seleccionado
        st.rerun()
    st.stop() # Detiene la app aquí si no han iniciado sesión

# --- SIDEBAR (SI YA INICIÓ SESIÓN) ---
with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_container_width=True)
    
    # Identificador de rol
    es_admin = st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM"
    rol = "👑 Admin" if es_admin else "👤 Asesor"
    st.markdown(f"**{rol}:** `{st.session_state.correo_asesor}`")
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.correo_asesor = None
        st.rerun()

    st.markdown("---")
    st.subheader("🤖 Asistente de Ofertas")
    consulta = st.text_input("Buscar precio:", placeholder="Ej: 500Mbps, 60GB")
    
    if consulta:
        portafolio = {**PLANES_MOVIL, **PLANES_FIJO}
        res = {k: v for k, v in portafolio.items() if consulta.lower() in k.lower()}
        if res:
            seleccion = st.selectbox("Resultados:", list(res.keys()))
            st.metric(label="Precio Sugerido", value=f"${res[seleccion]:,.0f} COP")
        else:
            st.warning("Sin resultados.")

    st.markdown("---")
    st.subheader("📊 Dashboard")
    if os.path.exists("crm_sistema_maestro.csv"):
        try:
            df = pd.read_csv("crm_sistema_maestro.csv")
            
            # --- FILTRO POR ROL ---
            if not es_admin and 'ASESOR' in df.columns:
                df = df[df['ASESOR'] == st.session_state.correo_asesor]
                
            if 'DIVISION' in df.columns and not df.empty:
                # Sumatoria de ingresos para el perfil actual
                st.metric("💰 Ingresos Totales", f"${df['VALOR_TOTAL'].sum():,.0f} COP")
                st.bar_chart(df['DIVISION'].value_counts())
                
                # --- EXPORTAR SOLO PARA ADMIN ---
                if es_admin:
                    st.download_button(
                        label="📥 Exportar CRM a Excel",
                        data=df.to_csv(index=False).encode('utf-8'),
                        file_name='CRM_Ventas_SomosTelser.csv',
                        mime='text/csv'
                    )
            else:
                st.caption("Aún no hay ventas registradas.")
        except: 
            st.caption("Cargando...")

# ==========================================
# 3. INTERFAZ Y AGENTE FINANCIERO
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
st.subheader("Gestión Inteligente de Contratos B2B")

# --- PESTAÑAS PARA CREAR Y ACTUALIZAR ---
tab1, tab2 = st.tabs(["📝 Registrar Nueva Venta", "🔄 Actualizar Seguimiento"])

# ------------------------------------------
# PESTAÑA 1: CREAR VENTA NUEVA
# ------------------------------------------
with tab1:
    div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🏢 Datos del Cliente")
        t_doc = st.selectbox("Tipo Doc:", ["NIT", "CV", "CE", "PPT"])
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
        dir = st.text_input("Dirección:")
        barrio = st.text_input("Barrio:")
        muni = st.text_input("Municipio:")
        email_cli = st.text_input("Departamento:")
        movil_cli = st.text_input("Contacto autorizado:")
        tel_contacto = st.text_input("Móvil Contacto autorizado:")

    with c2:
        st.subheader("👤 Representante Legal")
        nom_rep = st.text_input("Nombre Rep. Legal:")
        cc_rep = st.text_input("Cédula Rep. Legal:")
        mail_rep = st.text_input("Correo Rep. Legal:")
        tel_rep = st.text_input("Móvil Rep. Legal:")
        
        st.subheader("📊 Estado y Plan")
        # El estado inicial se fija en "En proceso de firma" para no confundir al inicio
        estado_inicial = st.selectbox("Estado:", ["En proceso de firma"])
        bitacora = st.text_area("📝 Notas / Bitácora:")
        
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Líneas:", min_value=1, value=1)
        
        # CÁLCULO FINANCIERO DINÁMICO (EN VIVO)
        dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
        valor = (tarifas[servicio] * lineas) * (1 - dcto/100)
        
        # --- NUEVO PANEL DE VALOR COMERCIAL ---
        frases = [
            "🚀 ¡Vamos por ese cierre, hoy es un gran día!",
            "💎 La calidad de tu servicio es nuestra mayor ventaja.",
            "📈 ¡A superar la meta de ventas de este mes!",
            "🤝 Cada cliente cuenta, ¡haz que esta venta sea memorable!",
            "🎯 ¡Enfocados en el objetivo, gran gestión!"
        ]
        
        if valor > 0:
            st.markdown(f"""
            <div style="background-color: #e1f5fe; padding: 12px; border-radius: 10px; border-left: 5px solid #0288d1; margin-bottom: 15px;">
                <p style="margin: 0; font-size: 1.1em; color: #01579b;">💰 <b>Total Estimado:</b> ${valor:,.0f} COP</p>
                <p style="margin: 5px 0 0 0; font-size: 0.85em;"><i>{random.choice(frases)}</i></p>
            </div>
            """, unsafe_allow_html=True)
        
        guardar = st.button("💾 Guardar Venta", use_container_width=True)
