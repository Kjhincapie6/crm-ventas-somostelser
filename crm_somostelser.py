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
# 1. Definimos las pestañas base
nombres_pestanas = ["Registrar Venta", "Actualizar Estado de Venta"]

# 2. Verificación de Administrador (usando el correo para mayor seguridad)
es_admin = st.session_state.get('correo_asesor') == "ADMIN@SOMOSTELSER.COM"

if es_admin:
    nombres_pestanas.append("Base de Datos")

# 3. Creamos las pestañas dinámicamente
tabs = st.tabs(nombres_pestanas)

# 4. Asignamos variables de forma segura
tab1 = tabs[0]
tab2 = tabs[1]

if es_admin:
    tab3 = tabs[2]

# ------------------------------------------
# USO DE LAS PESTAÑAS (Protegiendo el acceso)
# ------------------------------------------

with tab1:
    # ... tu código de registro ...
    pass

with tab2:
    # ... tu código de actualización ...
    pass

if es_admin:
    with tab3:
        # AQUÍ VA TODO TU CÓDIGO DEL DASHBOARD
        st.subheader("📊 Dashboard: Gestión de Ventas Somostelser")
        # ... resto de tu lógica de gráficos ...

# ------------------------------------------
# 1. DEFINICIÓN DE DATOS (fuera del tab1)
# ------------------------------------------
UBICACIONES_COL = {
    "Amazonas": ["Leticia", "Puerto Nariño"],
    "Antioquia": ["Medellín", "Envigado", "Itagüí", "Bello", "Rionegro", "Sabaneta", "La Estrella", "Caldas","Retiro"],
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

        st.subheader("⚙️ Gestión Técnica") 
        # --- VENTANA FLOTANTE (POPOVER) ---
        datos_moviles = {"tipo": "N/A", "op": "N/A", "num": "N/A", "cant": 1}
       # Asegúrate de que esta línea esté alineada con el código de arriba
    if 'lista_lineas' not in st.session_state:
        st.session_state.lista_lineas = []

    # El 'with' del popover debe tener EXACTAMENTE la misma sangría que el 'if' de arriba
    with st.popover("📱 Configurar Líneas Móviles (Click aquí)"):
        # Estos inputs temporales capturan los datos de una sola línea
        tipo = st.radio("Tipo de gestión:", ["Portabilidad", "Línea Nueva", "Línea Existente"], key="gest_m_tab1")
        op = "N/A"
        if tipo == "Portabilidad":
            op = st.selectbox("Operador Origen:", ["Claro", "Movistar", "Móvil Éxito", "Wom"], key="op_m_tab1")
        num = st.text_input("Número de línea:", key="num_m_tab1")
        
        # BOTÓN PARA ACUMULAR
        if st.button("➕ Agregar esta línea a la venta"):
            nueva_linea = {"cantidad": cant, "tipo": tipo, "operador": op, "numero": num}
            st.session_state.lista_lineas.append(nueva_linea)
            st.success(f"Línea {num} agregada a la lista")
        else:
            st.info("La gestión móvil aplica tambien para Full tigo.")
            datos_moviles["cant"] = st.number_input("Cantidad:", min_value=1, value=1, key="cant_f_tab1")

        # --- BOTÓN DE CIERRE MANUAL ---
        if st.button("💾 Registrar Linea y Cerrar Venta", key="btn_save_tab1", type="primary", use_container_width=True):
            if n_doc and nombre:
                # Lógica de guardado en CSV
                archivo = "crm_sistema_maestro.csv"
                df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()
                
                nueva_fila = pd.DataFrame([{
                    'CLIENTE': nombre,
                    'NIT': n_doc,
                    'TIPO_PERSONA': tipo_pers,
                    'DIVISION': div,
                    'CANTIDAD_LINEAS': datos_moviles["cant"],
                    'TIPO_GESTION': datos_moviles["tipo"],
                    'OPERADOR': datos_moviles["op"],
                    'NUM_LINEA': datos_moviles["num"]
                }])
                
                pd.concat([df_ex, nueva_fila], ignore_index=True).to_csv(archivo, index=False)
                st.success("✅ Venta guardada exitosamente.")
                st.rerun() # Esto refresca la app para limpiar el formulario
            else:
                st.error("⚠️ Faltan datos del titular.")

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
        
        # 🔄 Título dinámico: Si es Móvil dice "Líneas:", si no, dice "Cantidad:"
        titulo_cantidad = "Líneas:" if div == "Móvil" else "Cantidad:"
        lineas = st.number_input(titulo_cantidad, min_value=1, value=1)
        # --- NUEVA LÓGICA: LÍNEA MÓVIL PARA FULL TIGO ---
        plan_movil_asociado = None
        if div == "Fijo" and "Full Tigo" in servicio:
            incluye_movil = st.checkbox("📱 ¿Incluye línea móvil?")
            if incluye_movil:
                plan_movil_asociado = "Plan Datos Tigo Empresarial 6.12 (Ilim GB)"
                st.info(f"✨ Plan móvil asociado: **{plan_movil_asociado}**")
        
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
        # ==============================
        # Documentos cliente
        # ==============================

        st.subheader("📎 Documentos del Cliente")

        archivo_subido = st.file_uploader(
            "Adjuntar documentos",
            type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"],
            accept_multiple_files=True
        )

        if archivo_subido:
            st.success(f"📎 {len(archivo_subido)} documento(s) seleccionado(s)")
            
# ==========================================
# PESTAÑA 2: ACTUALIZAR EL ESTADO
# ==========================================
with tab2:
    st.subheader("🔄 Actualizar Seguimiento de Venta")
    
    if os.path.exists("crm_sistema_maestro.csv"):
        df_update = pd.read_csv("crm_sistema_maestro.csv")
        
        # Parches de seguridad y normalización de ID
        if 'ESTADO' not in df_update.columns: df_update['ESTADO'] = "En proceso de firma"
        if 'ID_VENTA' not in df_update.columns: df_update['ID_VENTA'] = range(1, len(df_update) + 1)
        # Forzar ID_VENTA a entero para evitar conflictos de tipo
        df_update['ID_VENTA'] = df_update['ID_VENTA'].astype(float).astype(int)
        
        # Filtro de Asesor
        if not es_admin and 'ASESOR' in df_update.columns:
            df_mis_ventas = df_update[df_update['ASESOR'] == st.session_state.correo_asesor]
        else:
            df_mis_ventas = df_update
            
        if not df_mis_ventas.empty:
            opciones_ventas = df_mis_ventas['ID_VENTA'].astype(str) + " - " + df_mis_ventas['CLIENTE']
            venta_seleccionada = st.selectbox("Selecciona la venta:", opciones_ventas.tolist(), key="select_venta_update")
            
            # --- LÓGICA DE ACTUALIZACIÓN CON DEPURACIÓN ---
            if venta_seleccionada and " - " in venta_seleccionada:
                try:
                    # Corrección: int(float(...)) maneja el "311.0"
                    id_venta = int(float(venta_seleccionada.split(" - ")[0]))
                    
                    # Verificación: ¿Existe este ID en el DF?
                    fila = df_update[df_update['ID_VENTA'] == id_venta]
                    
                    if not fila.empty:
                        estado_actual = fila['ESTADO'].values[0]
                        st.info(f"📌 Estado Actual: **{estado_actual}**")
                        
                        nuevo_estado = st.selectbox(
                            "Cambiar estado a:", 
                            ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"],
                            key="select_nuevo_estado_tab2"
                        )
                        
                        # Botón de guardado
                        if st.button("🔄 Guardar y Notificar", key="btn_guardar_final_tab2"):
                            df_update.loc[df_update['ID_VENTA'] == id_venta, 'ESTADO'] = nuevo_estado
                            df_update.to_csv("crm_sistema_maestro.csv", index=False)
                            enviar_telegram(f"✅ Venta {id_venta} actualizada. Nuevo estado: {nuevo_estado}")
                            st.success("✅ Estado actualizado y notificado.")
                            st.rerun()
                    else:
                        st.error(f"No se encontró la venta con ID: {id_venta}")
                        
                except Exception as e:
                    st.error(f"Error procesando la venta: {e}")
            else:
                st.warning("Selecciona una venta válida.")
        else:
            st.warning("No tienes ventas registradas para actualizar.")
    else:
        st.info("Aún no hay base de datos creada.")
# ==========================================
# PESTAÑA 3: DASHBOARD Y VISUALIZACIÓN DE DATA
# ==========================================
if es_admin:
    with tab3:
        st.subheader("Análisis Centralizado")
        
        archivo = "crm_sistema_maestro.csv"
        
        if os.path.exists(archivo):
            df = pd.read_csv(archivo)
            
        if not df.empty:
            # 1. Métricas Rápidas
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Registros", len(df))
            
            # Ajuste: usamos 'Instalado' que es lo que aparece en tu captura
            instaladas = len(df[df['ESTADO'] == 'Instalado'])
            c2.metric("Ventas Instaladas", instaladas)
            
            fijos = len(df[df['PORTAFOLIO'] == 'FIJO'])
            moviles = len(df[df['PORTAFOLIO'] == 'MOVIL'])
            c3.metric("Fijo vs Móvil", f"{fijos} | {moviles}")
            
            st.divider()
            
            # --- GRÁFICOS APILADOS (UNO DEBAJO DEL OTRO) ---
            
            # Gráfico 1: Ventas por Estado
            st.markdown("#### 📈 Ventas por Estado")
            estado_data = df['ESTADO'].value_counts().reset_index()
            estado_data.columns = ['ESTADO', 'CANTIDAD']
            
            chart1 = alt.Chart(estado_data).mark_bar(color='#00a0e3').encode(
                x=alt.X('ESTADO', sort='-y'),
                y='CANTIDAD'
            )
            st.altair_chart(chart1, use_container_width=True)
            
            st.markdown("---") # Divisor sutil entre gráficos
            
            # Gráfico 2: Portafolio Agrupado (Fijo/Móvil + Activado/Anulado)
            st.markdown("#### 📊 Portafolio: Activadas vs Anuladas por Servicio")
            
            # Normalizamos nombres
            df['ESTADO_NORMALIZADO'] = df['ESTADO'].replace('Instalado', 'Activado')
            df_filtrado = df[df['ESTADO_NORMALIZADO'].isin(['Activado', 'Anulado'])]
            

            # (Asegúrate de que este código esté dentro de tu bloque 'if es_admin: with tab3:')
            st.markdown("#### 📊 Portafolio: Activadas vs Anuladas por Servicio")

            # 1. Primero, creamos df_filtrado normalizando los nombres
            # (Asegúrate de tener esta línea antes de agrupar)
            df['ESTADO_NORMALIZADO'] = df['ESTADO'].replace('Instalado', 'Activado')
            df_filtrado = df[df['ESTADO_NORMALIZADO'].isin(['Activado', 'Anulado'])]

            # 2. Tu código de agrupación (¡Está perfecto!)
            portafolio_grouped = df_filtrado.groupby(['PORTAFOLIO', 'ESTADO_NORMALIZADO']).size().reset_index(name='CANTIDAD')
            
            # 3. Creación del gráfico
            chart2 = alt.Chart(portafolio_grouped).mark_bar().encode(
                x=alt.X('PORTAFOLIO:N', title="Servicio"),
                xOffset='ESTADO_NORMALIZADO:N',
                y='CANTIDAD:Q',
                color=alt.Color('ESTADO_NORMALIZADO:N', 
                                legend=alt.Legend(title="Estado"),
                                scale=alt.Scale(domain=['Activado', 'Anulado'], 
                                                range=['#00a0e3', '#231f20'])),
                tooltip=['PORTAFOLIO', 'ESTADO_NORMALIZADO', 'CANTIDAD']
            ).properties(height=300)
            
            # 4. Mostrar el gráfico en Streamlit
            st.altair_chart(chart2, use_container_width=True)
    
            # --- PANEL DE ANÁLISIS AUTOMÁTICO ---
            st.markdown("### 💡 Análisis Crítico y Mejoras")
            
            # Calculamos tasas rápidas
            total_ventas = len(df_filtrado)
            if total_ventas > 0:
                tasa_anulacion = len(df[df['ESTADO'] == 'Anulado']) / len(df) * 100
                
                # Creamos contenedores de análisis
                c_a1, c_a2 = st.columns(2)
                
                with c_a1:
                    st.markdown("**Observaciones:**")
                    if tasa_anulacion > 20:
                        st.warning(f"⚠️ Tasa de anulación alta ({tasa_anulacion:.1f}%). Se sugiere revisar el proceso de validación de datos.")
                    else:
                        st.success("✅ Tasa de anulación dentro de límites aceptables.")
                
                with c_a2:
                    st.markdown("**Oportunidades de Mejora:**")
                    # Lógica simple para sugerir según qué portafolio es más fuerte
                    if fijos > moviles:
                        st.write("• El portafolio **Fijo** es el motor actual. Enfocar campañas de cross-selling en clientes Móviles.")
                    else:
                        st.write("• El portafolio **Móvil** tiene tracción. Evaluar ofertas de fidelización para clientes Fijos.")
            else:
                st.info("No hay datos suficientes para generar un análisis automático.")
            
# ==========================================
# GESTIÓN DE ANÁLISIS CENTRALIZADO (Solo Admin)
# ==========================================
if es_admin:
    with tab3:
        st.subheader("📊 Base de Datos Actual")
        
        # Fíjate cómo este 'if' y su 'else' están en la misma línea vertical
        if os.path.exists("crm_sistema_maestro.csv"):
            df_verificar = pd.read_csv("crm_sistema_maestro.csv")
            
            # 1. Mostramos la tabla interactiva una sola vez
            st.markdown("### 📋 Base de Datos Somostelser")
            st.dataframe(df_verificar, use_container_width=True)
            
            # 2. Botón para descargar la base de datos y revisarla en Excel
            csv = df_verificar.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Base de Datos (CSV)", data=csv, file_name="crm_respaldo.csv")
            
        else: # <--- Este else está perfectamente alineado con el if os.path.exists
            st.warning("El archivo 'crm_sistema_maestro.csv' aún no ha sido creado.")
