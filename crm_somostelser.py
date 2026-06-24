import streamlit as st
import pandas as pd
import os
import random
import requests
from datetime import date

# ==========================================
# TELEGRAM
# ==========================================
# 1. Función definida al inicio (fuera de cualquier 'with' o 'if')
def enviar_telegram(mensaje):
    TOKEN = "8942591199:AAFi8vkAvNyL4LLkUPO9TXKhC2bjukEDmcg" 
    # REEMPLAZA EL ID DE ABAJO POR TU ID NUMÉRICO REAL (sin @)
    CHAT_ID = "1415966548" 
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensaje}
    
    try:
        respuesta = requests.get(url, params=params)
        if respuesta.status_code == 200:
            st.success("✅ ¡Mensaje enviado!")
        else:
            st.error(f"❌ Error {respuesta.status_code}: {respuesta.text}")
    except Exception as e:
        st.error(f"❌ Error: {e}")

    # ... tu código existente de selectbox y ventas ..

# --- DEFINICIÓN SEGURA INICIAL (ESTO VA DE PRIMERO) ---
if 'correo_asesor' not in st.session_state:
    st.session_state.correo_asesor = None

es_admin = False 
if st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM":
    es_admin = True

# --- CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

# ... (Aquí sigue el resto de tu código de login, sidebar, etc.)

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
if 'correo_asesor' not in st.session_state:
    st.session_state.correo_asesor = None

# --- PANTALLA DE ACCESO ---
if st.session_state.correo_asesor is None:
    st.title("🔐 Acceso al CRM Somos Telser")
    st.write("Por favor, selecciona tu perfil e ingresa la contraseña:")
    
    usuario_seleccionado = st.selectbox("Usuario:", [
        "", 
        "ADMIN@SOMOSTELSER.COM", 
        "ASESOR1@SOMOSTELSER.COM", 
        "ASESOR2@SOMOSTELSER.COM",
        "ASESOR3@SOMOSTELSER.COM",
        "ASESOR4@SOMOSTELSER.COM"
    ], key="select_usuario")
    
    password = st.text_input("Contraseña:", type="password", key="pass_input")
    
    # Botón de Login único
    if st.button("Ingresar al Portal", key="btn_login"):
        if usuario_seleccionado != "" and password == "Telser2026":
            st.session_state.correo_asesor = usuario_seleccionado
            st.rerun()
        elif usuario_seleccionado == "":
            st.warning("Por favor, selecciona un usuario.")
        else:
            st.error("Contraseña incorrecta.")
            
    st.stop() 

# --- DEFINIR ROL ---
es_admin = st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM"

# --- SIDEBAR (SI YA INICIÓ SESIÓN) ---
with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_container_width=True)
    
    # Identificador de rol
    rol = "👑 Admin" if es_admin else "👤 Asesor"
    st.markdown(f"**{rol}:** `{st.session_state.correo_asesor}`")
    
    # Aquí siguen tus Tareas Pendientes...

# --- TAREAS PENDIENTES ---
    st.markdown("---")
    st.subheader("🔔 Tareas Pendientes")
    if os.path.exists("crm_sistema_maestro.csv"):
        df_tasks = pd.read_csv("crm_sistema_maestro.csv")
        if 'FECHA_SEGUIMIENTO' in df_tasks.columns:
            df_tasks['FECHA_SEGUIMIENTO'] = pd.to_datetime(df_tasks['FECHA_SEGUIMIENTO'])
            hoy = pd.Timestamp(date.today())
            
            # CAMBIO AQUÍ: Filtramos solo para Cotizado o En proceso de firma
            pendientes = df_tasks[
                (df_tasks['FECHA_SEGUIMIENTO'] <= hoy) & 
                (df_tasks['ESTADO'].isin(['Cotizado', 'En proceso de firma']))
            ]
            
            if not es_admin: 
                pendientes = pendientes[pendientes['ASESOR'] == st.session_state.correo_asesor]
            
            if not pendientes.empty:
                for _, row in pendientes.iterrows(): 
                    st.warning(f"📞 {row['CLIENTE']} | {row['TIPO_SEGUIMIENTO']}")
            else: 
                st.success("¡Todo al día!")
                
    
        # Identificador de rol
    
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

# --- LAS PESTAÑAS ---
tab1, tab2 = st.tabs(["📝 Registrar Venta", "🔄 Actualizar Estado de Venta"])

