import streamlit as st
import pandas as pd
import os
import random
import requests
import altair as alt
from datetime import date, timedelta

# ==========================================
# CONFIGURACIÓN DE PÁGINA (siempre primero)
# ==========================================
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

# ==========================================
# FUNCIÓN TELEGRAM
# ==========================================
def enviar_telegram(mensaje):
    TOKEN  = "8942591199:AAFi8vkAvNyL4LLkUPO9TXKhC2bjukEDmcg"
    CHAT_ID = "1415966548"
    url    = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.get(url, params={"chat_id": CHAT_ID, "text": mensaje})
        if r.status_code == 200:
            st.success("✅ Notificación Telegram enviada.")
        else:
            st.error(f"❌ Telegram error {r.status_code}: {r.text}")
    except Exception as e:
        st.error(f"❌ Error Telegram: {e}")

# ==========================================
# PORTAFOLIO
# ==========================================
PLANES_MOVIL = {
    "Pospago Negocios 4.9 Plus+ (60 GB)":              44900.0,
    "Pospago Negocios 5.4 Plus+ (100 GB)":             53900.0,
    "Pospago 5.3 Empresarial (Ilim GB)":              113900.0,
    "Plan Datos Tigo Empresarial 6.9 (30 GB)":         38300.0,
    "Plan Datos Tigo Empresarial 6.10 (60 GB)":        47900.0,
    "Plan Datos Tigo Empresarial 6.11 (110 GB)":       57900.0,
    "Plan Datos Tigo Empresarial 6.12 (Ilim GB)":     113900.0,
    "Plan Datos Tigo Empresarial 6.8 FULL TIGO (Ilim GB)": 54900.0,
}

PLANES_FIJO = {
    "Internet Business 300 Mbps (HFC/FTTx)":   88880.0,
    "Internet Business 500 Mbps (HFC/FTTx)":  115000.0,
    "Internet Business 700 Mbps (HFC/FTTx)":  180001.0,
    "Internet Full Tigo Business 500 Mbps":    144000.0,
    "Internet Full Tigo Business 700 Mbps":    174000.0,
    "Internet Full Tigo Business 1000 Mbps":   274000.0,
}

UBICACIONES_COL = {
    "Amazonas":               ["Leticia","Puerto Nariño"],
    "Antioquia":              ["Medellín","Envigado","Itagüí","Bello","Rionegro","Sabaneta","La Estrella","Caldas","Retiro"],
    "Arauca":                 ["Arauca","Tame","Saravena"],
    "Atlántico":              ["Barranquilla","Soledad","Puerto Colombia","Malambo"],
    "Bolívar":                ["Cartagena","Magangué","Turbaco"],
    "Boyacá":                 ["Tunja","Duitama","Sogamoso","Chiquinquirá"],
    "Caldas":                 ["Manizales","La Dorada","Chinchiná"],
    "Caquetá":                ["Florencia","San Vicente del Caguán"],
    "Casanare":               ["Yopal","Aguazul"],
    "Cauca":                  ["Popayán","Santander de Quilichao","Puerto Tejada"],
    "Cesar":                  ["Valledupar","Aguachica","Codazzi"],
    "Chocó":                  ["Quibdó","Istmina"],
    "Córdoba":                ["Montería","Lorica","Cereté"],
    "Cundinamarca":           ["Bogotá D.C.","Soacha","Chía","Cajicá","Zipaquirá","Fusagasugá","Facatativá"],
    "Guainía":                ["Inírida"],
    "Guaviare":               ["San José del Guaviare"],
    "Huila":                  ["Neiva","Pitalito","Garzón"],
    "La Guajira":             ["Riohacha","Maicao","Uribia"],
    "Magdalena":              ["Santa Marta","Ciénaga"],
    "Meta":                   ["Villavicencio","Acacías","Granada"],
    "Nariño":                 ["Pasto","Ipiales","Tumaco"],
    "Norte de Santander":     ["Cúcuta","Ocaña","Villa del Rosario"],
    "Putumayo":               ["Mocoa","Puerto Asís"],
    "Quindío":                ["Armenia","Calarcá"],
    "Risaralda":              ["Pereira","Dosquebradas","Santa Rosa de Cabal"],
    "San Andrés y Providencia":["San Andrés"],
    "Santander":              ["Bucaramanga","Floridablanca","Girón","Piedecuesta","Barrancabermeja"],
    "Sucre":                  ["Sincelejo","Corozal"],
    "Tolima":                 ["Ibagué","Espinal","Melgar","Honda"],
    "Valle del Cauca":        ["Cali","Palmira","Buga","Buenaventura","Cartago","Jamundí","Tuluá"],
    "Vaupés":                 ["Mitú"],
    "Vichada":                ["Puerto Carreño"],
}

