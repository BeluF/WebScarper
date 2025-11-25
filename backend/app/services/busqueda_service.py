"""
Servicio para búsqueda automática de recetas.

Maneja búsquedas en masa en múltiples sitios de recetas,
con soporte para búsqueda paralela o secuencial según el límite.
"""

import asyncio
import uuid
import time
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.models import Receta
from app.scraper.scraper_factory import ScraperFactory


# Almacén en memoria para el estado de las búsquedas activas
_busquedas_activas: Dict[str, dict] = {}


class BusquedaService:
    """
    Servicio que maneja búsquedas automáticas de recetas en múltiples sitios.
    
    Soporta búsqueda paralela (para límites bajos, más rápida) y 
    secuencial (para límites altos, más segura contra bloqueos).
    """
    
    # Umbral para decidir entre búsqueda paralela o secuencial
    UMBRAL_PARALELO = 50
    # Máximo de sitios a buscar en paralelo
    MAX_PARALELO = 3
    # Delay entre sitios en búsqueda secuencial (segundos)
    DELAY_SECUENCIAL = 3.0
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio con una sesión de base de datos.
        
        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db
    
    def iniciar_busqueda_automatica(
        self,
        palabra_clave: Optional[str],
        filtros: dict,
        sitios: List[str],
        limite: int = 500
    ) -> str:
        """
        Inicia una búsqueda automática en los sitios seleccionados.
        
        Crea un ID de búsqueda único y configura el estado inicial.
        La búsqueda se ejecutará en segundo plano.
        
        Args:
            palabra_clave: Texto a buscar (opcional).
            filtros: Filtros dietéticos {"sin_tacc": bool, "vegetariana": bool, "vegana": bool}.
            sitios: Lista de nombres de sitios o ["todos"].
            limite: Límite máximo de recetas (default 500).
            
        Returns:
            ID único de la búsqueda para seguimiento.
        """
        busqueda_id = str(uuid.uuid4())
        
        # Obtener lista de sitios a buscar
        sitios_disponibles = ScraperFactory.obtener_sitios_soportados()
        
        if "todos" in sitios:
            sitios_a_buscar = [s["nombre"] for s in sitios_disponibles]
        else:
            sitios_a_buscar = [s for s in sitios if s in [sd["nombre"] for sd in sitios_disponibles]]
        
        if not sitios_a_buscar:
            sitios_a_buscar = [s["nombre"] for s in sitios_disponibles]
        
        # Calcular límite por sitio
        limite_por_sitio = max(1, limite // len(sitios_a_buscar))
        
        # Determinar tipo de búsqueda
        tipo_busqueda = "paralelo" if limite <= self.UMBRAL_PARALELO else "secuencial"
        
        # Inicializar estado de la búsqueda
        _busquedas_activas[busqueda_id] = {
            "busqueda_id": busqueda_id,
            "estado": "en_progreso",
            "tipo_busqueda": tipo_busqueda,
            "palabra_clave": palabra_clave,
            "filtros": filtros,
            "limite": limite,
            "limite_por_sitio": limite_por_sitio,
            "progreso_porcentaje": 0,
            "sitios": {
                nombre: {
                    "nombre": nombre,
                    "estado": "pendiente",
                    "encontradas": 0,
                    "nuevas": 0,
                    "duplicadas": 0,
                    "error_mensaje": None
                }
                for nombre in sitios_a_buscar
            },
            "total_encontradas": 0,
            "total_nuevas": 0,
            "total_duplicadas": 0,
            "errores": [],
            "tiempo_inicio": time.time(),
            "tiempo_transcurrido": 0,
            "cancelado": False
        }
        
        return busqueda_id
    
    def obtener_tipo_busqueda(self, busqueda_id: str) -> str:
        """
        Obtiene el tipo de búsqueda (paralelo o secuencial).
        
        Args:
            busqueda_id: ID de la búsqueda.
            
        Returns:
            'paralelo' o 'secuencial'.
        """
        if busqueda_id in _busquedas_activas:
            return _busquedas_activas[busqueda_id].get("tipo_busqueda", "secuencial")
        return "secuencial"
    
    async def ejecutar_busqueda(self, busqueda_id: str):
        """
        Ejecuta la búsqueda en segundo plano.
        
        Selecciona automáticamente entre búsqueda paralela o secuencial
        según el límite configurado.
        
        Args:
            busqueda_id: ID de la búsqueda a ejecutar.
        """
        if busqueda_id not in _busquedas_activas:
            return
        
        estado = _busquedas_activas[busqueda_id]
        
        try:
            if estado["tipo_busqueda"] == "paralelo":
                await self._busqueda_paralela(busqueda_id)
            else:
                await self._busqueda_secuencial(busqueda_id)
            
            # Marcar como completado si no fue cancelado
            if not estado.get("cancelado", False):
                estado["estado"] = "completado"
                estado["progreso_porcentaje"] = 100
        except Exception as e:
            estado["estado"] = "error"
            estado["errores"].append(f"Error general: {str(e)}")
        finally:
            estado["tiempo_transcurrido"] = time.time() - estado["tiempo_inicio"]
    
    async def _busqueda_paralela(self, busqueda_id: str):
        """
        Ejecuta búsqueda en paralelo (para límites bajos).
        
        Busca en varios sitios simultáneamente, con un máximo de
        MAX_PARALELO sitios a la vez para evitar sobrecarga.
        
        Args:
            busqueda_id: ID de la búsqueda.
        """
        estado = _busquedas_activas[busqueda_id]
        sitios = list(estado["sitios"].keys())
        
        # Procesar en lotes de MAX_PARALELO sitios
        for i in range(0, len(sitios), self.MAX_PARALELO):
            if estado.get("cancelado", False):
                break
                
            lote = sitios[i:i + self.MAX_PARALELO]
            tareas = [
                self._buscar_en_sitio(busqueda_id, sitio)
                for sitio in lote
            ]
            await asyncio.gather(*tareas)
            
            # Actualizar progreso
            completados = sum(
                1 for s in estado["sitios"].values() 
                if s["estado"] in ["completado", "error"]
            )
            estado["progreso_porcentaje"] = int((completados / len(sitios)) * 100)
    
    async def _busqueda_secuencial(self, busqueda_id: str):
        """
        Ejecuta búsqueda secuencial (para límites altos).
        
        Busca sitio por sitio con delays entre cada uno para
        evitar bloqueos por rate limiting.
        
        Args:
            busqueda_id: ID de la búsqueda.
        """
        estado = _busquedas_activas[busqueda_id]
        sitios = list(estado["sitios"].keys())
        
        for idx, sitio in enumerate(sitios):
            if estado.get("cancelado", False):
                break
                
            await self._buscar_en_sitio(busqueda_id, sitio)
            
            # Actualizar progreso
            estado["progreso_porcentaje"] = int(((idx + 1) / len(sitios)) * 100)
            
            # Delay entre sitios (excepto el último)
            if idx < len(sitios) - 1:
                await asyncio.sleep(self.DELAY_SECUENCIAL)
    
    async def _buscar_en_sitio(self, busqueda_id: str, nombre_sitio: str):
        """
        Busca recetas en un sitio específico.
        
        Obtiene el scraper adecuado, realiza la búsqueda,
        y guarda las recetas nuevas verificando duplicados.
        
        Args:
            busqueda_id: ID de la búsqueda.
            nombre_sitio: Nombre del sitio a buscar.
        """
        estado = _busquedas_activas[busqueda_id]
        estado_sitio = estado["sitios"][nombre_sitio]
        
        # Marcar como en progreso
        estado_sitio["estado"] = "en_progreso"
        
        try:
            # Obtener el scraper para este sitio
            scraper = self._obtener_scraper_por_nombre(nombre_sitio)
            if not scraper:
                estado_sitio["estado"] = "error"
                estado_sitio["error_mensaje"] = "Scraper no encontrado"
                return
            
            # Buscar recetas
            recetas_encontradas = await scraper.buscar_recetas(
                palabra_clave=estado["palabra_clave"],
                filtros=estado["filtros"],
                limite=estado["limite_por_sitio"]
            )
            
            estado_sitio["encontradas"] = len(recetas_encontradas)
            estado["total_encontradas"] += len(recetas_encontradas)
            
            # Procesar cada receta encontrada
            for receta_data in recetas_encontradas:
                if estado.get("cancelado", False):
                    break
                    
                url = receta_data.get("url", "")
                if not url:
                    continue
                
                # Verificar duplicado
                if self._verificar_duplicado(url):
                    estado_sitio["duplicadas"] += 1
                    estado["total_duplicadas"] += 1
                else:
                    # Intentar scrapear y guardar la receta completa
                    try:
                        await self._scrapear_y_guardar_receta(scraper, url)
                        estado_sitio["nuevas"] += 1
                        estado["total_nuevas"] += 1
                    except Exception as e:
                        # Si falla el scraping individual, continuar con las demás
                        pass
            
            estado_sitio["estado"] = "completado"
            
        except Exception as e:
            estado_sitio["estado"] = "error"
            estado_sitio["error_mensaje"] = str(e)
            estado["errores"].append(f"{nombre_sitio}: {str(e)}")
    
    def _obtener_scraper_por_nombre(self, nombre_sitio: str):
        """
        Obtiene un scraper por nombre de sitio.
        
        Args:
            nombre_sitio: Nombre del sitio (ej: "Cookpad").
            
        Returns:
            Instancia del scraper o None si no se encuentra.
        """
        sitios = ScraperFactory.obtener_sitios_soportados()
        for sitio in sitios:
            if sitio["nombre"] == nombre_sitio:
                # Crear una URL ficticia para obtener el scraper
                dominio = sitio["dominios"][0] if sitio.get("dominios") else ""
                if dominio:
                    url_ficticia = f"https://{dominio}/"
                    return ScraperFactory.obtener_scraper(url_ficticia)
        return None
    
    def _verificar_duplicado(self, url: str) -> bool:
        """
        Verifica si una receta ya existe en la base de datos.
        
        Args:
            url: URL de origen de la receta.
            
        Returns:
            True si la receta ya existe, False si es nueva.
        """
        existente = self.db.query(Receta).filter(Receta.url_origen == url).first()
        return existente is not None
    
    async def _scrapear_y_guardar_receta(self, scraper, url: str):
        """
        Scrapea una receta completa y la guarda en la base de datos.
        
        Args:
            scraper: Instancia del scraper a usar.
            url: URL de la receta a scrapear.
            
        Raises:
            Exception: Si hay error durante el scraping o guardado.
        """
        # Scrapear la receta completa
        datos = await scraper.scrapear(url)
        
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
    
    def obtener_progreso(self, busqueda_id: str) -> Optional[dict]:
        """
        Obtiene el progreso actual de una búsqueda.
        
        Args:
            busqueda_id: ID de la búsqueda.
            
        Returns:
            Diccionario con el estado de progreso o None si no existe.
        """
        if busqueda_id not in _busquedas_activas:
            return None
        
        estado = _busquedas_activas[busqueda_id]
        
        # Actualizar tiempo transcurrido
        if estado["estado"] == "en_progreso":
            estado["tiempo_transcurrido"] = time.time() - estado["tiempo_inicio"]
        
        return {
            "busqueda_id": estado["busqueda_id"],
            "estado": estado["estado"],
            "progreso_porcentaje": estado["progreso_porcentaje"],
            "sitios": list(estado["sitios"].values()),
            "total_encontradas": estado["total_encontradas"],
            "total_nuevas": estado["total_nuevas"],
            "total_duplicadas": estado["total_duplicadas"],
            "errores": estado["errores"],
            "tiempo_transcurrido": estado["tiempo_transcurrido"]
        }
    
    def obtener_resultado(self, busqueda_id: str) -> Optional[dict]:
        """
        Obtiene el resultado final de una búsqueda completada.
        
        Args:
            busqueda_id: ID de la búsqueda.
            
        Returns:
            Diccionario con el resultado final o None si no existe.
        """
        if busqueda_id not in _busquedas_activas:
            return None
        
        estado = _busquedas_activas[busqueda_id]
        
        return {
            "busqueda_id": estado["busqueda_id"],
            "estado": estado["estado"],
            "total_encontradas": estado["total_encontradas"],
            "total_nuevas": estado["total_nuevas"],
            "total_duplicadas": estado["total_duplicadas"],
            "sitios": list(estado["sitios"].values()),
            "errores": estado["errores"],
            "tiempo_total": estado["tiempo_transcurrido"]
        }
    
    def cancelar_busqueda(self, busqueda_id: str) -> bool:
        """
        Cancela una búsqueda en progreso.
        
        Args:
            busqueda_id: ID de la búsqueda a cancelar.
            
        Returns:
            True si se canceló, False si no existe o ya terminó.
        """
        if busqueda_id not in _busquedas_activas:
            return False
        
        estado = _busquedas_activas[busqueda_id]
        
        if estado["estado"] != "en_progreso":
            return False
        
        estado["cancelado"] = True
        estado["estado"] = "cancelado"
        return True
    
    def limpiar_busqueda(self, busqueda_id: str) -> bool:
        """
        Elimina una búsqueda del almacén en memoria.
        
        Args:
            busqueda_id: ID de la búsqueda a limpiar.
            
        Returns:
            True si se eliminó, False si no existía.
        """
        if busqueda_id in _busquedas_activas:
            del _busquedas_activas[busqueda_id]
            return True
        return False