# ------------------------------------------
# PESTAÑA 1: TU CÓDIGO ORIGINAL INTACTO
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
        estado = st.selectbox("Estado:", ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"])
        bitacora = st.text_area("📝 Notas / Bitácora:")
        
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Líneas:", min_value=1, value=1)
        
        # CÁLCULO FINANCIERO DINÁMICO
        dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
        valor = (tarifas[servicio] * lineas) * (1 - dcto/100)
        
        # PANEL DE VALOR COMERCIAL
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

        st.subheader("📎 Documentos del Cliente")

        archivo_subido = st.file_uploader(
            "Adjuntar documentos",
            type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"],
            accept_multiple_files=True
        )

        if archivo_subido:
            st.success(f"📎 {len(archivo_subido)} documento(s) seleccionado(s)")

    guardar = st.button("💾 Guardar Venta", key="btn_guardar_venta_tab1", use_container_width=True)

    if guardar:
        if n_doc and nombre:

            carpeta_documentos = "documentos_clientes"

            if not os.path.exists(carpeta_documentos):
                os.makedirs(carpeta_documentos)

            archivos_guardados = []

            if archivo_subido:
                for archivo_doc in archivo_subido:
                    nombre_archivo = f"{n_doc}_{archivo_doc.name}"
                    ruta_archivo = os.path.join(
                        carpeta_documentos,
                        nombre_archivo
                    )

                    with open(ruta_archivo, "wb") as f:
                        f.write(archivo_doc.getbuffer())

                    archivos_guardados.append(nombre_archivo)

            archivo = "crm_sistema_maestro.csv"
            df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()

            nueva_fila = pd.DataFrame([{
                'ID_VENTA': len(df_ex) + 1,
                'ASESOR': st.session_state.correo_asesor,
                'ESTADO': estado,
                'DIVISION': div,
                'NIT': n_doc,
                'CLIENTE': nombre,
                'SERVICIO': servicio,
                'VALOR_TOTAL': valor,
                'BITACORA': bitacora,
                'DOCUMENTOS': ";".join(archivos_guardados),
                'ESTADO_FINANCIERO': (
                    "APROBADO" if valor >= 35000 else "REVISION"
                )
            }])

            pd.concat([df_ex, nueva_fila], ignore_index=True).to_csv(
                archivo,
                index=False
            )

            st.success("✅ Venta registrada correctamente.")
            st.rerun()

        else:
            st.error("⚠️ Faltan datos obligatorios.")
# ==========================================
# PESTAÑA 2: ACTUALIZAR EL ESTADO
# ------------------------------------------
with tab2:
    st.subheader("🔄 Actualizar Seguimiento de Venta")
    
    if os.path.exists("crm_sistema_maestro.csv"):
        df_update = pd.read_csv("crm_sistema_maestro.csv")
        
        # --- PARCHES DE SEGURIDAD PARA CSV ANTIGUOS ---
        if 'ESTADO' not in df_update.columns:
            df_update['ESTADO'] = "En proceso de firma"
        if 'ID_VENTA' not in df_update.columns:
            df_update['ID_VENTA'] = range(1, len(df_update) + 1)
        if 'CLIENTE' not in df_update.columns:
            df_update['CLIENTE'] = "Cliente Desconocido"
            
        if not es_admin and 'ASESOR' in df_update.columns:
            df_mis_ventas = df_update[df_update['ASESOR'] == st.session_state.correo_asesor]
        else:
            df_mis_ventas = df_update
            
        if not df_mis_ventas.empty:
            opciones_ventas = df_mis_ventas['ID_VENTA'].astype(str) + " - " + df_mis_ventas['CLIENTE']
            venta_seleccionada = st.selectbox("Selecciona la venta que deseas actualizar:", opciones_ventas.tolist())
            
            if venta_seleccionada:
                id_venta = int(venta_seleccionada.split(" - ")[0])
                estado_actual = df_update.loc[df_update['ID_VENTA'] == id_venta, 'ESTADO'].values[0]
                
                st.info(f"📌 Estado Actual: **{estado_actual}**")
                
                nuevo_estado = st.selectbox(
                    "Cambiar estado a:", 
                    ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"]
                )
                
                if st.button("🔄 Guardar Nuevo Estado", key="btn_guardar_estado_tab2", use_container_width=True):
                    df_update.loc[df_update['ID_VENTA'] == id_venta, 'ESTADO'] = nuevo_estado
                    df_update.to_csv("crm_sistema_maestro.csv", index=False)
                    st.success(f"✅ El estado de la venta ha sido actualizado a '{nuevo_estado}'.")
                    st.rerun()
        else:
            st.warning("No tienes ventas registradas para actualizar.")
    else:
        st.info("Aún no hay base de datos creada. Registra una venta primero.")

