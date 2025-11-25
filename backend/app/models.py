"""
Modelos de base de datos para el sistema de recetario.

Define la estructura de la tabla de recetas usando SQLAlchemy ORM.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON

from app.database import Base


class Receta(Base):
    """
    Modelo de Receta para almacenar información scrapeada de sitios de cocina.
    
    Attributes:
        id: Identificador único de la receta.
        url_origen: URL original de donde se scrapeó la receta.
        sitio_origen: Nombre del sitio web de origen.
        titulo: Título de la receta.
        descripcion: Descripción opcional de la receta.
        imagen_url: URL de la imagen principal de la receta.
        ingredientes: Lista de ingredientes en formato JSON.
        pasos: Lista de pasos de preparación en formato JSON.
        tiempo_preparacion: Tiempo de preparación de la receta.
        tiempo_coccion: Tiempo de cocción de la receta.
        porciones: Número de porciones que rinde la receta.
        es_sin_tacc: Indica si la receta es apta para celíacos.
        es_vegetariana: Indica si la receta es vegetariana.
        es_vegana: Indica si la receta es vegana.
        notas_personales: Notas agregadas por el usuario.
        fecha_agregada: Fecha y hora en que se agregó la receta.
        fecha_actualizada: Fecha y hora de la última actualización.
    """
    
    __tablename__ = "recetas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url_origen = Column(String(500), unique=True, nullable=False, index=True)
    sitio_origen = Column(String(100), nullable=False)
    titulo = Column(String(300), nullable=False)
    descripcion = Column(Text, nullable=True)
    imagen_url = Column(String(500), nullable=True)
    ingredientes = Column(JSON, nullable=False, default=list)
    pasos = Column(JSON, nullable=False, default=list)
    tiempo_preparacion = Column(String(50), nullable=True)
    tiempo_coccion = Column(String(50), nullable=True)
    porciones = Column(String(50), nullable=True)
    es_sin_tacc = Column(Boolean, default=False)
    es_vegetariana = Column(Boolean, default=False)
    es_vegana = Column(Boolean, default=False)
    notas_personales = Column(Text, nullable=True)
    fecha_agregada = Column(DateTime, default=datetime.utcnow)
    fecha_actualizada = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Receta(id={self.id}, titulo='{self.titulo}')>"