FRASES_MOTIVACION = [
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

CSV_PATH = "crm_sistema_maestro.csv"

# ==========================================
# SISTEMA DE LOGIN
# ==========================================
if "correo_asesor" not in st.session_state:
    st.session_state.correo_asesor = None

if st.session_state.correo_asesor is None:
    st.title("🔐 Acceso al CRM Somos Telser")
    st.write("Por favor, selecciona tu perfil e ingresa la contraseña:")

    usuario_sel = st.selectbox("Usuario:", [
        "", "ADMIN@SOMOSTELSER.COM",
        "ASESOR1@SOMOSTELSER.COM", "ASESOR2@SOMOSTELSER.COM",
        "ASESOR3@SOMOSTELSER.COM", "ASESOR4@SOMOSTELSER.COM",
    ], key="select_usuario")

    password = st.text_input("Contraseña:", type="password", key="pass_input")

    if st.button("Ingresar al Portal", key="btn_login"):
        if usuario_sel == "":
            st.warning("Por favor, selecciona un usuario.")
        elif password == "Telser2026":
            st.session_state.correo_asesor = usuario_sel
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop()

# ==========================================
# ROL (una sola definición)
# ==========================================
es_admin = st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM"

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_column_width=True)

    rol_label = "👑 Admin" if es_admin else "👤 Asesor"
    st.markdown(f"**{rol_label}:** `{st.session_state.correo_asesor}`")

    # Tareas pendientes
    st.markdown("---")
    st.subheader("🔔 Tareas Pendientes")
    if os.path.exists(CSV_PATH):
        try:
            df_tasks = pd.read_csv(CSV_PATH)
            if "FECHA_SEGUIMIENTO" in df_tasks.columns:
                df_tasks["FECHA_SEGUIMIENTO"] = pd.to_datetime(
                    df_tasks["FECHA_SEGUIMIENTO"], errors="coerce"
                )
                hoy_ts = pd.Timestamp(date.today())
                pendientes = df_tasks[
                    (df_tasks["FECHA_SEGUIMIENTO"] <= hoy_ts) &
                    (df_tasks["ESTADO"].isin(["Cotizado", "En proceso de firma"]))
                ]
                if not es_admin:
                    pendientes = pendientes[
                        pendientes["ASESOR"] == st.session_state.correo_asesor
                    ]
                if not pendientes.empty:
                    for _, row in pendientes.iterrows():
                        st.warning(f"📞 {row['CLIENTE']} | {row.get('TIPO_SEGUIMIENTO','Seguimiento')}")
                else:
                    st.success("¡Todo al día!")
        except Exception:
            st.caption("No se pudo leer el CSV.")

    if st.button("🚪 Cerrar Sesión", key="btn_logout"):
        st.session_state.correo_asesor = None
        st.rerun()

    # Asistente de ofertas
    st.markdown("---")
    st.subheader("🤖 Asistente de Ofertas")
    consulta = st.text_input("Buscar precio:", placeholder="Ej: 500Mbps, 60GB", key="consulta_oferta")
    if consulta:
        portafolio_total = {**PLANES_MOVIL, **PLANES_FIJO}
        resultados = {k: v for k, v in portafolio_total.items() if consulta.lower() in k.lower()}
        if resultados:
            sel_oferta = st.selectbox("Resultados:", list(resultados.keys()), key="sel_oferta")
            st.metric("Precio Sugerido", f"${resultados[sel_oferta]:,.0f} COP")
        else:
            st.warning("Sin resultados.")

    # Mini-dashboard en sidebar
    st.markdown("---")
    st.subheader("📊 Resumen")
    if os.path.exists(CSV_PATH):
        try:
            df_sb = pd.read_csv(CSV_PATH)
            if not es_admin and "ASESOR" in df_sb.columns:
                df_sb = df_sb[df_sb["ASESOR"] == st.session_state.correo_asesor]
            if "VALOR_TOTAL" in df_sb.columns and not df_sb.empty:
                st.metric("💰 Ingresos Totales", f"${df_sb['VALOR_TOTAL'].sum():,.0f} COP")
            if "DIVISION" in df_sb.columns and not df_sb.empty:
                st.bar_chart(df_sb["DIVISION"].value_counts())
            if es_admin and not df_sb.empty:
                st.download_button(
                    "📥 Exportar CRM",
                    data=df_sb.to_csv(index=False).encode("utf-8"),
                    file_name="CRM_Ventas_SomosTelser.csv",
                    mime="text/csv",
                    key="dl_sidebar",
                )
        except Exception:
            st.caption("Cargando...")

