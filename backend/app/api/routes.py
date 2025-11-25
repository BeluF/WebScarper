"""
Rutas de la API REST para el sistema de recetario.

Define todos los endpoints para gestión de recetas, scraping y exportación PDF.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import obtener_db
from app.schemas import (
    RecetaCrear, RecetaActualizar, RecetaRespuesta, 
    RecetaListaRespuesta, ScrapingRespuesta, PDFMultipleRequest, HealthCheck
)
from app.services.recipe_service import RecipeService
from app.services.pdf_generator import PDFGenerator

router = APIRouter(prefix="/api", tags=["recetas"])


@router.get("/health", response_model=HealthCheck)
def health_check():
    """
    Verifica el estado del servicio.
    
    Returns:
        Estado del servicio y versión de la API.
    """
    return HealthCheck(status="ok", version="1.0.0")


@router.get("/recetas", response_model=RecetaListaRespuesta)
def listar_recetas(
    busqueda: Optional[str] = Query(None, description="Buscar por nombre"),
    sin_tacc: Optional[bool] = Query(None, description="Filtrar sin TACC"),
    vegetariana: Optional[bool] = Query(None, description="Filtrar vegetarianas"),
    vegana: Optional[bool] = Query(None, description="Filtrar veganas"),
    skip: int = Query(0, ge=0, description="Saltar N resultados"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de resultados"),
    db: Session = Depends(obtener_db)
):
    """
    Lista todas las recetas con filtros opcionales.
    
    Args:
        busqueda: Texto a buscar en el título.
        sin_tacc: Si es True, solo muestra recetas sin TACC.
        vegetariana: Si es True, solo muestra recetas vegetarianas.
        vegana: Si es True, solo muestra recetas veganas.
        skip: Número de resultados a saltar (para paginación).
        limit: Máximo de resultados a retornar.
        db: Sesión de base de datos.
        
    Returns:
        Lista de recetas y total de resultados.
    """
    service = RecipeService(db)
    recetas, total = service.obtener_todas(
        busqueda=busqueda,
        sin_tacc=sin_tacc,
        vegetariana=vegetariana,
        vegana=vegana,
        skip=skip,
        limit=limit
    )
    
    return RecetaListaRespuesta(total=total, recetas=recetas)


@router.get("/recetas/{receta_id}", response_model=RecetaRespuesta)
def obtener_receta(receta_id: int, db: Session = Depends(obtener_db)):
    """
    Obtiene una receta por su ID.
    
    Args:
        receta_id: ID de la receta a obtener.
        db: Sesión de base de datos.
        
    Returns:
        Datos de la receta.
        
    Raises:
        HTTPException: Si la receta no existe.
    """
    service = RecipeService(db)
    receta = service.obtener_por_id(receta_id)
    
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    
    return receta


@router.post("/recetas/scrapear", response_model=ScrapingRespuesta)
async def scrapear_receta(datos: RecetaCrear, db: Session = Depends(obtener_db)):
    """
    Scrapea una nueva receta desde una URL.
    
    Args:
        datos: URL de la receta a scrapear.
        db: Sesión de base de datos.
        
    Returns:
        Resultado del scraping con la receta creada.
    """
    service = RecipeService(db)
    
    try:
        receta = await service.scrapear_y_guardar(str(datos.url))
        return ScrapingRespuesta(
            exito=True,
            mensaje="Receta scrapeada y guardada exitosamente",
            receta=receta
        )
    except ValueError as e:
        return ScrapingRespuesta(
            exito=False,
            mensaje=str(e),
            receta=None
        )
    except Exception as e:
        return ScrapingRespuesta(
            exito=False,
            mensaje=f"Error al scrapear la receta: {str(e)}",
            receta=None
        )


@router.put("/recetas/{receta_id}", response_model=RecetaRespuesta)
def actualizar_receta(
    receta_id: int, 
    datos: RecetaActualizar, 
    db: Session = Depends(obtener_db)
):
    """
    Actualiza una receta existente.
    
    Args:
        receta_id: ID de la receta a actualizar.
        datos: Campos a actualizar.
        db: Sesión de base de datos.
        
    Returns:
        Receta actualizada.
        
    Raises:
        HTTPException: Si la receta no existe.
    """
    service = RecipeService(db)
    receta = service.actualizar(receta_id, datos)
    
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    
    return receta


@router.delete("/recetas/{receta_id}")
def eliminar_receta(receta_id: int, db: Session = Depends(obtener_db)):
    """
    Elimina una receta.
    
    Args:
        receta_id: ID de la receta a eliminar.
        db: Sesión de base de datos.
        
    Returns:
        Mensaje de confirmación.
        
    Raises:
        HTTPException: Si la receta no existe.
    """
    service = RecipeService(db)
    eliminada = service.eliminar(receta_id)
    
    if not eliminada:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    
    return {"mensaje": "Receta eliminada exitosamente"}


@router.get("/recetas/{receta_id}/pdf")
def descargar_pdf(receta_id: int, db: Session = Depends(obtener_db)):
    """
    Genera y descarga una receta como PDF.
    
    Args:
        receta_id: ID de la receta.
        db: Sesión de base de datos.
        
    Returns:
        Archivo PDF de la receta.
        
    Raises:
        HTTPException: Si la receta no existe.
    """
    service = RecipeService(db)
    receta = service.obtener_por_id(receta_id)
    
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    
    generador = PDFGenerator()
    pdf_buffer = generador.generar_pdf_individual(receta)
    
    # Limpiar el título para el nombre del archivo
    nombre_archivo = receta.titulo.replace(" ", "_")[:50]
    nombre_archivo = "".join(c for c in nombre_archivo if c.isalnum() or c == "_")
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre_archivo}.pdf"'
        }
    )


@router.post("/recetas/pdf-multiple")
def descargar_pdf_multiple(
    datos: PDFMultipleRequest, 
    db: Session = Depends(obtener_db)
):
    """
    Genera y descarga múltiples recetas como un solo PDF.
    
    Args:
        datos: Lista de IDs de recetas.
        db: Sesión de base de datos.
        
    Returns:
        Archivo PDF con todas las recetas.
        
    Raises:
        HTTPException: Si no se encuentran recetas.
    """
    service = RecipeService(db)
    recetas = service.obtener_multiples(datos.ids)
    
    if not recetas:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron recetas con los IDs proporcionados"
        )
    
    generador = PDFGenerator()
    pdf_buffer = generador.generar_pdf_multiple(recetas)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="mi_recetario.pdf"'
        }
    )


@router.get("/sitios-soportados")
def obtener_sitios_soportados():
    """
    Obtiene la lista de sitios web soportados para scraping.
    
    Returns:
        Lista de sitios con sus dominios.
    """
    from app.scraper.scraper_factory import ScraperFactory
    return {"sitios": ScraperFactory.obtener_sitios_soportados()}
