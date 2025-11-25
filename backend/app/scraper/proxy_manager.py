"""
Gestor de rotación de proxies.

Proporciona funcionalidad para rotar entre múltiples proxies
y evitar bloqueos por múltiples peticiones.
"""

import random
from typing import Optional, List
from pathlib import Path

from app.config import PROXY_ENABLED, PROXY_LIST_FILE


class ProxyManager:
    """
    Gestor de proxies para el sistema de scraping.
    
    Permite cargar una lista de proxies y rotarlos automáticamente
    entre peticiones para evitar bloqueos.
    
    Attributes:
        proxies: Lista de URLs de proxies disponibles.
        enabled: Indica si el uso de proxies está habilitado.
    """
    
    def __init__(self, proxy_file: Optional[str] = None, enabled: bool = None):
        """
        Inicializa el gestor de proxies.
        
        Args:
            proxy_file: Ruta al archivo con lista de proxies.
            enabled: Si el uso de proxies está habilitado.
        """
        self.enabled = enabled if enabled is not None else PROXY_ENABLED
        self.proxies: List[str] = []
        self._indice_actual = 0
        self._proxies_fallidos: set = set()
        
        if self.enabled:
            archivo = proxy_file or PROXY_LIST_FILE
            self._cargar_proxies(archivo)
    
    def _cargar_proxies(self, archivo: str):
        """
        Carga la lista de proxies desde un archivo.
        
        El archivo debe tener un proxy por línea en formato:
        - http://ip:puerto
        - http://usuario:contraseña@ip:puerto
        - socks5://ip:puerto
        
        Args:
            archivo: Ruta al archivo de proxies.
        """
        path = Path(archivo)
        if not path.exists():
            return
        
        try:
            with open(path, "r") as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith("#"):
                        self.proxies.append(linea)
        except Exception as e:
            print(f"Error al cargar proxies: {e}")
    
    def agregar_proxy(self, proxy: str):
        """
        Agrega un proxy a la lista.
        
        Args:
            proxy: URL del proxy a agregar.
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
    
    def remover_proxy(self, proxy: str):
        """
        Remueve un proxy de la lista.
        
        Args:
            proxy: URL del proxy a remover.
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
    
    def obtener_proxy(self) -> Optional[str]:
        """
        Obtiene el siguiente proxy disponible usando rotación round-robin.
        
        Returns:
            URL del proxy o None si no hay proxies disponibles.
        """
        if not self.enabled or not self.proxies:
            return None
        
        # Filtrar proxies que no han fallado
        proxies_disponibles = [
            p for p in self.proxies 
            if p not in self._proxies_fallidos
        ]
        
        if not proxies_disponibles:
            # Si todos fallaron, resetear y volver a intentar
            self._proxies_fallidos.clear()
            proxies_disponibles = self.proxies
        
        # Rotación round-robin
        self._indice_actual = self._indice_actual % len(proxies_disponibles)
        proxy = proxies_disponibles[self._indice_actual]
        self._indice_actual += 1
        
        return proxy
    
    def obtener_proxy_aleatorio(self) -> Optional[str]:
        """
        Obtiene un proxy aleatorio de la lista.
        
        Returns:
            URL del proxy o None si no hay proxies disponibles.
        """
        if not self.enabled or not self.proxies:
            return None
        
        proxies_disponibles = [
            p for p in self.proxies 
            if p not in self._proxies_fallidos
        ]
        
        if not proxies_disponibles:
            self._proxies_fallidos.clear()
            proxies_disponibles = self.proxies
        
        return random.choice(proxies_disponibles)
    
    def marcar_fallido(self, proxy: str):
        """
        Marca un proxy como fallido temporalmente.
        
        Args:
            proxy: URL del proxy que falló.
        """
        self._proxies_fallidos.add(proxy)
    
    def resetear_fallidos(self):
        """Resetea la lista de proxies fallidos."""
        self._proxies_fallidos.clear()
    
    @property
    def cantidad_proxies(self) -> int:
        """Retorna la cantidad de proxies disponibles."""
        return len(self.proxies)
    
    @property
    def cantidad_disponibles(self) -> int:
        """Retorna la cantidad de proxies no marcados como fallidos."""
        return len([
            p for p in self.proxies 
            if p not in self._proxies_fallidos
        ])