# ==========================================
# TÍTULO PRINCIPAL
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
st.subheader("Gestión Inteligente de Contratos B2B")

# ==========================================
# PESTAÑAS — se crean UNA SOLA VEZ
# ==========================================
nombres_tabs = ["📋 Registrar Venta", "🔄 Actualizar Estado"]
if es_admin:
    nombres_tabs.append("📊 Base de Datos")

tabs = st.tabs(nombres_tabs)
tab1 = tabs[0]
tab2 = tabs[1]
tab3 = tabs[2] if es_admin else None

# ==========================================================
# ██████████  PESTAÑA 1: REGISTRAR VENTA  ██████████
# ==========================================================
with tab1:

    if "lista_lineas" not in st.session_state:
        st.session_state.lista_lineas = []

    div = st.radio(
        "Seleccione División:", ["Móvil", "Fijo"],
        key="div_radio", horizontal=True
    )

    col_izq, col_der = st.columns(2)

    # ── COLUMNA IZQUIERDA ──────────────────────────────────
    with col_izq:
        st.subheader("🏢 Datos del Cliente")
        t_doc    = st.selectbox("Tipo Doc:", ["NIT", "CV", "CE", "PPT"], key="t_doc")
        n_doc    = st.text_input("Número de Documento:", key="n_doc")
        nombre   = st.text_input("Razón Social o Nombre:", key="nombre")
        dir_cli  = st.text_input("Dirección:", key="dir_cli")
        barrio   = st.text_input("Barrio:", key="barrio")

        depto = st.selectbox(
            "Departamento:",
            options=sorted(UBICACIONES_COL.keys()),
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
                key="muni_activo",
            )
        else:
            muni = st.selectbox(
                "Municipio:", options=[], disabled=True,
                placeholder="Selecciona primero un departamento",
                key="muni_disabled",
            )

        email_cli    = st.text_input("Email contacto:", key="email_cli")
        contacto_cli = st.text_input("Nombre contacto autorizado:", key="contacto_cli")
        tel_contacto = st.text_input("Móvil contacto autorizado:", key="tel_contacto")

        st.subheader("⚙️ Gestión Técnica")
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
                "Cantidad:", min_value=1, value=1, key="cant_linea_pop"
            )
            num_linea = st.text_input("Número de línea:", key="num_linea_pop")

            if st.button("➕ Agregar línea", key="btn_add_linea"):
                st.session_state.lista_lineas.append({
                    "cantidad": cant_linea,
                    "tipo":     tipo_linea,
                    "operador": op_linea,
                    "numero":   num_linea,
                })
                st.success(f"✅ Línea {num_linea} agregada.")

            if st.session_state.lista_lineas:
                st.markdown("**Líneas acumuladas:**")
                for i, ln in enumerate(st.session_state.lista_lineas, 1):
                    st.write(f"{i}. {ln['tipo']} | {ln['operador']} | {ln['numero']} | x{ln['cantidad']}")
                if st.button("🗑️ Limpiar todas las líneas", key="btn_clear_lineas"):
                    st.session_state.lista_lineas = []
                    st.rerun()
            else:
                st.info("La gestión móvil aplica también para Full Tigo.")

    # ── COLUMNA DERECHA ────────────────────────────────────
    with col_der:
        st.subheader("👤 Representante Legal")
        nom_rep  = st.text_input("Nombre Rep. Legal:", key="nom_rep")
        cc_rep   = st.text_input("Cédula Rep. Legal:", key="cc_rep")
        mail_rep = st.text_input("Correo Rep. Legal:", key="mail_rep")
        tel_rep  = st.text_input("Móvil Rep. Legal:", key="tel_rep")

        st.subheader("📊 Estado y Plan")
        estado = st.selectbox(
            "Estado inicial:",
            ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"],
            key="estado_venta",
        )
        bitacora = st.text_area("📝 Notas / Bitácora:", key="bitacora")

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

        tarifas  = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()), key="servicio")

        lbl_cant = "Líneas:" if div == "Móvil" else "Cantidad:"
        lineas   = st.number_input(lbl_cant, min_value=1, value=1, key="lineas")

        plan_movil_asociado = None
        if div == "Fijo" and "Full Tigo" in servicio:
            if st.checkbox("📱 ¿Incluye línea móvil?", key="incluye_movil"):
                plan_movil_asociado = "Plan Datos Tigo Empresarial 6.12 (Ilim GB)"
                st.info(f"✨ Plan móvil asociado: **{plan_movil_asociado}**")

        # Cálculo financiero
        dcto = (30 if lineas >= 9 else
                25 if lineas >= 6 else
                20 if lineas >= 3 else
                10 if lineas == 2 else 0)
        valor = tarifas[servicio] * lineas * (1 - dcto / 100)

        if valor > 0:
            valor_fmt  = f"${valor:,.0f} COP"
            dcto_txt   = f"&nbsp;&nbsp;🏷️ Descuento: {dcto}%" if dcto > 0 else ""
            frase_html = random.choice(FRASES_MOTIVACION)
            html_card  = (
                '<div style="background:#e1f5fe;padding:12px;border-radius:10px;'
                'border-left:5px solid #0288d1;margin-bottom:15px;">'
                '<p style="margin:0;font-size:1.1em;color:#01579b;">'
                f'💰 <b>Total Estimado:</b> {valor_fmt} {dcto_txt}'
                '</p>'
                f'<p style="margin:5px 0 0;font-size:0.85em;"><i>{frase_html}</i></p>'
                '</div>'
            )
            st.markdown(html_card, unsafe_allow_html=True)

        st.subheader("📎 Documentos del Cliente")
        archivos_subidos = st.file_uploader(
            "Adjuntar documentos",
            type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"],
            accept_multiple_files=True,
            key="file_uploader",
        )
        if archivos_subidos:
            st.success(f"📎 {len(archivos_subidos)} documento(s) seleccionado(s)")

    # ── BOTÓN GUARDAR (ancho completo) ─────────────────────
    st.markdown("---")
    if st.button("💾 Guardar Venta", key="btn_guardar_tab1", use_container_width=True, type="primary"):
        if not n_doc or not nombre:
            st.error("⚠️ Faltan datos obligatorios: Número de Documento y Razón Social.")
        else:
            # Guardar archivos adjuntos
            carpeta_docs = "documentos_clientes"
            os.makedirs(carpeta_docs, exist_ok=True)
            archivos_guardados = []
            if archivos_subidos:
                for doc in archivos_subidos:
                    ruta = os.path.join(carpeta_docs, f"{n_doc}_{doc.name}")
                    with open(ruta, "wb") as f:
                        f.write(doc.getbuffer())
                    archivos_guardados.append(f"{n_doc}_{doc.name}")

            # Resumen líneas móviles
            resumen_lineas = " | ".join([
                f"{ln['tipo']}/{ln['operador']}/{ln['numero']}(x{ln['cantidad']})"
                for ln in st.session_state.lista_lineas
            ]) if st.session_state.lista_lineas else ""

            # Leer/crear CSV
            df_ex = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame()

            nueva_fila = pd.DataFrame([{
                "ID_VENTA":           len(df_ex) + 1,
                "FECHA_REGISTRO":     str(date.today()),
                "ASESOR":             st.session_state.correo_asesor,
                "ESTADO":             estado,
                "DIVISION":           div,
                "PORTAFOLIO":         "MOVIL" if div == "Móvil" else "FIJO",
                "TIPO_DOC":           t_doc,
                "NIT":                n_doc,
                "CLIENTE":            nombre,
                "DIRECCION":          dir_cli,
                "BARRIO":             barrio,
                "DEPARTAMENTO":       depto or "",
                "MUNICIPIO":          muni  or "",
                "EMAIL_CLIENTE":      email_cli,
                "CONTACTO":           contacto_cli,
                "TEL_CONTACTO":       tel_contacto,
                "REP_LEGAL":          nom_rep,
                "CC_REP":             cc_rep,
                "CORREO_REP":         mail_rep,
                "TEL_REP":            tel_rep,
                "SERVICIO":           servicio,
                "CANTIDAD_LINEAS":    lineas,
                "LINEAS_DETALLE":     resumen_lineas,
                "PLAN_MOVIL_ASOC":    plan_movil_asociado or "",
                "DESCUENTO_PCT":      dcto,
                "VALOR_TOTAL":        valor,
                "BITACORA":           bitacora,
                "FECHA_SEGUIMIENTO":  str(fecha_seg),
                "TIPO_SEGUIMIENTO":   tipo_seg,
                "DOCUMENTOS":         ";".join(archivos_guardados),
                "ESTADO_FINANCIERO":  "APROBADO" if valor >= 35000 else "REVISION",
            }])

            pd.concat([df_ex, nueva_fila], ignore_index=True).to_csv(CSV_PATH, index=False)
            st.session_state.lista_lineas = []

            enviar_telegram(
                f"🆕 Nueva venta registrada\n"
                f"Asesor: {st.session_state.correo_asesor}\n"
                f"Cliente: {nombre} | {n_doc}\n"
                f"Servicio: {servicio}\n"
                f"Valor: ${valor:,.0f} COP | Estado: {estado}"
            )
            st.success("✅ Venta registrada correctamente.")
            st.rerun()

