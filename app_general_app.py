import streamlit as st
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.graphics.shapes import Drawing, Rect, String
from PIL import Image as PILImage
import io

st.set_page_config(
    page_title="Generador Universal de Presupuestos",
    page_icon="📋",
    layout="centered"
)

# Estilos CSS con eliminación total de botones + y -
st.markdown("""
<style>
    .main-title {
        color: #1A2530;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #2980B9;
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #2980B9;
        color: white;
        font-weight: bold;
        font-size: 18px;
        border-radius: 8px;
        padding: 10px 24px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3498DB;
        color: white;
    }

    /* ELIMINA Y OCULTA COMPLETAMENTE LOS BOTONES + Y - DE TODOS LOS CAMPOS NUMÉRICOS */
    div[data-testid="stNumberInputContainer"] button {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📋 SISTEMA UNIVERSAL DE PRESUPUESTOS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Cotizaciones Profesionales para Pequeños Negocios y Servicios</div>',
            unsafe_allow_html=True)


# Funciones de formato de miles
def fmt_currency(val):
    return f"${val:,.2f}"


def fmt_qty(val):
    return f"{val:,.2f}".rstrip('0').rstrip('.')


# Construcción del PDF
def generar_pdf(datos_taller, datos_cliente, conceptos, condiciones, incluir_iva, logo_file=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []

    PRIMARY = colors.HexColor(datos_taller.get('color_primario', "#1A2530"))
    ACCENT = colors.HexColor(datos_taller.get('color_acento', "#2980B9"))
    LIGHT_BG = colors.HexColor("#F8F9FA")
    ALT_BG = colors.HexColor("#F2F4F4")
    TEXT_DARK = colors.HexColor("#2C3E50")
    LINE_COLOR = colors.HexColor("#BDC3C7")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=15, textColor=PRIMARY, leading=18
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#566573"), leading=12
    )

    meta_val = ParagraphStyle(
        'MetaVal', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, textColor=TEXT_DARK, leading=12
    )

    th_style = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white, alignment=1
    )

    cell_left = ParagraphStyle(
        'CellLeft', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, textColor=TEXT_DARK, leading=11
    )

    cell_center = ParagraphStyle(
        'CellCenter', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, textColor=TEXT_DARK, alignment=1, leading=11
    )

    cell_right = ParagraphStyle(
        'CellRight', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, textColor=TEXT_DARK, alignment=2, leading=11
    )

    bold_right = ParagraphStyle(
        'BoldRight', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, textColor=PRIMARY, alignment=2, leading=11
    )

    # Logo / Encabezado
    if logo_file is not None:
        try:
            img_bytes = logo_file.getvalue()
            pil_img = PILImage.open(io.BytesIO(img_bytes))
            w, h = pil_img.size
            max_w, max_h = 130, 60
            ratio = min(max_w / w, max_h / h)
            new_w, new_h = w * ratio, h * ratio

            logo_element = RLImage(io.BytesIO(img_bytes), width=new_w, height=new_h)
        except Exception:
            logo_element = Paragraph(f"<b>{datos_taller['nombre_taller']}</b>", title_style)
    else:
        d = Drawing(130, 60)
        d.add(Rect(0, 0, 130, 60, fillColor=colors.HexColor("#FAFAFA"), strokeColor=LINE_COLOR, strokeWidth=1,
                   strokeDashArray=[3, 3], rx=4, ry=4))
        d.add(String(65, 34, datos_taller['nombre_taller'][:18].upper(), textAnchor="middle", fontName="Helvetica-Bold",
                     fontSize=8, fillColor=PRIMARY))
        d.add(String(65, 20, datos_taller.get('giro', 'SERVICIOS EN GENERAL')[:22].upper(), textAnchor="middle",
                     fontName="Helvetica-Bold", fontSize=7, fillColor=ACCENT))
        logo_element = d

    header_info = [
        [Paragraph(f"<b>{datos_taller['nombre_taller'].upper()}</b>", title_style), logo_element],
        [Paragraph(f"<b>Propietario / Encargado:</b> {datos_taller['propietario']}<br/>"
                   f"<b>Teléfono / WhatsApp:</b> {datos_taller['telefono']} &nbsp;|&nbsp; <b>RFC/ID:</b> {datos_taller['rfc']}<br/>"
                   f"<b>Dirección:</b> {datos_taller['direccion']}", subtitle_style), ""]
    ]

    header_table = Table(header_info, colWidths=[410, 130])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (1, 0), (1, 1)),
        ('ALIGN', (1, 0), (1, 1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=8))

    # Bloque de metadatos
    meta_data = [
        [
            Paragraph("<b>COTIZACIÓN / PRESUPUESTO</b>",
                      ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11,
                                     textColor=PRIMARY)),
            Paragraph(f"<b>FOLIO N°:</b> {datos_cliente['folio']}",
                      ParagraphStyle('Folio', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10,
                                     textColor=ACCENT, alignment=2))
        ],
        [
            Paragraph(f"<b>Cliente:</b> {datos_cliente['nombre']}", meta_val),
            Paragraph(f"<b>Fecha:</b> {datos_cliente['fecha'].strftime('%d/%m/%Y')}",
                      ParagraphStyle('RightMeta', parent=meta_val, alignment=2))
        ],
        [
            Paragraph(f"<b>Teléfono Cliente:</b> {datos_cliente['telefono']}", meta_val),
            Paragraph(f"<b>Vigencia:</b> {datos_cliente['vigencia']} Días",
                      ParagraphStyle('RightMeta2', parent=meta_val, alignment=2))
        ],
        [
            Paragraph(f"<b>Obra / Servicio / Ubicación:</b> {datos_cliente['ubicacion']}", meta_val),
            Paragraph("<b>Página:</b> 1 de 1", ParagraphStyle('RightMeta3', parent=meta_val, alignment=2))
        ]
    ]

    meta_table = Table(meta_data, colWidths=[370, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, LINE_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#EAEDED")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Encabezados de Tabla
    headers = [
        Paragraph("CONCEPTO Y DESCRIPCIÓN DEL TRABAJO O SERVICIO", th_style),
        Paragraph("UNIDAD", th_style),
        Paragraph("CANT.", th_style),
        Paragraph("P. UNITARIO", th_style),
        Paragraph("TOTAL", th_style)
    ]

    items_data = [headers]
    subtotal = 0.0

    for item in conceptos:
        if item['concepto'].strip():
            cant = float(item['cantidad'])
            precio = float(item['precio'])
            tot = cant * precio
            subtotal += tot

            items_data.append([
                Paragraph(item['concepto'].replace('\n', '<br/>'), cell_left),
                Paragraph(item['unidad'], cell_center),
                Paragraph(fmt_qty(cant), cell_center),
                Paragraph(fmt_currency(precio), cell_right),
                Paragraph(fmt_currency(tot), cell_right)
            ])

    while len(items_data) < 6:
        items_data.append([
            Paragraph("&nbsp;", cell_left),
            Paragraph("", cell_center),
            Paragraph("", cell_center),
            Paragraph("", cell_right),
            Paragraph("", cell_right)
        ])

    items_table = Table(items_data, colWidths=[280, 50, 45, 80, 85])
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, LINE_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]

    for idx in range(1, len(items_data)):
        if idx % 2 == 0:
            t_style.append(('BACKGROUND', (0, idx), (-1, idx), ALT_BG))

    items_table.setStyle(TableStyle(t_style))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # Cálculos
    iva = subtotal * 0.16 if incluir_iva else 0.0
    total = subtotal + iva

    summary_data = [
        [
            Paragraph("<b>TÉRMINOS Y CONDICIONES:</b>",
                      ParagraphStyle('TermsTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8,
                                     textColor=PRIMARY)),
            Paragraph("SUBTOTAL:", bold_right),
            Paragraph(fmt_currency(subtotal), ParagraphStyle('R1', parent=cell_right, fontName='Helvetica-Bold'))
        ]
    ]

    if incluir_iva:
        summary_data.append([
            Paragraph("", cell_left),
            Paragraph("I.V.A. (16%):", bold_right),
            Paragraph(fmt_currency(iva), cell_right)
        ])

    anticipo_line = f"• Requiere <b>{condiciones['anticipo_pct']}% de anticipo</b> para iniciar el trabajo.<br/>" if \
    condiciones['anticipo_pct'] > 0 else "• <b>No requiere anticipo inicial.</b><br/>"
    restante_pct = 100 - condiciones['anticipo_pct']
    restante_line = f"• <b>{restante_pct}% restante</b> contra-entrega o finalización del servicio.<br/>" if \
    condiciones['anticipo_pct'] > 0 else "• <b>100% del pago</b> a la contra-entrega o finalización del servicio.<br/>"

    summary_data.append([
        Paragraph(f"{anticipo_line}"
                  f"{restante_line}"
                  f"• Tiempo estimado de ejecución/entrega: <b>{condiciones['dias_entrega']} días hábiles</b>.<br/>"
                  "• Todo trabajo adicional no contemplado en esta cotización se presupuestará por separado.",
                  ParagraphStyle('Terms', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5,
                                 textColor=colors.HexColor("#566573"), leading=10.5)),
        Paragraph("<b>TOTAL:</b>", bold_right),
        Paragraph(f"<b>{fmt_currency(total)}</b>",
                  ParagraphStyle('R2', parent=cell_right, fontName='Helvetica-Bold', textColor=ACCENT, fontSize=10))
    ])

    summary_table = Table(summary_data, colWidths=[310, 110, 120])
    summary_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (0, 0 if not incluir_iva else 1)),
        ('SPAN', (0, len(summary_data) - 1), (0, len(summary_data) - 1)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
        ('BOX', (0, 0), (0, -1), 0.5, LINE_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (1, 0), (2, -1), 0.5, LINE_COLOR),
        ('BACKGROUND', (1, 0), (2, -1), colors.HexColor("#FAFAFA")),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 25))

    # Firmas
    sig_data = [
        [
            Paragraph(
                f"_______________________________________<br/><b>{datos_taller['propietario'].upper()}</b><br/>{datos_taller['nombre_taller']}",
                ParagraphStyle('Sig1', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, alignment=1)),
            Paragraph(
                "_______________________________________<br/><b>ACEPTADO POR EL CLIENTE</b><br/>Firma de Conformidad",
                ParagraphStyle('Sig2', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, alignment=1))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(sig_table)

    doc.build(story)
    buffer.seek(0)
    return buffer


# --- INTERFAZ STREAMLIT ---

GIROS_PREDEFINIDOS = {
    "Personalizado (Cualquier Negocio)": {
        "color_primario": "#1A2530", "color_acento": "#2980B9",
        "nombre_ejemplo": "MI NEGOCIO / SERVICIO", "giro": "SERVICIOS GENERALES",
        "propietario_ejemplo": "C. Juan Pérez (Propietario)",
        "tel_ejemplo": "(000) 000-0000",
        "rfc_ejemplo": "XAXX010101000",
        "dir_ejemplo": "Calle Principal #123, Ciudad",
        "unidades": ["PZA", "SERVIC", "HORA", "KG", "MTS", "M2", "LOTE"]
    },
    "Herrería / Metalmecánica": {
        "color_primario": "#1A2530", "color_acento": "#D35400",
        "nombre_ejemplo": "TALLER DE HERRERÍA Y METAL", "giro": "HERRERÍA Y FORJA",
        "propietario_ejemplo": "Encargado de Taller",
        "tel_ejemplo": "(000) 000-0000",
        "rfc_ejemplo": "XAXX010101000",
        "dir_ejemplo": "Zona Industrial #456",
        "unidades": ["PZA", "ML", "M2", "KG", "LOTE", "SERVIC"]
    },
    "Carpintería / Mueblería": {
        "color_primario": "#4A235A", "color_acento": "#CA6F1E",
        "nombre_ejemplo": "CARPINTERÍA Y DISEÑO EN MADERA", "giro": "CARPINTERÍA GENERAL",
        "propietario_ejemplo": "Maestro Carpintero",
        "tel_ejemplo": "(000) 000-0000",
        "rfc_ejemplo": "XAXX010101000",
        "dir_ejemplo": "Av. Los Pinos #789",
        "unidades": ["PZA", "ML", "M2", "JUEGO", "SERVIC"]
    },
    "Plomería / Electricidad / Mantenimiento": {
        "color_primario": "#1B4F72", "color_acento": "#28B463",
        "nombre_ejemplo": "SERVICIOS TÉCNICOS INTEGRALES", "giro": "MANTENIMIENTO GENERAL",
        "propietario_ejemplo": "Técnico Especialista",
        "tel_ejemplo": "(000) 000-0000",
        "rfc_ejemplo": "XAXX010101000",
        "dir_ejemplo": "Col. Centro #101",
        "unidades": ["SERVIC", "PZA", "MTS", "HORA", "LOTE"]
    },
    "Imprenta / Diseño / Publicidad": {
        "color_primario": "#117A65", "color_acento": "#E74C3C",
        "nombre_ejemplo": "STUDIO CREATIVO Y PUBLICIDAD", "giro": "IMPRENTA Y DISEÑO",
        "propietario_ejemplo": "Director Creativo",
        "tel_ejemplo": "(000) 000-0000",
        "rfc_ejemplo": "XAXX010101000",
        "dir_ejemplo": "Plaza Comercial Local 5",
        "unidades": ["PZA", "CIENTO", "MILLAR", "M2", "SERVIC"]
    },
    "Mecánica / Taller Automotriz": {
        "color_primario": "#212F3D", "color_acento": "#C0392B",
        "nombre_ejemplo": "TALLER MECÁNICO AUTOMOTRIZ", "giro": "SERVICIO AUTOMOTRIZ",
        "propietario_ejemplo": "Ing. de Servicio",
        "tel_ejemplo": "(000) 000-0000",
        "rfc_ejemplo": "XAXX010101000",
        "dir_ejemplo": "Calzada Principal #302",
        "unidades": ["SERVIC", "PZA", "JUEGO", "LITRO", "HORA"]
    }
}

st.sidebar.header("⚙️ Configuración del Negocio")
giro_sel = st.sidebar.selectbox("Selecciona el tipo de negocio", list(GIROS_PREDEFINIDOS.keys()))
config_giro = GIROS_PREDEFINIDOS[giro_sel]

# Carga de Logo
st.sidebar.markdown("---")
st.sidebar.subheader("🖼️ Logotipo del Negocio")
logo_file = st.sidebar.file_uploader("Sube el logo de tu negocio (PNG / JPG)", type=["png", "jpg", "jpeg"])

if logo_file:
    st.sidebar.image(logo_file, caption="Vista previa del Logo", width="stretch")

with st.expander("📌 Configurar Datos Fijos de tu Negocio", expanded=False):
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        taller_nombre = st.text_input("Nombre comercial del negocio", config_giro["nombre_ejemplo"])
        taller_propietario = st.text_input("Nombre del Propietario / Encargado", config_giro["propietario_ejemplo"])
        taller_tel = st.text_input("Teléfono / WhatsApp de contacto", config_giro["tel_ejemplo"])
    with col_t2:
        taller_giro = st.text_input("Giro / Especialidad", config_giro["giro"])
        taller_rfc = st.text_input("RFC o Identificación Fiscal", config_giro["rfc_ejemplo"])
        taller_dir = st.text_input("Dirección física", config_giro["dir_ejemplo"])

datos_taller = {
    'nombre_taller': taller_nombre,
    'propietario': taller_propietario,
    'telefono': taller_tel,
    'rfc': taller_rfc,
    'direccion': taller_dir,
    'giro': taller_giro,
    'color_primario': config_giro["color_primario"],
    'color_acento': config_giro["color_acento"]
}

st.subheader("📋 Datos del Cliente")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    cliente_nombre = st.text_input("Nombre del Cliente", placeholder="Ej. Juan Pérez")
    cliente_ubicacion = st.text_input("Dirección u Ubicación de la Obra/Servicio", placeholder="Ej. Calle X #123")

with c2:
    cliente_tel = st.text_input("Teléfono Cliente", placeholder="Ej. 312 000 0000")
    folio_num = st.text_input("Número de Folio", "001/2026")

with c3:
    fecha_cot = st.date_input("Fecha de emisión", datetime.date.today())
    vigencia = st.number_input("Vigencia (Días)", min_value=1, value=15)

datos_cliente = {
    'nombre': cliente_nombre if cliente_nombre else "___________________________",
    'telefono': cliente_tel if cliente_tel else "___________________________",
    'ubicacion': cliente_ubicacion if cliente_ubicacion else "___________________________",
    'folio': folio_num,
    'fecha': fecha_cot,
    'vigencia': vigencia
}

st.subheader("🛠️ Conceptos y Servicios a Cotizar")
st.caption("Detalle los conceptos del trabajo. Se dará formato de miles automáticamente (ej. $100,000.00).")

if 'num_conceptos' not in st.session_state:
    st.session_state.num_conceptos = 3

conceptos_lista = []

for i in range(st.session_state.num_conceptos):
    st.markdown(f"**Concepto #{i + 1}**")
    col_desc, col_un, col_cant, col_precio = st.columns([3.0, 1.0, 1.2, 2.8])

    with col_desc:
        desc = st.text_area(
            f"Descripción #{i + 1}",
            placeholder="Escriba el detalle del trabajo o material...",
            key=f"desc_{i}",
            height=65,
            label_visibility="collapsed"
        )
    with col_un:
        unidad = st.selectbox(f"Unidad #{i + 1}", config_giro["unidades"], key=f"un_{i}", label_visibility="collapsed")
    with col_cant:
        cant = st.number_input(
            f"Cantidad #{i + 1}",
            min_value=1,
            value=1,
            key=f"cant_{i}",
            label_visibility="collapsed"
        )
    with col_precio:
        precio = st.number_input(
            f"Precio Unitario #{i + 1} ($ MXN)",
            min_value=0.0,
            value=0.0,
            format="%.2f",
            key=f"prec_{i}"
        )
        if precio > 0:
            st.caption(f"💵 **Precio:** `{fmt_currency(precio)} MXN`")

    conceptos_lista.append({
        'concepto': desc,
        'unidad': unidad,
        'cantidad': cant,
        'precio': precio
    })

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("➕ Agregar otro concepto"):
        st.session_state.num_conceptos += 1
        st.rerun()

with col_btn2:
    if st.session_state.num_conceptos > 1:
        if st.button("➖ Eliminar último concepto"):
            st.session_state.num_conceptos -= 1
            st.rerun()

st.subheader("💵 Condiciones de Pago y Totales")
col_cond1, col_cond2, col_cond3 = st.columns(3)

with col_cond1:
    anticipo = st.number_input("% Anticipo requerido", min_value=0, max_value=100, value=50)
with col_cond2:
    dias_entrega = st.number_input("Días hábiles de entrega", min_value=1, value=1)
with col_cond3:
    incluir_iva = st.checkbox("¿Desglosar IVA (16%)?", value=True)

condiciones = {
    'anticipo_pct': anticipo,
    'dias_entrega': dias_entrega
}

# Previsualización del total
subtotal_preview = sum([c['cantidad'] * c['precio'] for c in conceptos_lista if c['concepto']])
total_preview = subtotal_preview * 1.16 if incluir_iva else subtotal_preview

st.markdown("---")
col_prev1, col_prev2 = st.columns([2, 1])
with col_prev1:
    st.markdown(f"### **Total Estimado:** `{fmt_currency(total_preview)} MXN`")
    if incluir_iva:
        st.caption(f"(Subtotal: {fmt_currency(subtotal_preview)} + IVA 16%: {fmt_currency(subtotal_preview * 0.16)})")

with col_prev2:
    if st.button("📄 GENERAR PRESUPUESTO PDF"):
        pdf_bytes = generar_pdf(datos_taller, datos_cliente, conceptos_lista, condiciones, incluir_iva, logo_file)

        st.download_button(
            label="⬇️ DESCARGAR PDF",
            data=pdf_bytes,
            file_name=f"Presupuesto_{folio_num.replace('/', '-')}_{cliente_nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        st.success("✅ Presupuesto en PDF generado. Haz clic arriba para descargarlo.")
