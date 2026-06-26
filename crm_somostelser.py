import streamlit as st
import pandas as pd
import os
import random
import requests
import altair as alt
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
        st.image("logo_somostelser.png", use_column_width=True)
    
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
tab1, tab2, tab3 = st.tabs(["📝 Registrar Venta", "🔄 Actualizar Estado de Venta", "📊 Base de Datos"])

# ------------------------------------------
# 1. DEFINICIÓN DE DATOS (fuera del tab1)
# ------------------------------------------
UBICACIONES_COL = {
    "Amazonas": ["Leticia", "Puerto Nariño"],
    "Antioquia": ["Medellín", "Envigado", "Itagüí", "Bello", "Rionegro", "Sabaneta", "La Estrella", "Caldas"],
    "Arauca": ["Arauca", "Tame", "Saravena"],
    "Atlántico": ["Barranquilla", "Soledad", "Puerto Colombia", "Malambo"],
    "Bolívar": ["Cartagena", "Magangué", "Turbaco"],
    "Boyacá": ["Tunja", "Duitama", "Sogamoso", "Chiquinquirá"],
    "Caldas": ["Manizales", "La Dorada", "Chinchiná"],
    "Caquetá": ["Florencia", "San Vicente del Caguán"],
    "Casanare": ["Yopal", "Aguazul"],
    "Cauca": ["Popayán", "Santander de Quilichao", "Puerto Tejada"],
    "Cesar": ["Valledupar", "Aguachica", "Codazzi"],
    "Chocó": ["Quibdó", "Istmina"],
    "Córdoba": ["Montería", "Lorica", "Cereté"],
    "Cundinamarca": ["Bogotá D.C.", "Soacha", "Chía", "Cajicá", "Zipaquirá", "Fusagasugá", "Facatativá"],
    "Guainía": ["Inírida"],
    "Guaviare": ["San José del Guaviare"],
    "Huila": ["Neiva", "Pitalito", "Garzón"],
    "La Guajira": ["Riohacha", "Maicao", "Uribia"],
    "Magdalena": ["Santa Marta", "Ciénaga"],
    "Meta": ["Villavicencio", "Acacías", "Granada"],
    "Nariño": ["Pasto", "Ipiales", "Tumaco"],
    "Norte de Santander": ["Cúcuta", "Ocaña", "Villa del Rosario"],
    "Putumayo": ["Mocoa", "Puerto Asís"],
    "Quindío": ["Armenia", "Calarcá"],
    "Risaralda": ["Pereira", "Dosquebradas", "Santa Rosa de Cabal"],
    "San Andrés y Providencia": ["San Andrés"],
    "Santander": ["Bucaramanga", "Floridablanca", "Girón", "Piedecuesta", "Barrancabermeja"],
    "Sucre": ["Sincelejo", "Corozal"],
    "Tolima": ["Ibagué", "Espinal", "Melgar", "Honda"],
    "Valle del Cauca": ["Cali", "Palmira", "Buga", "Buenaventura", "Cartago", "Jamundí", "Tuluá"],
    "Vaupés": ["Mitú"],
    "Vichada": ["Puerto Carreño"]
}