# ==========================================================
# ██████████  PESTAÑA 2: ACTUALIZAR ESTADO  ██████████
# ==========================================================
with tab2:
    st.subheader("🔄 Actualizar Seguimiento de Venta")

    if not os.path.exists(CSV_PATH):
        st.info("Aún no hay base de datos. Registra tu primera venta en la pestaña anterior.")
    else:
        df_upd = pd.read_csv(CSV_PATH)

        # Red de seguridad de columnas
        for col in ["ESTADO", "ID_VENTA", "CLIENTE", "ASESOR"]:
            if col not in df_upd.columns:
                df_upd[col] = "Sin dato"

        df_upd["ID_VENTA"] = pd.to_numeric(df_upd["ID_VENTA"], errors="coerce").fillna(0).astype(int)

        # Filtro por rol
        df_vista = df_upd.copy() if es_admin else df_upd[df_upd["ASESOR"] == st.session_state.correo_asesor].copy()

        if df_vista.empty:
            st.warning("No tienes ventas registradas para actualizar.")
        else:
            df_vista["OPCION"] = df_vista["ID_VENTA"].astype(str).str.zfill(4) + " - " + df_vista["CLIENTE"].astype(str)
            seleccion = st.selectbox("Selecciona la venta:", df_vista["OPCION"].tolist(), key="sel_venta_tab2")

            if seleccion:
                id_sel = int(seleccion[:4])
                fila   = df_upd[df_upd["ID_VENTA"] == id_sel].iloc[0]

                # Tarjeta de información
                st.markdown("---")
                ci1, ci2 = st.columns(2)
                with ci1:
                    st.info(f"📌 Estado actual: **{fila['ESTADO']}**")
                    st.write(f"**Cliente:** {fila.get('CLIENTE','N/A')}")
                    st.write(f"**Servicio:** {fila.get('SERVICIO','N/A')}")
                with ci2:
                    st.write(f"**Asesor:** {fila.get('ASESOR','N/A')}")
                    st.write(f"**División:** {fila.get('DIVISION','N/A')}")
                    try:
                        st.write(f"**Valor:** ${float(fila.get('VALOR_TOTAL',0)):,.0f} COP")
                    except Exception:
                        st.write("**Valor:** N/A")

                st.markdown("---")
                nuevo_estado = st.selectbox(
                    "Cambiar estado a:",
                    ["Cotizado", "En proceso de firma", "Ingreso de pedido", "Activado", "Anulado"],
                    key="sel_nuevo_estado_tab2",
                )
                nota_adicional = st.text_area("📝 Agregar nota a la bitácora (opcional):", key="nota_tab2")

                if st.button("🔄 Guardar y Notificar", key="btn_guardar_tab2", type="primary", use_container_width=True):
                    df_upd.loc[df_upd["ID_VENTA"] == id_sel, "ESTADO"] = nuevo_estado
                    if nota_adicional.strip():
                        texto_actual = str(fila.get("BITACORA", ""))
                        df_upd.loc[df_upd["ID_VENTA"] == id_sel, "BITACORA"] = (
                            texto_actual + f"\n[{date.today()}] {nota_adicional.strip()}"
                        )
                    df_upd.to_csv(CSV_PATH, index=False)
                    enviar_telegram(
                        f"🔄 Venta #{str(id_sel).zfill(4)} actualizada\n"
                        f"Cliente: {fila.get('CLIENTE','N/A')}\n"
                        f"Nuevo estado: {nuevo_estado}\n"
                        f"Asesor: {st.session_state.correo_asesor}"
                    )
                    st.success("✅ Estado actualizado y notificado.")
                    st.rerun()

