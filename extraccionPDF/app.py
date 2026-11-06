import fitz #PyMuPDF #leer texto de pdf
import pytesseract #OCR #leer texto de imagen
from PIL import Image #Presentar imagenes
import io  #manejar flujo 
import pdfplumber #leer tablas de pdf
import os

from shiny import App, reactive, render, ui
import tempfile #crear archivos temporales

pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"

def extraer_texto_directo(page):
    """Extrae texto directamente de la página."""
    return page.get_text()

def extraer_imagenes_y_ocr(page, doc, contador):
    """Extrae imágenes y aplica OCR si contienen texto."""
    resultados = []
    
    for i, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_img = doc.extract_image(xref)
        img_bytes = base_img["image"]
        image = Image.open(io.BytesIO(img_bytes))
        texto_ocr = pytesseract.image_to_string(image)
        if texto_ocr.strip():
            resultados.append((
                contador + i, 
                texto_ocr.strip()
                ))
    return resultados

def extraer_tablas_pdfplumber(path_pdf, pagina_actual):
    """Extrae tablas como texto plano usando pdfplumber."""
    tablas_extraidas = []
    with pdfplumber.open(path_pdf) as pdf:
        if pagina_actual < len(pdf.pages):
            page = pdf.pages[pagina_actual]
            tables = page.extract_tables()
            for t in tables:
                tabla_texto = "\n".join([
                    "\t".join(
                        cell if cell is not None 
                        else "" for cell in fila)
                    for fila in t
                ])
                tablas_extraidas.append(tabla_texto)
    return tablas_extraidas

def procesar_pdf_shiny(path_pdf):
    """Procesa el PDF y retorna resultados para Shiny."""
    resultados = []
    doc = fitz.open(path_pdf)
    
    for i, page in enumerate(doc):
        pagina_resultados = {
            "numero": i + 1,
            "texto_directo": "",
            "ocr": [],
            "tablas": []
        }
        
        # Texto directo
        texto = extraer_texto_directo(page)
        if texto.strip():
            pagina_resultados["texto_directo"] = texto.strip()

        # OCR desde imágenes
        resultados_ocr = extraer_imagenes_y_ocr(page, doc, i * 1000)
        for idx, texto_ocr in resultados_ocr:
            pagina_resultados["ocr"].append(f"OCR #{idx}: {texto_ocr}")

        # Tablas
        tablas = extraer_tablas_pdfplumber(path_pdf, i)
        for j, tabla in enumerate(tablas):
            pagina_resultados["tablas"].append(f"Tabla #{j+1}:\n{tabla}")
        
        resultados.append(pagina_resultados)
    
    doc.close()
    return resultados

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.tags.style("""
            .area-subida {
                border: 2px solid #fdfdfd; 
                border-radius: 8px;
                padding: 20px;
                background-color: #f8f9fa;
                text-align: center;
                margin: 15px 0;
            }
            .area-subida:hover {
                background-color: #fff3cd;
            }
        """),
        
        ui.div(
            ui.h4("Subir PDF"),
            ui.input_file("archivo", "Haz clic para seleccionar archivo PDF", accept=[".pdf"]),
            class_="area-subida"
        ),
        
        ui.output_text("estado"),
        title="Opciones",
        width=400
    ),
    ui.h2("Extractor de Texto de PDF"),
    ui.output_ui("resultados")
)

def server(input, output, session):
    @output
    @render.text
    def estado():
        if input.archivo() is None:
            return "Esperando archivo PDF..."
        else:
            return f"Procesando: {input.archivo()[0]['name']}"
    
    @reactive.Calc
    def resultados_pdf():
        if input.archivo() is None:
            return None
        
        archivo_info = input.archivo()[0]
        archivo_path = archivo_info["datapath"]
        
        # Procesar el PDF
        resultados = procesar_pdf_shiny(archivo_path)
        return resultados
    
    @output
    @render.ui
    def resultados():
        if input.archivo() is None:
            return ui.p("Por favor, sube un archivo PDF para comenzar.")
        
        resultados = resultados_pdf()
        if not resultados:
            return ui.p("No se pudieron extraer resultados del PDF.")
        
        # Mostrar resultados
        contenido = []
        for pagina in resultados:
            contenido.append(ui.h3(f"Página {pagina['numero']}"))
            
            if pagina['texto_directo']:
                contenido.append(ui.h4("Texto extraído directamente"))
                contenido.append(ui.pre(pagina['texto_directo']))
            
            if pagina['ocr']:
                contenido.append(ui.h4("Texto desde imágenes (OCR)"))
                for ocr_item in pagina['ocr']:
                    contenido.append(ui.pre(ocr_item))
            
            if pagina['tablas']:
                contenido.append(ui.h4("Tablas detectadas"))
                for tabla in pagina['tablas']:
                    contenido.append(ui.pre(tabla))
            
            contenido.append(ui.hr())
        
        return ui.div(*contenido)

# Crear la aplicación Shiny
app = App(app_ui, server)
