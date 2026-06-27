import streamlit as st
import pandas as pd
import os
import random
import requests
import altair as alt
from datetime import date, timedelta

# ==========================================
# CONFIGURACIÓN DE PÁGINA (debe ir primero)
# ==========================================
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

# ==========================================
# TELEGRAM
# ==========================================
def enviar_telegram(mensaje):
    TOKEN = "8942591199:AAFi8vkAvNyL4LLkUPO9TXKhC2bjukEDmcg"
    CHAT_ID = "1415966548"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        respuesta = requests.get(url, params=params)
        if respuesta.status_code == 200:
            st.success("✅ ¡Mensaje enviado por Telegram!")
        else:
            st.error(f"❌ Error Telegram {respuesta.status_code}: {respuesta.text}")
    except Exception as e:
        st.error(f"❌ Error Telegram: {e}")

# ==========================================
# PORTAFOLIO
# ==========================================
PLANES_MOVIL = {
    "Pospago Negocios 4.9 Plus+ (60 GB)": 44900.0,
    "Pospago Negocios 5.4 Plus+ (100 GB)": 53900.0,
    "Pospago 5.3 Empresarial (Ilim GB)": 113900.0,
    "Plan Datos Tigo Empresarial 6.9 (30 GB)": 38300.0,
    "Plan Datos Tigo Empresarial 6.10 (60 GB)": 47900.0,
    "Plan Datos Tigo Empresarial 6.11 (110 GB)": 57900.0,
    "Plan Datos Tigo Empresarial 6.12 (Ilim GB)": 113900.0,
    "Plan Datos Tigo Empresarial 6.8 FULL TIGO (Ilim GB)": 54900.0,
}

PLANES_FIJO = {
    "Internet Business 300 Mbps (HFC/FTTx)": 88880.0,
    "Internet Business 500 Mbps (HFC/FTTx)": 115000.0,
    "Internet Business 700 Mbps (HFC/FTTx)": 180001.0,
    "Internet Full Tigo Business 500 Mbps": 144000.0,
    "Internet Full Tigo Business 700 Mbps": 174000.0,
    "Internet Full Tigo Business 1000 Mbps": 274000.0,
}

UBICACIONES_COL = {
    "Amazonas": ["Leticia", "Puerto Nariño"],
    "Antioquia": ["Medellín", "Envigado", "Itagüí", "Bello", "Rionegro", "Sabaneta", "La Estrella", "Caldas", "Retiro"],
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
    "Vichada": ["Puerto Carreño"],
}

# ==========================================
# SISTEMA DE LOGIN
# ==========================================
if "correo_asesor" not in st.session_state:
    st.session_state.correo_asesor = None

if st.session_state.correo_asesor is None:
    st.title("🔐 Acceso al CRM Somos Telser")
    st.write("Por favor, selecciona tu perfil e ingresa la contraseña:")

    usuario_seleccionado = st.selectbox(
        "Usuario:",
        [
            "",
            "ADMIN@SOMOSTELSER.COM",
            "ASESOR1@SOMOSTELSER.COM",
            "ASESOR2@SOMOSTELSER.COM",
            "ASESOR3@SOMOSTELSER.COM",
            "ASESOR4@SOMOSTELSER.COM",
        ],
        key="select_usuario",
    )
    password = st.text_input("Contraseña:", type="password", key="pass_input")

    if st.button("Ingresar al Portal", key="btn_login"):
        if usuario_seleccionado != "" and password == "Telser2026":
            st.session_state.correo_asesor = usuario_seleccionado
            st.rerun()
        elif usuario_seleccionado == "":
            st.warning("Por favor, selecciona un usuario.")
        else:
            st.error("Contraseña incorrecta.")
    st.stop()

