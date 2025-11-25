"""
Schemas Pydantic para validación de datos.

Define los esquemas de entrada y salida para la API REST.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field


class RecetaBase(BaseModel):
    """Schema base con campos comunes de una receta."""
    
    titulo: str = Field(..., min_length=1, max_length=300, description="Título de la receta")
    descripcion: Optional[str] = Field(None, description="Descripción de la receta")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen")
    ingredientes: List[str] = Field(default_factory=list, description="Lista de ingredientes")
    pasos: List[str] = Field(default_factory=list, description="Pasos de preparación")
    tiempo_preparacion: Optional[str] = Field(None, description="Tiempo de preparación")
    tiempo_coccion: Optional[str] = Field(None, description="Tiempo de cocción")
    porciones: Optional[str] = Field(None, description="Número de porciones")
    es_sin_tacc: bool = Field(False, description="Es apta para celíacos")
    es_vegetariana: bool = Field(False, description="Es vegetariana")
    es_vegana: bool = Field(False, description="Es vegana")
    notas_personales: Optional[str] = Field(None, description="Notas del usuario")


class RecetaCrear(BaseModel):
    """Schema para crear una receta mediante scraping."""
    
    url: HttpUrl = Field(..., description="URL de la receta a scrapear")


class RecetaActualizar(BaseModel):
    """Schema para actualizar una receta existente."""
    
    titulo: Optional[str] = Field(None, min_length=1, max_length=300)
    descripcion: Optional[str] = None
    ingredientes: Optional[List[str]] = None
    pasos: Optional[List[str]] = None
    tiempo_preparacion: Optional[str] = None
    tiempo_coccion: Optional[str] = None
    porciones: Optional[str] = None
    es_sin_tacc: Optional[bool] = None
    es_vegetariana: Optional[bool] = None
    es_vegana: Optional[bool] = None
    notas_personales: Optional[str] = None


class RecetaRespuesta(RecetaBase):
    """Schema de respuesta con todos los campos de una receta."""
    
    id: int
    url_origen: str
    sitio_origen: str
    fecha_agregada: datetime
    fecha_actualizada: datetime
    
    class Config:
        from_attributes = True


class RecetaListaRespuesta(BaseModel):
    """Schema para respuesta de lista de recetas con paginación."""
    
    total: int = Field(..., description="Total de recetas")
    recetas: List[RecetaRespuesta] = Field(..., description="Lista de recetas")


class ScrapingRespuesta(BaseModel):
    """Schema de respuesta del proceso de scraping."""
    
    exito: bool = Field(..., description="Indica si el scraping fue exitoso")
    mensaje: str = Field(..., description="Mensaje descriptivo")
    receta: Optional[RecetaRespuesta] = Field(None, description="Receta scrapeada")


class PDFMultipleRequest(BaseModel):
    """Schema para solicitud de PDF con múltiples recetas."""
    
    ids: List[int] = Field(..., min_length=1, description="Lista de IDs de recetas")


class HealthCheck(BaseModel):
    """Schema para respuesta de health check."""
    
    status: str = Field(..., description="Estado del servicio")
    version: str = Field(..., description="Versión de la API")


# ============================================
# Schemas para Búsqueda Automática de Recetas
# ============================================

class FiltrosDieteticos(BaseModel):
    """Filtros dietéticos para la búsqueda automática."""
    
    sin_tacc: bool = Field(False, description="Filtrar recetas sin TACC")
    vegetariana: bool = Field(False, description="Filtrar recetas vegetarianas")
    vegana: bool = Field(False, description="Filtrar recetas veganas")


class BusquedaRequest(BaseModel):
    """Schema para iniciar una búsqueda automática de recetas."""
    
    palabra_clave: Optional[str] = Field(
        None, 
        description="Palabra clave a buscar (opcional, vacío busca todas)"
    )
    filtros: FiltrosDieteticos = Field(
        default_factory=FiltrosDieteticos,
        description="Filtros dietéticos a aplicar"
    )
    sitios: List[str] = Field(
        default=["todos"],
        description="Lista de sitios donde buscar o ['todos']"
    )
    limite: int = Field(
        default=500,
        ge=1,
        le=1000,
        description="Límite de recetas a buscar (default 500)"
    )


class BusquedaIniciadaResponse(BaseModel):
    """Respuesta al iniciar una búsqueda automática."""
    
    busqueda_id: str = Field(..., description="ID único de la búsqueda")
    mensaje: str = Field(..., description="Mensaje informativo")
    tipo_busqueda: str = Field(..., description="'paralelo' o 'secuencial'")


class EstadoSitio(BaseModel):
    """Estado de búsqueda para un sitio específico."""
    
    nombre: str = Field(..., description="Nombre del sitio")
    estado: str = Field(..., description="pendiente, en_progreso, completado, error")
    encontradas: int = Field(0, description="Total de recetas encontradas")
    nuevas: int = Field(0, description="Recetas nuevas guardadas")
    duplicadas: int = Field(0, description="Recetas duplicadas omitidas")
    error_mensaje: Optional[str] = Field(None, description="Mensaje de error si falló")


class BusquedaProgreso(BaseModel):
    """Estado de progreso de una búsqueda en curso."""
    
    busqueda_id: str = Field(..., description="ID de la búsqueda")
    estado: str = Field(..., description="en_progreso, completado, error, cancelado")
    progreso_porcentaje: int = Field(0, description="Porcentaje de progreso (0-100)")
    sitios: List[EstadoSitio] = Field(default_factory=list, description="Estado por sitio")
    total_encontradas: int = Field(0, description="Total de recetas encontradas")
    total_nuevas: int = Field(0, description="Total de recetas nuevas guardadas")
    total_duplicadas: int = Field(0, description="Total de recetas duplicadas")
    errores: List[str] = Field(default_factory=list, description="Lista de errores")
    tiempo_transcurrido: Optional[float] = Field(None, description="Tiempo en segundos")


class BusquedaResultado(BaseModel):
    """Resultado final de una búsqueda completada."""
    
    busqueda_id: str = Field(..., description="ID de la búsqueda")
    estado: str = Field(..., description="completado, error, cancelado")
    total_encontradas: int = Field(0, description="Total de recetas encontradas")
    total_nuevas: int = Field(0, description="Total de recetas nuevas guardadas")
    total_duplicadas: int = Field(0, description="Total de recetas duplicadas")
    sitios: List[EstadoSitio] = Field(default_factory=list, description="Resumen por sitio")
    errores: List[str] = Field(default_factory=list, description="Errores durante la búsqueda")
    tiempo_total: float = Field(0, description="Tiempo total en segundos")