# ------------------------------------------
# 2. PESTAÑA 1 INTEGRADA
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
        
        # --- SELECTORES CON BÚSQUEDA PREDICTIVA ---
        depto = st.selectbox(
            "Departamento:", 
            options=sorted(list(UBICACIONES_COL.keys())),
            index=None, 
            placeholder="Escribe para buscar departamento..."
        )
        
        # Lógica para el selector de municipio
        if depto:
            muni = st.selectbox(
                "Municipio:", 
                options=sorted(UBICACIONES_COL[depto]),
                index=None,
                placeholder="Escribe para buscar municipio..."
            )
        else:
            # Mostramos un selector vacío y deshabilitado para mantener el orden visual
            muni = st.selectbox("Municipio:", options=[], disabled=True, placeholder="Selecciona primero un depto")
        
        # ------------------------------------------
        
        email_cli = st.text_input("Email contacto:")
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
            "🎯 ¡Enfocados en el objetivo, excelente gestión!",
            "⚡ ¡Tu energía determina tu éxito, mantén el ritmo!",
            "🌟 Un cliente feliz es la mejor estrategia de crecimiento.",
            "📊 Los buenos datos y una gran estrategia siempre cierran ventas.",
            "🔥 La persistencia vence a la resistencia, ¡tú puedes!",
            "🏆 Los grandes logros nacen de la constancia diaria.",
            "💼 Profesionalismo y visión: así se construyen relaciones duraderas.",
            "🧠 Conecta con el cliente, entiende su necesidad y el cierre será natural.",
            "💡 Cada gestión bien hecha es una semilla para el éxito de mañana.",
            "🥇 ¡No hay límites cuando hay buena planeación y actitud!"
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
# ==========================================
with tab2:
    st.subheader("🔄 Actualizar Seguimiento de Venta")
    
    if os.path.exists("crm_sistema_maestro.csv"):
        df_update = pd.read_csv("crm_sistema_maestro.csv")
        
        # Parches de seguridad
        if 'ESTADO' not in df_update.columns: df_update['ESTADO'] = "En proceso de firma"
        if 'ID_VENTA' not in df_update.columns: df_update['ID_VENTA'] = range(1, len(df_update) + 1)
        if 'CLIENTE' not in df_update.columns: df_update['CLIENTE'] = "Cliente Desconocido"
        
        # Filtro de Asesor
        if not es_admin and 'ASESOR' in df_update.columns:
            df_mis_ventas = df_update[df_update['ASESOR'] == st.session_state.correo_asesor]
        else:
            df_mis_ventas = df_update
            
        if not df_mis_ventas.empty:
            opciones_ventas = df_mis_ventas['ID_VENTA'].astype(str) + " - " + df_mis_ventas['CLIENTE']
            venta_seleccionada = st.selectbox("Selecciona la venta:", opciones_ventas.tolist(), key="select_venta_update")
            
            if venta_seleccionada:
                id_venta = int(venta_seleccionada.split(" - ")[0])
                estado_actual = df_update.loc[df_update['ID_VENTA'] == id_venta, 'ESTADO'].values[0]
                
                st.info(f"📌 Estado Actual: **{estado_actual}**")
                
                nuevo_estado = st.selectbox(
                    "Cambiar estado a:", 
                    ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"],
                    key="select_nuevo_estado_tab2"
                )
                
                if st.button("🔄 Guardar y Notificar", key="btn_guardar_final_tab2"):
                    # 1. Guardar en CSV
                    df_update.loc[df_update['ID_VENTA'] == id_venta, 'ESTADO'] = nuevo_estado
                    df_update.to_csv("crm_sistema_maestro.csv", index=False)
                    
                    # 2. Notificar Telegram
                    mensaje = f"✅ Venta {id_venta} actualizada.\nNuevo estado: {nuevo_estado}"
                    enviar_telegram(mensaje)
                    
                    # 3. Éxito
                    st.success(f"✅ Estado actualizado a '{nuevo_estado}' y notificado.")
                    st.rerun()
        else:
            st.warning("No tienes ventas registradas para actualizar.")
    else:
        st.info("Aún no hay base de datos creada.")
# ==========================================
# PESTAÑA 3: DASHBOARD Y VISUALIZACIÓN DE DATA
# ==========================================
with tab3:
    st.subheader("📊 Dashboard: Gestión de Ventas Somostelser")
    
    # Archivo optimizado y limpio
    archivo = "crm_sistema_maestro.csv"
    
    if os.path.exists(archivo):
        # Leemos el archivo optimizado
        df = pd.read_csv(archivo)
            
        if not df.empty:
            # 1. Métricas Rápidas
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Registros", len(df))
            
            instaladas = len(df[df['ESTADO'] == 'Instalado'])
            c2.metric("Ventas Instaladas", instaladas)
            
            fijos = len(df[df['PORTAFOLIO'] == 'FIJO'])
            moviles = len(df[df['PORTAFOLIO'] == 'MOVIL'])
            c3.metric("Fijo vs Móvil", f"{fijos} | {moviles}")
            
            st.divider()
            
            # 2. Gráficos con Altair (Colores Personalizados)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 Ventas por Estado")
                estado_data = df['ESTADO'].value_counts().reset_index()
                estado_data.columns = ['ESTADO', 'CANTIDAD']
                
                chart1 = alt.Chart(estado_data).mark_bar(color='#2ecc71').encode(
                    x='ESTADO',
                    y='CANTIDAD'
                )
                st.altair_chart(chart1, use_container_width=True)
                
            with col2:
                st.markdown("#### 📊 Portafolio (Fijo vs Móvil)")
                portafolio_data = df['PORTAFOLIO'].value_counts().reset_index()
                portafolio_data.columns = ['PORTAFOLIO', 'CANTIDAD']
                
                chart2 = alt.Chart(portafolio_data).mark_bar().encode(
                    x='PORTAFOLIO',
                    y='CANTIDAD',
                    color=alt.Color('PORTAFOLIO', scale=alt.Scale(range=['#3498db', '#e74c3c']))
                )
                st.altair_chart(chart2, use_container_width=True)
            
            st.divider()
            
            # 3. Dataframe interactivo
            st.markdown("### 📋 Base de Datos Somostelser")
            st.dataframe(df, use_container_width=True)
            
        else:
            st.warning("El archivo CSV no tiene datos.")
    else:
        st.error(f"No se encuentra el archivo {archivo}. Asegúrate de haberlo subido a GitHub.")