# ==========================================
# ROL
# ==========================================
es_admin = st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM"

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_column_width=True)

    rol = "👑 Admin" if es_admin else "👤 Asesor"
    st.markdown(f"**{rol}:** `{st.session_state.correo_asesor}`")

    # --- TAREAS PENDIENTES ---
    st.markdown("---")
    st.subheader("🔔 Tareas Pendientes")
    if os.path.exists("crm_sistema_maestro.csv"):
        df_tasks = pd.read_csv("crm_sistema_maestro.csv")
        if "FECHA_SEGUIMIENTO" in df_tasks.columns:
            df_tasks["FECHA_SEGUIMIENTO"] = pd.to_datetime(
                df_tasks["FECHA_SEGUIMIENTO"], errors="coerce"
            )
            hoy = pd.Timestamp(date.today())
            pendientes = df_tasks[
                (df_tasks["FECHA_SEGUIMIENTO"] <= hoy)
                & (df_tasks["ESTADO"].isin(["Cotizado", "En proceso de firma"]))
            ]
            if not es_admin:
                pendientes = pendientes[
                    pendientes["ASESOR"] == st.session_state.correo_asesor
                ]
            if not pendientes.empty:
                for _, row in pendientes.iterrows():
                    tipo_seg = row.get("TIPO_SEGUIMIENTO", "Seguimiento")
                    st.warning(f"📞 {row['CLIENTE']} | {tipo_seg}")
            else:
                st.success("¡Todo al día!")

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.correo_asesor = None
        st.rerun()

    # --- ASISTENTE DE OFERTAS ---
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

    # --- MINI DASHBOARD EN SIDEBAR ---
    st.markdown("---")
    st.subheader("📊 Dashboard")
    if os.path.exists("crm_sistema_maestro.csv"):
        try:
            df_sb = pd.read_csv("crm_sistema_maestro.csv")
            if not es_admin and "ASESOR" in df_sb.columns:
                df_sb = df_sb[df_sb["ASESOR"] == st.session_state.correo_asesor]
            if "DIVISION" in df_sb.columns and not df_sb.empty:
                st.metric("💰 Ingresos Totales", f"${df_sb['VALOR_TOTAL'].sum():,.0f} COP")
                st.bar_chart(df_sb["DIVISION"].value_counts())
                if es_admin:
                    st.download_button(
                        label="📥 Exportar CRM a Excel",
                        data=df_sb.to_csv(index=False).encode("utf-8"),
                        file_name="CRM_Ventas_SomosTelser.csv",
                        mime="text/csv",
                    )
            else:
                st.caption("Aún no hay ventas registradas.")
        except Exception:
            st.caption("Cargando...")

# ==========================================
# TÍTULO PRINCIPAL
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
st.subheader("Gestión Inteligente de Contratos B2B")

# ==========================================
# PESTAÑAS
# ==========================================
nombres_pestanas = ["Registrar Venta", "Actualizar Estado de Venta"]
if es_admin:
    nombres_pestanas.append("Base de Datos")

tabs = st.tabs(nombres_pestanas)
tab1 = tabs[0]
tab2 = tabs[1]
tab3 = tabs[2] if es_admin else None