# ==========================================================
# ██████████  PESTAÑA 3: BASE DE DATOS (solo Admin)  ██████
# ==========================================================
if es_admin and tab3 is not None:
    with tab3:
        st.subheader("📊 Dashboard y Base de Datos — Vista Administrador")

        if not os.path.exists(CSV_PATH):
            st.info("Aún no hay datos registrados.")
        else:
            df = pd.read_csv(CSV_PATH)

            if df.empty:
                st.info("La base de datos está vacía.")
            else:
                # ── Métricas rápidas ──────────────────────────────
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📁 Total Registros", len(df))
                m2.metric("✅ Activadas", len(df[df["ESTADO"].isin(["Activado", "Instalado"])]))

                col_div = "PORTAFOLIO" if "PORTAFOLIO" in df.columns else "DIVISION"
                val_fijo   = "FIJO"  if "PORTAFOLIO" in df.columns else "Fijo"
                val_movil  = "MOVIL" if "PORTAFOLIO" in df.columns else "Móvil"
                n_fijo  = len(df[df[col_div] == val_fijo])
                n_movil = len(df[df[col_div] == val_movil])
                m3.metric("📡 Fijo", n_fijo)
                m4.metric("📱 Móvil", n_movil)

                st.divider()

                # ── Gráfico 1: Ventas por Estado ──────────────────
                st.markdown("#### 📈 Ventas por Estado")
                g1_data = df["ESTADO"].value_counts().reset_index()
                g1_data.columns = ["ESTADO", "CANTIDAD"]
                grafico1 = alt.Chart(g1_data).mark_bar(color="#00a0e3").encode(
                    x=alt.X("ESTADO:N", sort="-y", title="Estado"),
                    y=alt.Y("CANTIDAD:Q", title="Cantidad"),
                    tooltip=["ESTADO", "CANTIDAD"],
                ).properties(height=280)
                st.altair_chart(grafico1, use_container_width=True)

                st.markdown("---")

                # ── Gráfico 2: Portafolio Activado vs Anulado ─────
                st.markdown("#### 📊 Portafolio: Activadas vs Anuladas")
                df["ESTADO_NORM"] = df["ESTADO"].replace("Instalado", "Activado")
                df_g2 = df[df["ESTADO_NORM"].isin(["Activado", "Anulado"])]
                if not df_g2.empty:
                    g2_data = df_g2.groupby([col_div, "ESTADO_NORM"]).size().reset_index(name="CANTIDAD")
                    grafico2 = alt.Chart(g2_data).mark_bar().encode(
                        x=alt.X(f"{col_div}:N", title="Portafolio"),
                        xOffset="ESTADO_NORM:N",
                        y=alt.Y("CANTIDAD:Q"),
                        color=alt.Color(
                            "ESTADO_NORM:N",
                            legend=alt.Legend(title="Estado"),
                            scale=alt.Scale(
                                domain=["Activado", "Anulado"],
                                range=["#00a0e3", "#231f20"]
                            ),
                        ),
                        tooltip=[col_div, "ESTADO_NORM", "CANTIDAD"],
                    ).properties(height=280)
                    st.altair_chart(grafico2, use_container_width=True)

                st.markdown("---")

                # ── Análisis automático ───────────────────────────
                st.markdown("### 💡 Análisis y Recomendaciones")
                tasa_anul = len(df[df["ESTADO"] == "Anulado"]) / len(df) * 100
                ca1, ca2 = st.columns(2)
                with ca1:
                    st.markdown("**Observación:**")
                    if tasa_anul > 20:
                        st.warning(f"⚠️ Tasa de anulación alta: {tasa_anul:.1f}%. Revisar proceso de validación.")
                    else:
                        st.success(f"✅ Tasa de anulación en {tasa_anul:.1f}%: dentro del rango aceptable.")
                with ca2:
                    st.markdown("**Oportunidad:**")
                    if n_fijo > n_movil:
                        st.write("• Portafolio **Fijo** lidera. Potenciar cross-selling hacia clientes Móviles.")
                    else:
                        st.write("• Portafolio **Móvil** lidera. Impulsar paquetes de fidelización en Fijo.")

                st.divider()

                # ── Tabla completa con filtros ────────────────────
                st.markdown("#### 🗃️ Base de Datos Completa")

                # Filtro rápido por asesor (solo admin lo ve)
                asesores = ["Todos"] + sorted(df["ASESOR"].dropna().unique().tolist())
                filtro_asesor = st.selectbox("Filtrar por asesor:", asesores, key="filtro_asesor_tab3")
                df_tabla = df if filtro_asesor == "Todos" else df[df["ASESOR"] == filtro_asesor]

                filtro_estado = st.multiselect(
                    "Filtrar por estado:",
                    options=df["ESTADO"].dropna().unique().tolist(),
                    default=df["ESTADO"].dropna().unique().tolist(),
                    key="filtro_estado_tab3",
                )
                df_tabla = df_tabla[df_tabla["ESTADO"].isin(filtro_estado)]

                st.dataframe(df_tabla, use_container_width=True, height=400)

                st.download_button(
                    label="📥 Descargar Base de Datos Completa",
                    data=df_tabla.to_csv(index=False).encode("utf-8"),
                    file_name=f"CRM_SomosTelser_{date.today()}.csv",
                    mime="text/csv",
                    key="dl_tab3",
                )
