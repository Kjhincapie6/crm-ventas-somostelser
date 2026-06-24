# Cálculo Agente Financiero
    dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
    valor = (tarifas[servicio] * lineas) * (1 - dcto/100)
    umbral = 35000.0
    es_rentable = valor >= umbral
    
    # Auditoría en tiempo real
    if n_doc and nombre:
        if es_rentable:
            st.success("✅ Auditoría: Venta financieramente saludable.")
        else:
            st.warning("⚠️ Auditoría: Rentabilidad baja, requiere aprobación gerencial.")
    
    st.info(f"💰 **Resumen:** {div} | {servicio} | Dcto: {dcto}% | **Total: ${valor:,.0f} COP**")
    
    guardar = st.form_submit_button("💾 Guardar Venta Completa")

if guardar:
    if n_doc and nombre:
        estado_financiero = "APROBADO" if es_rentable else "REVISION"
        nueva_fila = pd.DataFrame([{
            'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre, 'DIRECCION': dir, 
            'BARRIO': barrio, 'MUNICIPIO': muni, 'EMAIL': email_cli, 'MOVIL': movil_cli,
            'REP_LEGAL': nom_rep, 'CC_REP': cc_rep, 'MAIL_REP': mail_rep, 
            'SERVICIO': servicio, 'VALOR_TOTAL': valor, 'ESTADO': estado,
            'ESTADO_FINANCIERO': estado_financiero,
            'ASESOR_REGISTRO': st.session_state.correo_asesor
        }])
        archivo = "crm_sistema_maestro.csv"
        pd.concat([pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame(), nueva_fila]).to_csv(archivo, index=False)
        st.success(f"✅ Venta registrada con estado: {estado_financiero}")
    else:
        st.error("⚠️ Error: Debe ingresar el Documento y el Nombre del Cliente.")
