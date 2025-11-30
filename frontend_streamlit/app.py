import streamlit as st
import requests
import os
from datetime import date
import pandas as pd


API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api_gateway:8000")

st.set_page_config(page_title="Gestión de Equipos TI", layout="wide")
st.title("Gestión de Equipos de TI - Universidad Pública")

st.sidebar.header("Módulos")
modulo = st.sidebar.radio("Selecciona un módulo", ["Equipos", "Proveedores", "Mantenimiento", "Reportes", "Alertas"])

# -------------------- EQUIPOS -------------------- #
def modulo_equipos():
    st.subheader("Gestión de equipos")

    # --- Cargar proveedores para el combo ---
    proveedores = []
    try:
        resp_prov = requests.get(f"{API_GATEWAY_URL}/proveedores/proveedores")
        if resp_prov.status_code == 200:
            proveedores = resp_prov.json()
        else:
            st.warning("No se pudieron cargar proveedores para el combo.")
    except Exception as e:
        st.warning(f"No se pudieron cargar proveedores: {e}")

    opciones_prov = ["(Sin proveedor)"]
    mapa_nombre_id = {"(Sin proveedor)": None}
    for p in proveedores:
        etiqueta = f"{p['id']} - {p['nombre']}"
        opciones_prov.append(etiqueta)
        mapa_nombre_id[etiqueta] = p["id"]

    # ---------- Alta de equipos ----------
    st.markdown("### Registrar nuevo equipo")
    with st.form("form_equipo_nuevo"):
        col1, col2, col3 = st.columns(3)
        with col1:
            nombre = st.text_input("Nombre del equipo", "")
            tipo = st.selectbox("Tipo", ["PC", "Laptop", "Switch", "Router", "Servidor"])
        with col2:
            ubicacion = st.text_input("Ubicación", "Laboratorio 1")
            fecha_compra = st.date_input("Fecha de compra", date.today())
        with col3:
            estado = st.selectbox(
                "Estado",
                ["OPERATIVO", "MANTENIMIENTO", "FUERA_DE_SERVICIO", "OBSOLETO", "BAJA"],
            )
            proveedor_sel = st.selectbox("Proveedor", opciones_prov)

        submit_nuevo = st.form_submit_button("Guardar equipo")

    if submit_nuevo:
        payload = {
            "nombre": nombre,
            "tipo": tipo,
            "ubicacion": ubicacion,
            "fecha_compra": str(fecha_compra),
            "estado": estado,
            "proveedor_id": mapa_nombre_id.get(proveedor_sel),
        }
        try:
            resp = requests.post(f"{API_GATEWAY_URL}/equipos/equipos", json=payload)
            if resp.status_code == 201:
                st.success("Equipo registrado correctamente")
            else:
                st.error(f"Error al registrar equipo: {resp.text}")
        except Exception as e:
            st.error(f"Error de conexión con el gateway: {e}")

    st.markdown("---")

    # ---------- Listado de equipos ----------
    st.markdown("### Listado de equipos")
    equipos = []
    try:
        resp = requests.get(f"{API_GATEWAY_URL}/equipos/equipos")
        if resp.status_code == 200:
            equipos = resp.json()
            if equipos:
                df = pd.DataFrame(equipos)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay equipos registrados.")
        else:
            st.error(f"Error al obtener equipos: {resp.text}")
    except Exception as e:
        st.error(f"Error de conexión con el gateway: {e}")

    # ---------- Edición / eliminación ----------
    st.markdown("### Editar / eliminar equipo")

    if not equipos:
        st.info("No hay equipos para editar/eliminar.")
        return

    # Seleccionar equipo por ID
    ids = [e["id"] for e in equipos]
    equipo_id_sel = st.selectbox("Selecciona el ID del equipo a editar", ids)

    equipo_seleccionado = next((e for e in equipos if e["id"] == equipo_id_sel), None)

    if equipo_seleccionado:
        with st.form("form_editar_equipo"):
            col1, col2, col3 = st.columns(3)
            with col1:
                nombre_e = st.text_input("Nombre", equipo_seleccionado["nombre"])
                tipo_e = st.selectbox(
                    "Tipo",
                    ["PC", "Laptop", "Switch", "Router", "Servidor"],
                    index=["PC", "Laptop", "Switch", "Router", "Servidor"].index(
                        equipo_seleccionado["tipo"]
                    )
                    if equipo_seleccionado["tipo"] in ["PC", "Laptop", "Switch", "Router", "Servidor"]
                    else 0,
                )
            with col2:
                ubicacion_e = st.text_input("Ubicación", equipo_seleccionado.get("ubicacion") or "")
                fecha_compra_e = st.date_input(
                    "Fecha de compra", date.fromisoformat(equipo_seleccionado["fecha_compra"])
                )
            with col3:
                estado_e = st.selectbox(
                    "Estado",
                    ["OPERATIVO", "MANTENIMIENTO", "FUERA_DE_SERVICIO", "OBSOLETO", "BAJA"],
                    index=["OPERATIVO", "MANTENIMIENTO", "FUERA_DE_SERVICIO", "OBSOLETO", "BAJA"].index(
                        equipo_seleccionado["estado"]
                    )
                    if equipo_seleccionado["estado"] in ["OPERATIVO", "MANTENIMIENTO", "FUERA_DE_SERVICIO", "OBSOLETO", "BAJA"]
                    else 0,
                )

                # proveedor actual
                prov_actual_id = equipo_seleccionado.get("proveedor_id")
                if prov_actual_id:
                    etiqueta_actual = next(
                        (f"{p['id']} - {p['nombre']}" for p in proveedores if p["id"] == prov_actual_id),
                        "(Sin proveedor)",
                    )
                else:
                    etiqueta_actual = "(Sin proveedor)"

                proveedor_sel_edit = st.selectbox(
                    "Proveedor",
                    opciones_prov,
                    index=opciones_prov.index(etiqueta_actual)
                    if etiqueta_actual in opciones_prov
                    else 0,
                )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                guardar_cambios = st.form_submit_button("Guardar cambios")
            with col_btn2:
                eliminar = st.form_submit_button("Eliminar equipo", type="secondary")

        # --- acciones ---
        if guardar_cambios:
            payload_update = {
                "nombre": nombre_e,
                "tipo": tipo_e,
                "ubicacion": ubicacion_e,
                "fecha_compra": str(fecha_compra_e),
                "estado": estado_e,
                "proveedor_id": mapa_nombre_id.get(proveedor_sel_edit := proveedor_sel_edit)
                if 'proveedor_sel_edit' in locals()
                else mapa_nombre_id.get(proveedor_sel_edit),
            }
            try:
                resp_upd = requests.put(
                    f"{API_GATEWAY_URL}/equipos/equipos/{equipo_id_sel}",
                    json=payload_update,
                )
                if resp_upd.status_code == 200:
                    st.success("Equipo actualizado correctamente")
                else:
                    st.error(f"Error al actualizar equipo: {resp_upd.text}")
            except Exception as e:
                st.error(f"Error al actualizar equipo: {e}")

        if eliminar:
            try:
                resp_del = requests.delete(
                    f"{API_GATEWAY_URL}/equipos/equipos/{equipo_id_sel}"
                )
                if resp_del.status_code == 200:
                    st.success("Equipo eliminado correctamente")
                else:
                    st.error(f"Error al eliminar equipo: {resp_del.text}")
            except Exception as e:
                st.error(f"Error al eliminar equipo: {e}")

