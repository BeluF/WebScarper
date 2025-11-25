"""
Servicio de lógica de negocio para recetas.

Maneja las operaciones CRUD y scraping de recetas.
"""

import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Receta
from app.schemas import RecetaActualizar
from app.scraper.scraper_factory import ScraperFactory


# Configurar logger
logger = logging.getLogger(__name__)


class RecipeService:
    """
    Servicio que encapsula la lógica de negocio para recetas.
    
    Proporciona métodos para crear, leer, actualizar y eliminar recetas,
    así como para realizar scraping de nuevas recetas.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio con una sesión de base de datos.
        
        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db
    
    def obtener_todas(
        self,
        busqueda: Optional[str] = None,
        sin_tacc: Optional[bool] = None,
        vegetariana: Optional[bool] = None,
        vegana: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Receta], int]:
        """
        Obtiene todas las recetas con filtros opcionales.
        
        Args:
            busqueda: Texto a buscar en el título.
            sin_tacc: Filtrar solo recetas sin TACC.
            vegetariana: Filtrar solo recetas vegetarianas.
            vegana: Filtrar solo recetas veganas.
            skip: Número de resultados a saltar (paginación).
            limit: Máximo de resultados a retornar.
            
        Returns:
            Tuple con lista de recetas y total de resultados.
        """
        query = self.db.query(Receta)
        
        # Aplicar filtros
        if busqueda:
            query = query.filter(
                or_(
                    Receta.titulo.ilike(f"%{busqueda}%"),
                    Receta.descripcion.ilike(f"%{busqueda}%")
                )
            )
        
        if sin_tacc is not None:
            query = query.filter(Receta.es_sin_tacc == sin_tacc)
        
        if vegetariana is not None:
            query = query.filter(Receta.es_vegetariana == vegetariana)
        
        if vegana is not None:
            query = query.filter(Receta.es_vegana == vegana)
        
        # Contar total antes de paginar
        total = query.count()
        
        # Aplicar paginación y ordenar por fecha
        recetas = query.order_by(Receta.fecha_agregada.desc()).offset(skip).limit(limit).all()
        
        return recetas, total
    
    def obtener_por_id(self, receta_id: int) -> Optional[Receta]:
        """
        Obtiene una receta por su ID.
        
        Args:
            receta_id: ID de la receta.
            
        Returns:
            Receta encontrada o None.
        """
        return self.db.query(Receta).filter(Receta.id == receta_id).first()
    
    def obtener_por_url(self, url: str) -> Optional[Receta]:
        """
        Obtiene una receta por su URL de origen.
        
        Args:
            url: URL de la receta.
            
        Returns:
            Receta encontrada o None.
        """
        return self.db.query(Receta).filter(Receta.url_origen == url).first()
    
    async def scrapear_y_guardar(self, url: str) -> Receta:
        """
        Scrapea una receta desde una URL y la guarda en la base de datos.
        
        Args:
            url: URL de la receta a scrapear.
            
        Returns:
            Receta guardada en la base de datos.
            
        Raises:
            ValueError: Si la URL no está soportada, ya existe, o la receta no es válida.
            Exception: Si hay error durante el scraping.
        """
        # Verificar si la URL ya existe
        existente = self.obtener_por_url(str(url))
        if existente:
            raise ValueError(f"Ya existe una receta con esta URL (ID: {existente.id})")
        
        # Obtener el scraper adecuado
        scraper = ScraperFactory.obtener_scraper(str(url))
        if not scraper:
            sitios = ScraperFactory.obtener_sitios_soportados()
            nombres = ", ".join([s["nombre"] for s in sitios])
            raise ValueError(f"URL no soportada. Sitios soportados: {nombres}")
        
        # Realizar el scraping
        datos = await scraper.scrapear(str(url))
        
        # Validar que la receta tenga contenido mínimo
        es_valida, mensaje_error = datos.validar()
        if not es_valida:
            logger.warning(f"Receta rechazada (vacía): {url} - {mensaje_error}")
            raise ValueError(f"La receta no tiene contenido válido: {mensaje_error}")
        
        # Validar idioma - rechazar recetas en inglés
        idioma = datos.detectar_idioma()
        if idioma == "en":
            logger.warning(f"Receta rechazada (en inglés): {url}")
            raise ValueError("La receta está en inglés. Solo se aceptan recetas en español.")
        
        # Crear la receta en la base de datos
        receta = Receta(
            url_origen=datos.url_origen,
            sitio_origen=datos.sitio_origen,
            titulo=datos.titulo,
            descripcion=datos.descripcion,
            imagen_url=datos.imagen_url,
            ingredientes=datos.ingredientes,
            pasos=datos.pasos,
            tiempo_preparacion=datos.tiempo_preparacion,
            tiempo_coccion=datos.tiempo_coccion,
            porciones=datos.porciones
        )
        
        self.db.add(receta)
        self.db.commit()
        self.db.refresh(receta)
        
        return receta
    
    def actualizar(self, receta_id: int, datos: RecetaActualizar) -> Optional[Receta]:
        """
        Actualiza una receta existente.
        
        Args:
            receta_id: ID de la receta a actualizar.
            datos: Datos a actualizar.
            
        Returns:
            Receta actualizada o None si no existe.
        """
        receta = self.obtener_por_id(receta_id)
        if not receta:
            return None
        
        # Actualizar solo los campos proporcionados
        datos_dict = datos.model_dump(exclude_unset=True)
        for campo, valor in datos_dict.items():
            setattr(receta, campo, valor)
        
        self.db.commit()
        self.db.refresh(receta)
        
        return receta
    
    def eliminar(self, receta_id: int) -> bool:
        """
        Elimina una receta.
        
        Args:
            receta_id: ID de la receta a eliminar.
            
        Returns:
            True si se eliminó, False si no existía.
        """
        receta = self.obtener_por_id(receta_id)
        if not receta:
            return False
        
        self.db.delete(receta)
        self.db.commit()
        
        return True
    
    def obtener_multiples(self, ids: List[int]) -> List[Receta]:
        """
        Obtiene múltiples recetas por sus IDs.
        
        Args:
            ids: Lista de IDs de recetas.
            
        Returns:
            Lista de recetas encontradas.
        """
        return self.db.query(Receta).filter(Receta.id.in_(ids)).all()
