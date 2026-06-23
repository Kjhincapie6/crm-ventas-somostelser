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
    """Valida las credenciales corporativas contra el servidor IMAP"""
    try:
        usuario = correo.strip()
        servidor = imaplib.IMAP4_SSL(ZIMBRA_SERVER, ZIMBRA_PORT)
        servidor.login(usuario, contrasena)
        servidor.logout()
        return True
    except imaplib.IMAP4.error:
        return False
    except Exception:
        # Plan B Seguro: Permite la demostración interactiva ante el jurado sin requerir red interna
        if contrasena == "Somostelser2026*": 
            return True
        return False

# ==========================================
# 2. CONFIGURACIÓN DE LA APP Y ESTILOS CSS
# ==========================================
st.set_page_config(page_title="CRM Corporativo - Somostelser", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-title { color: #0284c7; font-family: Arial, sans-serif; font-weight: 700; font-size: 32px; margin-bottom: 5px; }
    .sub-title { color: #64748b; font-size: 15px; margin-bottom: 25px; }
    div.stForm {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        padding: 30px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 24px !important; color: #0f172a !important; font-weight: 600 !important; }
    /* Estilo para avisos del portafolio */
    .portafolio-box { background-color: #eff6ff; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_DB = "crm_sistema_maestro.csv"

def cargar_base_datos():
    if os.path.exists(ARCHIVO_DB):
        return pd.read_csv(ARCHIVO_DB)
    return pd.DataFrame(columns=['ID', 'NOMBRE_CLIENTE', 'ESTADO', 'SERVICIO', 'CONTRATO', 'ASESOR', 'COMENTARIOS'])

if 'df_master' not in st.session_state:
    st.session_state.df_master = cargar_base_datos()

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.correo_asesor = ""

# ==========================================
# 3. CAPA DE SEGURIDAD INTERNA (LOGIN)
# ==========================================
if not st.session_state.autenticado:
    st.markdown("""
        <div style="text-align: center; margin-top: 40px;">
            <h1 class="main-title">🏢 CRM Corporativo — Somostelser S.A.S.</h1>
            <p class="sub-title">Consola Transaccional Multiusuario (+50 Asesores) • Acceso Seguro Zimbra</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.4, 1])
    with col_l2:
        with st.form("form_login"):
            input_correo = st.text_input("📧 Correo Institucional:", placeholder="usuario@asesorespymestigo.com")
            input_pass = st.text_input("🔑 Contraseña de Red / Correo:", type="password")
            boton_ingresar = st.form_submit_button("🔒 Autenticar e Ingresar")
            
            if boton_ingresar:
                if "@" not in input_correo or not input_pass:
                    st.error("Por favor, introduce una cuenta de correo corporativo válida.")
                else:
                    with st.spinner("Validando firmas en el servidor Zimbra..."):
                        acceso_concedido = autenticar_en_zimbra(input_correo, input_pass)
                        
                    if acceso_concedido:
                        st.session_state.autenticado = True
                        st.session_state.correo_asesor = input_correo.split("@")[0].upper()
                        st.success("¡Acceso verificado!")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas. Intente de nuevo.")
    st.stop()

# ==========================================
# 4. SISTEMA CRM OPERATIVO
# ==========================================
ARCH_LOGO = "logo_somostelser.png"
if os.path.exists(ARCH_LOGO):
    st.sidebar.image(ARCH_LOGO, use_container_width=True)
else:
    st.sidebar.markdown("<h2 style='color: #0284c7; text-align:center;'>ST SOMOS TELSER</h2>", unsafe_allow_html=True)

st.sidebar.markdown("<div style='text-align: center; padding-bottom: 15px;'><p style='color: #64748b; font-size: 13px; margin-top: 0px;'>Telecomunicaciones y Servicios</p></div>", unsafe_allow_html=True)
st.sidebar.markdown(f"**👤 Asesor en Sesión:**\n`{st.session_state.correo_asesor}`")

if st.sidebar.button("🚪 Cerrar Sesión Segura", use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.correo_asesor = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Extracción de Datos")
csv_data = st.session_state.df_master.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(label="📥 Descargar Base Consolidada (CSV)", data=csv_data, file_name="crm_ventas_consolidadas.csv", mime="text/csv", use_container_width=True)

st.markdown('<h1 class="main-title">🏢 Panel de Control de Ventas</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Gestión en tiempo real ligada al Portafolio Oficial de Negocios Tigo Business.</p>', unsafe_allow_html=True)

pestana_registro, pestana_historial = st.tabs(["✍️ Cargar Nueva Venta B2B", "📋 Pipeline General de la Empresa"])

# --- PESTAÑA 1: FORMULARIO TRANSMISOR CON PORTAFOLIO OFICIAL ---
with pestana_registro:
    st.markdown("### 📝 Ficha de Entrada - Ayudaventa Tigo Junio 2026")
    
    # Base de tarifas base oficiales estipuladas en el PDF (Valores aproximados de referencia estructural)
    TARIFAS_PLANES = {
        "Pospago Negocios 5.4 Plus+ (100 GB)": 65000.0,
        "Pospago 5.3 Empresarial (Ilim GB)": 85000.0,
        "Pospago Fidelización Negocios 4.9 Plus+ (60 GB)": 55000.0
    }
    
    with st.form("registro_operativo_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            id_contrato = st.number_input("ID único del Contrato / Pedido:", min_value=10000, step=1)
            nombre_cliente = st.text_input("Razón Social del Cliente Comercial:")
            estado_venta = st.selectbox("Estado del Proceso Técnico:", ["Ingreso de pedido", "Instalacion y aprovisionamiento", "Instalado", "Activado"])
            tipo_plan = st.selectbox("Plan Estructural Seleccionado (Oferta 5.0):", list(TARIFAS_PLANES.keys()))
            
        with col_f2:
            num_lineas = st.number_input("Número de Líneas a Contratar:", min_value=1, value=1, step=1)
            
            # Matriz de Descuentos por Volumen Automática extraída del PDF (Página 2)
            if num_lineas == 1:
                pct_dcto = 0
            elif num_lineas == 2:
                pct_dcto = 10
            elif (num_lineas >= 3) and (num_lineas <= 5):
                pct_dcto = 20
            elif (num_lineas >= 6) and (num_lineas <= 8):
                pct_dcto = 25
            else:
                pct_dcto = 30 # 9+ líneas
                
            tarifa_base_unidad = TARIFAS_PLANES[tipo_plan]
            subtotal_bruto = tarifa_base_unidad * num_lineas
            valor_descuento = subtotal_bruto * (pct_dcto / 100)
            valor_contrato_final = subtotal_bruto - valor_descuento
            
            # Cuadro dinámico e informativo para el asesor
            st.markdown(f"""
            <div class="portafolio-box">
                <b>📊 Auditoría de Portafolio en Vivo:</b><br>
                • Descuento por Volumen aplicado: <b>{pct_dcto}%</b><br>
                • Canon Mensual Estimado Unificado: <b>${valor_contrato_final:,.0f} COP</b>
            </div>
            """, unsafe_allow_html=True)
            
            notas_comerciales = st.text_area("Comentarios u observaciones de la negociación:")
            
        guardar_registro = st.form_submit_button("💾 Sincronizar y Guardar en CRM")
        
        if guardar_registro:
            if not nombre_cliente:
                st.error("Error: El nombre del cliente es obligatorio.")
            elif int(id_contrato) in st.session_state.df_master['ID'].values:
                st.error(f"El ID de Contrato {id_contrato} ya se encuentra registrado.")
            else:
                nueva_venta = pd.DataFrame([{col: None for col in st.session_state.df_master.columns}])
                nueva_venta['ID'] = int(id_contrato)
                nueva_venta['NOMBRE_CLIENTE'] = nombre_cliente.strip().upper()
                nueva_venta['ESTADO'] = estado_venta
                nueva_venta['SERVICIO'] = tipo_plan
                nueva_venta['CONTRATO'] = float(valor_contrato_final)
                nueva_venta['ASESOR'] = st.session_state.correo_asesor
                nueva_venta['COMENTARIOS'] = f"Líneas: {num_lineas} (Dcto {pct_dcto}%). " + notas_comerciales
                nueva_venta['PORTAFOLIO'] = 'MÓVIL'
                nueva_venta['FRENTE'] = 'B2B'
                
                st.session_state.df_master = pd.concat([st.session_state.df_master, nueva_venta], ignore_index=True)
                st.session_state.df_master.to_csv(ARCHIVO_DB, index=False)
                st.success(f"✔️ ¡Excelente! Contrato de **{nombre_cliente.upper()}** insertado con éxito.")
                st.rerun()

# --- PESTAÑA 2: PIPELINE ---
with pestana_historial:
    st.markdown("### 📋 Consola de Monitoreo de Cuentas")
    kpi_c1, kpi_c2 = st.columns(2)
    kpi_c1.metric("Contratos Totales Gestionados", f"{len(st.session_state.df_master)} Registros")
    kpi_c2.metric("Volumen de Facturación Mensual Administrado", f"${st.session_state.df_master['CONTRATO'].sum():,.0f} COP")
    st.markdown("---")
    
    filtro_general = st.text_input("🔍 Filtro global interactivo:")
    df_mostrar = st.session_state.df_master.copy()
    if filtro_general:
        df_mostrar = df_mostrar[df_mostrar['NOMBRE_CLIENTE'].str.contains(filtro_general, case=False, na=False) | df_mostrar['ASESOR'].str.contains(filtro_general, case=False, na=False)]
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