# ==========================================================
# PESTAÑA 1: REGISTRAR VENTA
# ==========================================================
with tab1:
    div = st.radio(
        "Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True
    )

    c1, c2 = st.columns(2)

    # ---- COLUMNA IZQUIERDA ----
    with c1:
        st.subheader("🏢 Datos del Cliente")
        t_doc = st.selectbox("Tipo Doc:", ["NIT", "CV", "CE", "PPT"], key="t_doc")
        n_doc = st.text_input("Número de Documento:", key="n_doc")
        nombre = st.text_input("Razón Social o Nombre:", key="nombre")
        dir_cli = st.text_input("Dirección:", key="dir_cli")
        barrio = st.text_input("Barrio:", key="barrio")

        depto = st.selectbox(
            "Departamento:",
            options=sorted(list(UBICACIONES_COL.keys())),
            index=None,
            placeholder="Escribe para buscar departamento...",
            key="depto",
        )
        if depto:
            muni = st.selectbox(
                "Municipio:",
                options=sorted(UBICACIONES_COL[depto]),
                index=None,
                placeholder="Escribe para buscar municipio...",
                key="muni",
            )
        else:
            muni = st.selectbox(
                "Municipio:",
                options=[],
                disabled=True,
                placeholder="Selecciona primero un depto",
                key="muni_disabled",
            )

        email_cli = st.text_input("Email contacto:", key="email_cli")
        movil_cli = st.text_input("Contacto autorizado:", key="movil_cli")
        tel_contacto = st.text_input("Móvil Contacto autorizado:", key="tel_contacto")

        st.subheader("⚙️ Gestión Técnica")

        # Inicializar lista de líneas en session_state
        if "lista_lineas" not in st.session_state:
            st.session_state.lista_lineas = []

        with st.popover("📱 Configurar Líneas Móviles (Click aquí)"):
            tipo_linea = st.radio(
                "Tipo de gestión:",
                ["Portabilidad", "Línea Nueva", "Línea Existente"],
                key="tipo_linea_pop",
            )
            op_linea = "N/A"
            if tipo_linea == "Portabilidad":
                op_linea = st.selectbox(
                    "Operador Origen:",
                    ["Claro", "Movistar", "Móvil Éxito", "Wom"],
                    key="op_linea_pop",
                )
            cant_linea = st.number_input(
                "Cantidad de esta línea:", min_value=1, value=1, key="cant_linea_pop"
            )
            num_linea = st.text_input("Número de línea:", key="num_linea_pop")

            if st.button("➕ Agregar esta línea a la venta", key="btn_add_linea"):
                nueva_linea = {
                    "cantidad": cant_linea,
                    "tipo": tipo_linea,
                    "operador": op_linea,
                    "numero": num_linea,
                }
                st.session_state.lista_lineas.append(nueva_linea)
                st.success(f"Línea {num_linea} agregada.")

            if st.session_state.lista_lineas:
                st.markdown("**Líneas acumuladas:**")
                for i, ln in enumerate(st.session_state.lista_lineas, 1):
                    st.write(
                        f"{i}. {ln['tipo']} | {ln['operador']} | {ln['numero']} | x{ln['cantidad']}"
                    )
                if st.button("🗑️ Limpiar líneas", key="btn_clear_lineas"):
                    st.session_state.lista_lineas = []
                    st.rerun()
            else:
                st.info("La gestión móvil aplica también para Full Tigo.")

    # ---- COLUMNA DERECHA ----
    with c2:
        st.subheader("👤 Representante Legal")
        nom_rep = st.text_input("Nombre Rep. Legal:", key="nom_rep")
        cc_rep = st.text_input("Cédula Rep. Legal:", key="cc_rep")
        mail_rep = st.text_input("Correo Rep. Legal:", key="mail_rep")
        tel_rep = st.text_input("Móvil Rep. Legal:", key="tel_rep")

        st.subheader("📊 Estado y Plan")
        estado = st.selectbox(
            "Estado:",
            ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"],
            key="estado_venta",
        )
        bitacora = st.text_area("📝 Notas / Bitácora:", key="bitacora")

        # Fecha de seguimiento (guarda la tarea en sidebar)
        fecha_seg = st.date_input(
            "📅 Fecha de seguimiento:",
            value=date.today() + timedelta(days=3),
            key="fecha_seg",
        )
        tipo_seg = st.selectbox(
            "Tipo de seguimiento:",
            ["Llamada", "Visita", "Correo", "WhatsApp"],
            key="tipo_seg",
        )

        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()), key="servicio")

        titulo_cantidad = "Líneas:" if div == "Móvil" else "Cantidad:"
        lineas = st.number_input(titulo_cantidad, min_value=1, value=1, key="lineas")

        # Línea móvil asociada para Full Tigo
        plan_movil_asociado = None
        if div == "Fijo" and "Full Tigo" in servicio:
            incluye_movil = st.checkbox("📱 ¿Incluye línea móvil?", key="incluye_movil")
            if incluye_movil:
                plan_movil_asociado = "Plan Datos Tigo Empresarial 6.12 (Ilim GB)"
                st.info(f"✨ Plan móvil asociado: **{plan_movil_asociado}**")

        # CÁLCULO FINANCIERO
        dcto = (
            30 if lineas >= 9
            else 25 if lineas >= 6
            else 20 if lineas >= 3
            else 10 if lineas == 2
            else 0
        )
        valor = (tarifas[servicio] * lineas) * (1 - dcto / 100)

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
            "🥇 ¡No hay límites cuando hay buena planeación y actitud!",
        ]

        if valor > 0:
            st.markdown(
                f"""
                <div style="background-color:#e1f5fe;padding:12px;border-radius:10px;
                border-left:5px solid #0288d1;margin-bottom:15px;">
                    <p style="margin:0;font-size:1.1em;color:#01579b;">
                        💰 <b>Total Estimado:</b> ${valor:,.0f} COP
                        {"&nbsp;&nbsp;🏷️ Descuento: " + str(dcto) + "%" if dcto > 0 else ""}
                    </p>
                    <p style="margin:5px 0 0 0;font-size:0.85em;"><i>{random.choice(frases)}</i></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.subheader("📎 Documentos del Cliente")
        archivo_subido = st.file_uploader(
            "Adjuntar documentos",
            type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"],
            accept_multiple_files=True,
            key="file_uploader",
        )
        if archivo_subido:
            st.success(f"📎 {len(archivo_subido)} documento(s) seleccionado(s)")

    # ---- BOTÓN GUARDAR (ancho completo, fuera de columnas) ----
    guardar = st.button(
        "💾 Guardar Venta", key="btn_guardar_venta_tab1", use_container_width=True
    )

    if guardar:
        if n_doc and nombre:
            # Guardar documentos adjuntos
            carpeta_documentos = "documentos_clientes"
            os.makedirs(carpeta_documentos, exist_ok=True)
            archivos_guardados = []
            if archivo_subido:
                for archivo_doc in archivo_subido:
                    nombre_archivo = f"{n_doc}_{archivo_doc.name}"
                    ruta_archivo = os.path.join(carpeta_documentos, nombre_archivo)
                    with open(ruta_archivo, "wb") as f:
                        f.write(archivo_doc.getbuffer())
                    archivos_guardados.append(nombre_archivo)

            # Construir resumen de líneas móviles
            resumen_lineas = ""
            if st.session_state.lista_lineas:
                resumen_lineas = " | ".join(
                    [
                        f"{ln['tipo']}/{ln['operador']}/{ln['numero']}(x{ln['cantidad']})"
                        for ln in st.session_state.lista_lineas
                    ]
                )

            archivo_csv = "crm_sistema_maestro.csv"
            df_ex = (
                pd.read_csv(archivo_csv)
                if os.path.exists(archivo_csv)
                else pd.DataFrame()
            )

            nueva_fila = pd.DataFrame(
                [
                    {
                        "ID_VENTA": len(df_ex) + 1,
                        "ASESOR": st.session_state.correo_asesor,
                        "ESTADO": estado,
                        "DIVISION": div,
                        "PORTAFOLIO": "MOVIL" if div == "Móvil" else "FIJO",
                        "NIT": n_doc,
                        "TIPO_DOC": t_doc,
                        "CLIENTE": nombre,
                        "DIRECCION": dir_cli,
                        "BARRIO": barrio,
                        "DEPARTAMENTO": depto if depto else "",
                        "MUNICIPIO": muni if muni else "",
                        "EMAIL_CLIENTE": email_cli,
                        "CONTACTO": movil_cli,
                        "TEL_CONTACTO": tel_contacto,
                        "REP_LEGAL": nom_rep,
                        "CC_REP": cc_rep,
                        "CORREO_REP": mail_rep,
                        "TEL_REP": tel_rep,
                        "SERVICIO": servicio,
                        "CANTIDAD_LINEAS": lineas,
                        "LINEAS_DETALLE": resumen_lineas,
                        "PLAN_MOVIL_ASOCIADO": plan_movil_asociado or "",
                        "DESCUENTO": dcto,
                        "VALOR_TOTAL": valor,
                        "BITACORA": bitacora,
                        "FECHA_SEGUIMIENTO": str(fecha_seg),
                        "TIPO_SEGUIMIENTO": tipo_seg,
                        "DOCUMENTOS": ";".join(archivos_guardados),
                        "ESTADO_FINANCIERO": "APROBADO" if valor >= 35000 else "REVISION",
                        "FECHA_REGISTRO": str(date.today()),
                    }
                ]
            )

            pd.concat([df_ex, nueva_fila], ignore_index=True).to_csv(
                archivo_csv, index=False
            )

            # Notificación Telegram
            enviar_telegram(
                f"🆕 Nueva venta registrada\n"
                f"Asesor: {st.session_state.correo_asesor}\n"
                f"Cliente: {nombre} | {n_doc}\n"
                f"Servicio: {servicio}\n"
                f"Valor: ${valor:,.0f} COP\n"
                f"Estado: {estado}"
            )

            # Limpiar líneas acumuladas
            st.session_state.lista_lineas = []
            st.success("✅ Venta registrada correctamente.")
            st.rerun()
        else:
            st.error("⚠️ Faltan datos obligatorios: Número de documento y Nombre/Razón Social.")

# ==========================================================
# PESTAÑA 2: ACTUALIZAR ESTADO
# ==========================================================
with tab2:
    st.subheader("🔄 Actualizar Seguimiento de Venta")

    if not os.path.exists("crm_sistema_maestro.csv"):
        st.info("Aún no hay base de datos creada.")
    else:
        df_update = pd.read_csv("crm_sistema_maestro.csv")

        # Red de seguridad para columnas esenciales
        for col in ["ESTADO", "ID_VENTA", "CLIENTE", "ASESOR"]:
            if col not in df_update.columns:
                df_update[col] = "Sin dato"

        df_update["ID_VENTA"] = (
            pd.to_numeric(df_update["ID_VENTA"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        # Filtro por rol
        if es_admin:
            df_mis_ventas = df_update.copy()
        else:
            df_mis_ventas = df_update[
                df_update["ASESOR"] == st.session_state.correo_asesor
            ].copy()

        if df_mis_ventas.empty:
            st.warning("No tienes ventas registradas para actualizar.")
        else:
            df_mis_ventas["ID_FMT"] = df_mis_ventas["ID_VENTA"].astype(str).str.zfill(4)
            df_mis_ventas["OPCION"] = (
                df_mis_ventas["ID_FMT"] + " - " + df_mis_ventas["CLIENTE"].astype(str)
            )
            opciones = df_mis_ventas["OPCION"].tolist()

            seleccion = st.selectbox(
                "Selecciona la venta a actualizar:", opciones, key="sel_venta_tab2"
            )

            if seleccion:
                id_v = int(seleccion[:4])
                venta = df_update[df_update["ID_VENTA"] == id_v]

                if not venta.empty:
                    fila = venta.iloc[0]
                    estado_actual = fila["ESTADO"]

                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.info(f"📌 Estado actual: **{estado_actual}**")
                        st.write(f"**Cliente:** {fila.get('CLIENTE', 'N/A')}")
                        st.write(f"**Servicio:** {fila.get('SERVICIO', 'N/A')}")
                    with col_info2:
                        st.write(f"**Valor:** ${float(fila.get('VALOR_TOTAL', 0)):,.0f} COP")
                        st.write(f"**Asesor:** {fila.get('ASESOR', 'N/A')}")
                        st.write(f"**División:** {fila.get('DIVISION', 'N/A')}")

                    nuevo_estado = st.selectbox(
                        "Cambiar estado a:",
                        ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"],
                        key="sel_nuevo_estado_tab2",
                    )

                    nueva_bitacora = st.text_area(
                        "📝 Agregar nota a la bitácora (opcional):", key="nueva_bitacora_tab2"
                    )

                    if st.button(
                        "🔄 Guardar y Notificar", key="btn_update_tab2", type="primary"
                    ):
                        df_update.loc[df_update["ID_VENTA"] == id_v, "ESTADO"] = nuevo_estado
                        if nueva_bitacora.strip():
                            bitacora_existente = str(fila.get("BITACORA", ""))
                            nueva_entrada = f"\n[{date.today()}] {nueva_bitacora.strip()}"
                            df_update.loc[df_update["ID_VENTA"] == id_v, "BITACORA"] = (
                                bitacora_existente + nueva_entrada
                            )
                        df_update.to_csv("crm_sistema_maestro.csv", index=False)
                        enviar_telegram(
                            f"🔄 Venta #{str(id_v).zfill(4)} actualizada\n"
                            f"Cliente: {fila.get('CLIENTE', 'N/A')}\n"
                            f"Nuevo estado: {nuevo_estado}\n"
                            f"Asesor: {st.session_state.correo_asesor}"
                        )
                        st.success("✅ Guardado y notificado correctamente.")
                        st.rerun()

# ==========================================================
# PESTAÑA 3: DASHBOARD Y BASE DE DATOS (solo Admin)
# ==========================================================
if es_admin and tab3 is not None:
    with tab3:
        st.subheader("📊 Dashboard: Gestión de Ventas Somostelser")

        archivo = "crm_sistema_maestro.csv"

        if os.path.exists(archivo):
            df = pd.read_csv(archivo)

            if not df.empty:
                # --- Métricas rápidas ---
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Registros", len(df))

                activadas = len(df[df["ESTADO"].isin(["Activado", "Instalado"])])
                c2.metric("Ventas Activadas", activadas)

                fijos = len(df[df["PORTAFOLIO"] == "FIJO"]) if "PORTAFOLIO" in df.columns else len(df[df["DIVISION"] == "Fijo"])
                moviles = len(df[df["PORTAFOLIO"] == "MOVIL"]) if "PORTAFOLIO" in df.columns else len(df[df["DIVISION"] == "Móvil"])
                c3.metric("Fijo vs Móvil", f"{fijos} | {moviles}")

                st.divider()

                # --- Gráfico 1: Ventas por Estado ---
                st.markdown("#### 📈 Ventas por Estado")
                estado_data = df["ESTADO"].value_counts().reset_index()
                estado_data.columns = ["ESTADO", "CANTIDAD"]
                chart1 = alt.Chart(estado_data).mark_bar(color="#00a0e3").encode(
                    x=alt.X("ESTADO:N", sort="-y", title="Estado"),
                    y=alt.Y("CANTIDAD:Q", title="Cantidad"),
                    tooltip=["ESTADO", "CANTIDAD"],
                )
                st.altair_chart(chart1, use_container_width=True)

                st.markdown("---")

                # --- Gráfico 2: Portafolio Activado vs Anulado ---
                st.markdown("#### 📊 Portafolio: Activadas vs Anuladas por Servicio")
                col_div = "PORTAFOLIO" if "PORTAFOLIO" in df.columns else "DIVISION"
                df["ESTADO_NORM"] = df["ESTADO"].replace("Instalado", "Activado")
                df_filtrado = df[df["ESTADO_NORM"].isin(["Activado", "Anulado"])]

                if not df_filtrado.empty:
                    portafolio_grouped = (
                        df_filtrado.groupby([col_div, "ESTADO_NORM"])
                        .size()
                        .reset_index(name="CANTIDAD")
                    )
                    chart2 = (
                        alt.Chart(portafolio_grouped)
                        .mark_bar()
                        .encode(
                            x=alt.X(f"{col_div}:N", title="Servicio"),
                            xOffset="ESTADO_NORM:N",
                            y=alt.Y("CANTIDAD:Q"),
                            color=alt.Color(
                                "ESTADO_NORM:N",
                                legend=alt.Legend(title="Estado"),
                                scale=alt.Scale(
                                    domain=["Activado", "Anulado"],
                                    range=["#00a0e3", "#231f20"],
                                ),
                            ),
                            tooltip=[col_div, "ESTADO_NORM", "CANTIDAD"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart2, use_container_width=True)

                # --- Análisis automático ---
                st.markdown("### 💡 Análisis Crítico y Mejoras")
                total = len(df)
                if total > 0:
                    tasa_anulacion = len(df[df["ESTADO"] == "Anulado"]) / total * 100
                    c_a1, c_a2 = st.columns(2)
                    with c_a1:
                        st.markdown("**Observaciones:**")
                        if tasa_anulacion > 20:
                            st.warning(
                                f"⚠️ Tasa de anulación alta ({tasa_anulacion:.1f}%). "
                                "Se sugiere revisar el proceso de validación de datos."
                            )
                        else:
                            st.success("✅ Tasa de anulación dentro de límites aceptables.")
                    with c_a2:
                        st.markdown("**Oportunidades de Mejora:**")
                        if fijos > moviles:
                            st.write(
                                "• El portafolio **Fijo** es el motor actual. "
                                "Enfocar campañas de cross-selling en clientes Móviles."
                            )
                        else:
                            st.write(
                                "• El portafolio **Móvil** tiene tracción. "
                                "Evaluar ofertas de fidelización para clientes Fijos."
                            )

                st.divider()

                # --- Tabla completa y descarga ---
                st.markdown("#### 🗃️ Base de Datos Completa")
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    label="📥 Descargar Base de Datos",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="CRM_Ventas_SomosTelser_respaldo.csv",
                    mime="text/csv",
                )
            else:
                st.info("La base de datos está vacía.")
        else:
            st.info("Aún no hay base de datos creada.")