# -------------------- PROVEEDORES -------------------- #
def modulo_proveedores():
    st.subheader("Gestión de proveedores")

    # ---------- Alta de proveedores ----------
    st.markdown("### Registrar nuevo proveedor")

    with st.form("form_proveedor_nuevo"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre / razón social", "")
            ruc = st.text_input("RUC", "")
            contacto = st.text_input("Persona de contacto", "")
        with col2:
            telefono = st.text_input("Teléfono", "")
            email = st.text_input("Correo electrónico", "")
            estado = st.selectbox("Estado", ["ACTIVO", "INACTIVO"])

        submit_nuevo = st.form_submit_button("Guardar proveedor")

    if submit_nuevo:
        payload = {
            "nombre": nombre,
            "ruc": ruc or None,
            "contacto": contacto or None,
            "telefono": telefono or None,
            "email": email or None,
            "estado": estado,
        }
        try:
            resp = requests.post(f"{API_GATEWAY_URL}/proveedores/proveedores", json=payload)
            if resp.status_code == 201:
                st.success("Proveedor registrado correctamente")
            else:
                st.error(f"Error al registrar proveedor: {resp.text}")
        except Exception as e:
            st.error(f"Error de conexión con el gateway: {e}")

    st.markdown("---")

    # ---------- Listado de proveedores ----------
    st.markdown("### Listado de proveedores")

    proveedores = []
    try:
        resp = requests.get(f"{API_GATEWAY_URL}/proveedores/proveedores")
        if resp.status_code == 200:
            proveedores = resp.json()
            if proveedores:
                df = pd.DataFrame(proveedores)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay proveedores registrados.")
        else:
            st.error(f"Error al obtener proveedores: {resp.text}")
    except Exception as e:
        st.error(f"Error de conexión con el gateway: {e}")

    # ---------- Edición / eliminación ----------
    st.markdown("### Editar / eliminar proveedor")

    if not proveedores:
        st.info("No hay proveedores para editar/eliminar.")
        return

    ids = [p["id"] for p in proveedores]
    proveedor_id_sel = st.selectbox("Selecciona el ID del proveedor a editar", ids)

    proveedor_sel = next((p for p in proveedores if p["id"] == proveedor_id_sel), None)

    if proveedor_sel:
        with st.form("form_editar_proveedor"):
            col1, col2 = st.columns(2)
            with col1:
                nombre_e = st.text_input("Nombre / razón social", proveedor_sel["nombre"])
                ruc_e = st.text_input("RUC", proveedor_sel.get("ruc") or "")
                contacto_e = st.text_input("Persona de contacto", proveedor_sel.get("contacto") or "")
            with col2:
                telefono_e = st.text_input("Teléfono", proveedor_sel.get("telefono") or "")
                email_e = st.text_input("Correo electrónico", proveedor_sel.get("email") or "")
                estado_e = st.selectbox(
                    "Estado",
                    ["ACTIVO", "INACTIVO"],
                    index=["ACTIVO", "INACTIVO"].index(proveedor_sel.get("estado", "ACTIVO"))
                    if proveedor_sel.get("estado") in ["ACTIVO", "INACTIVO"]
                    else 0,
                )

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                guardar_cambios = st.form_submit_button("Guardar cambios")
            with col_b2:
                eliminar = st.form_submit_button("Eliminar proveedor", type="secondary")

        # --- Actualizar ---
        if guardar_cambios:
            payload_upd = {
                "nombre": nombre_e,
                "ruc": ruc_e or None,
                "contacto": contacto_e or None,
                "telefono": telefono_e or None,
                "email": email_e or None,
                "estado": estado_e,
            }
            try:
                resp_upd = requests.put(
                    f"{API_GATEWAY_URL}/proveedores/proveedores/{proveedor_id_sel}",
                    json=payload_upd,
                )
                if resp_upd.status_code == 200:
                    st.success("Proveedor actualizado correctamente")
                else:
                    st.error(f"Error al actualizar proveedor: {resp_upd.text}")
            except Exception as e:
                st.error(f"Error al actualizar proveedor: {e}")

        # --- Eliminar ---
        if eliminar:
            try:
                resp_del = requests.delete(
                    f"{API_GATEWAY_URL}/proveedores/proveedores/{proveedor_id_sel}"
                )
                if resp_del.status_code == 200:
                    st.success("Proveedor eliminado correctamente")
                else:
                    st.error(f"Error al eliminar proveedor: {resp_del.text}")
            except Exception as e:
                st.error(f"Error al eliminar proveedor: {e}")

# -------------------- MANTENIMIENTO -------------------- #
def modulo_mantenimiento():
    st.subheader("Gestión de mantenimiento")

    # ---------- Cargar equipos para el combo ----------
    equipos = []
    try:
        resp_eq = requests.get(f"{API_GATEWAY_URL}/equipos/equipos")
        if resp_eq.status_code == 200:
            equipos = resp_eq.json()
        else:
            st.warning("No se pudieron cargar equipos para el combo.")
    except Exception as e:
        st.warning(f"No se pudieron cargar equipos: {e}")

    opciones_equipos = []
    mapa_equipo_label_id = {}
    for e in equipos:
        etiqueta = f"{e['id']} - {e['nombre']}"
        opciones_equipos.append(etiqueta)
        mapa_equipo_label_id[etiqueta] = e["id"]

    if not opciones_equipos:
        st.info("⚠️ Primero registra al menos un equipo en el módulo de Equipos.")
        return

    # ---------- Alta de mantenimientos ----------
    st.markdown("### Programar mantenimiento")

    with st.form("form_mantenimiento_nuevo"):
        col1, col2, col3 = st.columns(3)
        with col1:
            equipo_label = st.selectbox("Equipo", opciones_equipos)
            tipo = st.selectbox("Tipo de mantenimiento", ["PREVENTIVO", "CORRECTIVO"])
        with col2:
            fecha_programada = st.date_input("Fecha programada", date.today())
            estado = st.selectbox(
                "Estado",
                ["PROGRAMADO", "EN_PROCESO", "COMPLETADO", "CANCELADO"],
            )
        with col3:
            costo = st.number_input("Costo estimado", min_value=0.0, value=0.0)
            descripcion = st.text_input("Descripción", "")

        submit_nuevo = st.form_submit_button("Guardar mantenimiento")

    if submit_nuevo:
        payload = {
            "equipo_id": mapa_equipo_label_id[equipo_label],
            "tipo": tipo,
            "descripcion": descripcion or None,
            "fecha_programada": str(fecha_programada),
            "fecha_real": None,
            "estado": estado,
            "costo": float(costo) if costo else None,
        }
        try:
            resp = requests.post(
                f"{API_GATEWAY_URL}/mantenimiento/mantenimientos",
                json=payload,
            )
            if resp.status_code == 201:
                st.success("Mantenimiento registrado correctamente")
            else:
                st.error(f"Error al registrar mantenimiento: {resp.text}")
        except Exception as e:
            st.error(f"Error de conexión con el gateway: {e}")

    st.markdown("---")

    # ---------- Listado de mantenimientos ----------
    st.markdown("### Listado de mantenimientos")

    mantenimientos = []
    try:
        resp = requests.get(f"{API_GATEWAY_URL}/mantenimiento/mantenimientos")
        if resp.status_code == 200:
            mantenimientos = resp.json()
            if mantenimientos:
                df = pd.DataFrame(mantenimientos)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay mantenimientos registrados.")
        else:
            st.error(f"Error al obtener mantenimientos: {resp.text}")
    except Exception as e:
        st.error(f"Error de conexión con el gateway: {e}")

    # ---------- Edición / eliminación ----------
    st.markdown("### Editar / eliminar mantenimiento")

    if not mantenimientos:
        st.info("No hay mantenimientos para editar/eliminar.")
        return

    ids = [m["id"] for m in mantenimientos]
    mant_id_sel = st.selectbox("Selecciona el ID del mantenimiento", ids)

    mant_sel = next((m for m in mantenimientos if m["id"] == mant_id_sel), None)

    if mant_sel:
        # Equipo actual
        eq_actual_id = mant_sel.get("equipo_id")
        etiqueta_actual = next(
            (f"{e['id']} - {e['nombre']}" for e in equipos if e["id"] == eq_actual_id),
            opciones_equipos[0],
        )

        # Fechas
        fp = date.fromisoformat(mant_sel["fecha_programada"])
        fr_raw = mant_sel.get("fecha_real")
        fr_default = date.fromisoformat(fr_raw) if fr_raw else date.today()

        with st.form("form_editar_mantenimiento"):
            col1, col2, col3 = st.columns(3)
            with col1:
                equipo_label_e = st.selectbox(
                    "Equipo",
                    opciones_equipos,
                    index=opciones_equipos.index(etiqueta_actual)
                    if etiqueta_actual in opciones_equipos
                    else 0,
                )
                tipo_e = st.selectbox(
                    "Tipo",
                    ["PREVENTIVO", "CORRECTIVO"],
                    index=["PREVENTIVO", "CORRECTIVO"].index(mant_sel["tipo"])
                    if mant_sel["tipo"] in ["PREVENTIVO", "CORRECTIVO"]
                    else 0,
                )
            with col2:
                fecha_programada_e = st.date_input("Fecha programada", fp)
                estado_e = st.selectbox(
                    "Estado",
                    ["PROGRAMADO", "EN_PROCESO", "COMPLETADO", "CANCELADO"],
                    index=["PROGRAMADO", "EN_PROCESO", "COMPLETADO", "CANCELADO"].index(
                        mant_sel["estado"]
                    )
                    if mant_sel["estado"] in ["PROGRAMADO", "EN_PROCESO", "COMPLETADO", "CANCELADO"]
                    else 0,
                )
            with col3:
                usar_fecha_real = st.checkbox(
                    "Registrar fecha real",
                    value=bool(fr_raw or estado_e == "COMPLETADO"),
                )
                fecha_real_e = st.date_input("Fecha real", fr_default)
                costo_e = st.number_input(
                    "Costo",
                    min_value=0.0,
                    value=float(mant_sel["costo"]) if mant_sel.get("costo") is not None else 0.0,
                )

            descripcion_e = st.text_input(
                "Descripción",
                mant_sel.get("descripcion") or "",
            )

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                guardar = st.form_submit_button("Guardar cambios")
            with col_b2:
                eliminar = st.form_submit_button("Eliminar mantenimiento", type="secondary")

        # ---- acciones ----
        if guardar:
            payload_upd = {
                "equipo_id": mapa_equipo_label_id[equipo_label_e],
                "tipo": tipo_e,
                "descripcion": descripcion_e or None,
                "fecha_programada": str(fecha_programada_e),
                "estado": estado_e,
                "costo": float(costo_e) if costo_e else None,
            }
            # lógica para fecha_real
            if usar_fecha_real:
                payload_upd["fecha_real"] = str(fecha_real_e)
            else:
                payload_upd["fecha_real"] = None

            try:
                resp_upd = requests.put(
                    f"{API_GATEWAY_URL}/mantenimiento/mantenimientos/{mant_id_sel}",
                    json=payload_upd,
                )
                if resp_upd.status_code == 200:
                    st.success("Mantenimiento actualizado correctamente")
                else:
                    st.error(f"Error al actualizar mantenimiento: {resp_upd.text}")
            except Exception as e:
                st.error(f"Error al actualizar mantenimiento: {e}")

        if eliminar:
            try:
                resp_del = requests.delete(
                    f"{API_GATEWAY_URL}/mantenimiento/mantenimientos/{mant_id_sel}"
                )
                if resp_del.status_code == 200:
                    st.success("Mantenimiento eliminado correctamente")
                else:
                    st.error(f"Error al eliminar mantenimiento: {resp_del.text}")
            except Exception as e:
                st.error(f"Error al eliminar mantenimiento: {e}")

    st.markdown("---")

    # ---------- Mantenimientos próximos (agente "manual") ----------
    st.subheader("Mantenimientos próximos")

    dias = st.slider("Días hacia adelante", min_value=1, max_value=30, value=7)
    if st.button("Consultar próximos mantenimientos", key="btn_proximos_mant"):
        try:
            resp = requests.get(
                f"{API_GATEWAY_URL}/mantenimiento/mantenimientos/proximos",
                params={"dias": dias},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    st.dataframe(data, use_container_width=True)
                else:
                    st.info("No hay mantenimientos programados en ese rango.")
            else:
                st.error(f"Error al obtener mantenimientos próximos: {resp.text}")
        except Exception as e:
            st.error(f"Error de conexión con el gateway: {e}")

# -------------------- REPORTES -------------------- #
def modulo_reportes():
    st.subheader("Dashboard de equipos y mantenimiento")

    # --- Resumen de equipos ---
    st.markdown("### Resumen de equipos")

    try:
        resp_eq = requests.get(f"{API_GATEWAY_URL}/reportes/equipos-resumen")
        if resp_eq.status_code == 200:
            datos_eq = resp_eq.json()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de equipos", datos_eq.get("total_equipos", 0))
            with col2:
                st.write(" ")

            por_estado = datos_eq.get("por_estado", {})
            por_tipo = datos_eq.get("por_tipo", {})

            col_e1, col_e2 = st.columns(2)
            if por_estado:
                df_estado = pd.DataFrame(
                    {"Estado": list(por_estado.keys()), "Cantidad": list(por_estado.values())}
                ).set_index("Estado")
                with col_e1:
                    st.bar_chart(df_estado)
            else:
                with col_e1:
                    st.info("Sin datos de estado de equipos.")

            if por_tipo:
                df_tipo = pd.DataFrame(
                    {"Tipo": list(por_tipo.keys()), "Cantidad": list(por_tipo.values())}
                ).set_index("Tipo")
                with col_e2:
                    st.bar_chart(df_tipo)
            else:
                with col_e2:
                    st.info("Sin datos de tipo de equipos.")
        else:
            st.error(f"Error al obtener resumen de equipos: {resp_eq.text}")
    except Exception as e:
        st.error(f"Error de conexión al obtener resumen de equipos: {e}")

    st.markdown("---")

    # --- Resumen de mantenimiento ---
    st.markdown("### Resumen de mantenimiento")

    try:
        resp_mt = requests.get(f"{API_GATEWAY_URL}/reportes/mantenimiento-resumen")
        if resp_mt.status_code == 200:
            datos_mt = resp_mt.json()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de mantenimientos", datos_mt.get("total_mantenimientos", 0))
            with col2:
                st.write(" ")

            por_tipo_m = datos_mt.get("por_tipo", {})
            por_estado_m = datos_mt.get("por_estado", {})

            col_m1, col_m2 = st.columns(2)
            if por_tipo_m:
                df_tipo_m = pd.DataFrame(
                    {"Tipo": list(por_tipo_m.keys()), "Cantidad": list(por_tipo_m.values())}
                ).set_index("Tipo")
                with col_m1:
                    st.bar_chart(df_tipo_m)
            else:
                with col_m1:
                    st.info("Sin datos de tipo de mantenimiento.")

            if por_estado_m:
                df_estado_m = pd.DataFrame(
                    {"Estado": list(por_estado_m.keys()), "Cantidad": list(por_estado_m.values())}
                ).set_index("Estado")
                with col_m2:
                    st.bar_chart(df_estado_m)
            else:
                with col_m2:
                    st.info("Sin datos de estado de mantenimiento.")
        else:
            st.error(f"Error al obtener resumen de mantenimiento: {resp_mt.text}")
    except Exception as e:
        st.error(f"Error de conexión al obtener resumen de mantenimiento: {e}")

    st.markdown("---")

    # --- Descarga de PDF ---
    st.markdown("### Exportar reporte")

    if "pdf_reporte" not in st.session_state:
        st.session_state.pdf_reporte = None

    if st.button("Generar reporte PDF"):
        try:
            resp_pdf = requests.get(f"{API_GATEWAY_URL}/reportes/reporte-pdf")
            if resp_pdf.status_code == 200:
                st.session_state.pdf_reporte = resp_pdf.content
                st.success("Reporte PDF generado correctamente. Ahora puedes descargarlo.")
            else:
                st.error(f"Error al generar PDF: {resp_pdf.text}")
        except Exception as e:
            st.error(f"Error de conexión al generar PDF: {e}")

    if st.session_state.pdf_reporte:
        st.download_button(
            label="Descargar reporte PDF",
            data=st.session_state.pdf_reporte,
            file_name="reporte_ti.pdf",
            mime="application/pdf",
        )

# -------------------- ALERTAS -------------------- #
def modulo_alertas():
    st.subheader("Alertas inteligentes")

    col1, col2 = st.columns(2)
    with col1:
        dias = st.slider(
            "Días hacia adelante para revisar mantenimientos",
            min_value=1,
            max_value=30,
            value=7,
        )
    with col2:
        anios = st.slider(
            "Años de antigüedad para marcar equipos como obsoletos",
            min_value=1,
            max_value=10,
            value=5,
        )

    if st.button("Actualizar alertas"):
        try:
            resp = requests.get(
                f"{API_GATEWAY_URL}/agente/resumen-alertas",
                params={"dias": dias, "anios": anios},
            )
            if resp.status_code == 200:
                datos = resp.json()

                st.markdown("### Mantenimientos próximos")
                proximos = datos.get("proximos_mantenimientos", [])
                if proximos:
                    st.dataframe(proximos, use_container_width=True)
                else:
                    st.success("✅ No hay mantenimientos programados en ese rango de días.")

                st.markdown("---")
                st.markdown("### Equipos obsoletos")
                obsoletos = datos.get("equipos_obsoletos", [])
                if obsoletos:
                    st.dataframe(obsoletos, use_container_width=True)
                else:
                    st.success("✅ No hay equipos marcados como obsoletos con ese criterio.")
            else:
                st.error(f"Error al obtener alertas: {resp.text}")
        except Exception as e:
            st.error(f"Error de conexión con el gateway: {e}")
    else:
        st.info("Configura los parámetros y pulsa **Actualizar alertas** para ver resultados.")

# --------- Router simple --------- #
if modulo == "Equipos":
    modulo_equipos()
elif modulo == "Proveedores":
    modulo_proveedores()
elif modulo == "Mantenimiento":
    modulo_mantenimiento()
elif modulo == "Reportes":
    modulo_reportes()
elif modulo == "Alertas":
    modulo_alertas()