"""
Servicio de generación de PDFs para recetas.

Genera PDFs individuales o múltiples con diseño atractivo.
"""

import os
from typing import List
from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from app.models import Receta
from app.config import PDF_TEMP_DIR


class PDFGenerator:
    """
    Generador de PDFs para recetas.
    
    Crea documentos PDF con diseño profesional incluyendo
    imagen, ingredientes y pasos de preparación.
    """
    
    # Colores del tema
    COLOR_PRIMARIO = HexColor("#2D5A27")  # Verde oscuro
    COLOR_SECUNDARIO = HexColor("#8BC34A")  # Verde claro
    COLOR_TEXTO = HexColor("#333333")
    COLOR_GRIS = HexColor("#666666")
    
    def __init__(self):
        """Inicializa el generador de PDFs."""
        # Asegurar que existe el directorio temporal
        Path(PDF_TEMP_DIR).mkdir(parents=True, exist_ok=True)
        
        # Configurar estilos
        self.estilos = getSampleStyleSheet()
        self._configurar_estilos()
    
    def _configurar_estilos(self):
        """Configura los estilos personalizados para el PDF."""
        # Título principal
        self.estilos.add(ParagraphStyle(
            name='TituloReceta',
            parent=self.estilos['Heading1'],
            fontSize=24,
            textColor=self.COLOR_PRIMARIO,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulos (secciones)
        self.estilos.add(ParagraphStyle(
            name='Seccion',
            parent=self.estilos['Heading2'],
            fontSize=16,
            textColor=self.COLOR_PRIMARIO,
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.estilos.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.estilos['Normal'],
            fontSize=11,
            textColor=self.COLOR_TEXTO,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        # Metadatos (tiempo, porciones)
        self.estilos.add(ParagraphStyle(
            name='Metadatos',
            parent=self.estilos['Normal'],
            fontSize=10,
            textColor=self.COLOR_GRIS,
            alignment=TA_CENTER,
            spaceAfter=15
        ))
        
        # Items de lista
        self.estilos.add(ParagraphStyle(
            name='ItemLista',
            parent=self.estilos['Normal'],
            fontSize=11,
            textColor=self.COLOR_TEXTO,
            leftIndent=20,
            spaceAfter=4
        ))
        
        # Origen
        self.estilos.add(ParagraphStyle(
            name='Origen',
            parent=self.estilos['Normal'],
            fontSize=9,
            textColor=self.COLOR_GRIS,
            alignment=TA_CENTER,
            spaceBefore=20
        ))
    
    def generar_pdf_individual(self, receta: Receta) -> BytesIO:
        """
        Genera un PDF para una receta individual.
        
        Args:
            receta: Receta a convertir en PDF.
            
        Returns:
            BytesIO con el contenido del PDF.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elementos = self._construir_contenido_receta(receta)
        doc.build(elementos)
        
        buffer.seek(0)
        return buffer
    
    def generar_pdf_multiple(self, recetas: List[Receta]) -> BytesIO:
        """
        Genera un PDF con múltiples recetas.
        
        Args:
            recetas: Lista de recetas a incluir.
            
        Returns:
            BytesIO con el contenido del PDF.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elementos = []
        
        # Portada
        elementos.append(Spacer(1, 8*cm))
        elementos.append(Paragraph(
            "Mi Recetario Personal",
            self.estilos['TituloReceta']
        ))
        elementos.append(Spacer(1, 1*cm))
        elementos.append(Paragraph(
            f"{len(recetas)} recetas seleccionadas",
            self.estilos['Metadatos']
        ))
        elementos.append(PageBreak())
        
        # Índice
        elementos.append(Paragraph("Índice", self.estilos['Seccion']))
        for i, receta in enumerate(recetas, 1):
            elementos.append(Paragraph(
                f"{i}. {receta.titulo}",
                self.estilos['ItemLista']
            ))
        elementos.append(PageBreak())
        
        # Cada receta
        for i, receta in enumerate(recetas):
            elementos.extend(self._construir_contenido_receta(receta))
            if i < len(recetas) - 1:
                elementos.append(PageBreak())
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer
    
    def _construir_contenido_receta(self, receta: Receta) -> List:
        """
        Construye los elementos del PDF para una receta.
        
        Args:
            receta: Receta a renderizar.
            
        Returns:
            Lista de elementos Platypus para el PDF.
        """
        elementos = []
        
        # Título
        elementos.append(Paragraph(receta.titulo, self.estilos['TituloReceta']))
        
        # Metadatos (tiempo, porciones, categorías)
        metadatos = []
        if receta.tiempo_preparacion:
            metadatos.append(f"⏱️ Prep: {receta.tiempo_preparacion}")
        if receta.tiempo_coccion:
            metadatos.append(f"🍳 Cocción: {receta.tiempo_coccion}")
        if receta.porciones:
            metadatos.append(f"👥 {receta.porciones}")
        
        categorias = []
        if receta.es_sin_tacc:
            categorias.append("🌾 Sin TACC")
        if receta.es_vegetariana:
            categorias.append("🥬 Vegetariana")
        if receta.es_vegana:
            categorias.append("🌱 Vegana")
        
        if metadatos:
            elementos.append(Paragraph(
                " | ".join(metadatos),
                self.estilos['Metadatos']
            ))
        
        if categorias:
            elementos.append(Paragraph(
                " | ".join(categorias),
                self.estilos['Metadatos']
            ))
        
        # Descripción
        if receta.descripcion:
            elementos.append(Paragraph(receta.descripcion, self.estilos['TextoNormal']))
            elementos.append(Spacer(1, 0.5*cm))
        
        # Ingredientes
        if receta.ingredientes:
            elementos.append(Paragraph("🥘 Ingredientes", self.estilos['Seccion']))
            for ingrediente in receta.ingredientes:
                elementos.append(Paragraph(
                    f"• {ingrediente}",
                    self.estilos['ItemLista']
                ))
            elementos.append(Spacer(1, 0.5*cm))
        
        # Pasos de preparación
        if receta.pasos:
            elementos.append(Paragraph("📝 Preparación", self.estilos['Seccion']))
            for i, paso in enumerate(receta.pasos, 1):
                elementos.append(Paragraph(
                    f"<b>Paso {i}:</b> {paso}",
                    self.estilos['TextoNormal']
                ))
            elementos.append(Spacer(1, 0.5*cm))
        
        # Notas personales
        if receta.notas_personales:
            elementos.append(Paragraph("📌 Notas Personales", self.estilos['Seccion']))
            elementos.append(Paragraph(
                receta.notas_personales,
                self.estilos['TextoNormal']
            ))
        
        # Origen
        elementos.append(Paragraph(
            f"Fuente: {receta.sitio_origen} - {receta.url_origen}",
            self.estilos['Origen']
        ))
        
        return elementos
