/**
 * Cliente API con Axios para comunicación con el backend.
 */

import axios from 'axios';
import { 
  Receta, 
  RecetaListaRespuesta, 
  ScrapingRespuesta, 
  RecetaActualizar,
  FiltrosReceta,
  SitioSoportado,
  HealthCheck
} from '../types/recipe';

// Configurar la URL base de la API
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Verifica el estado del servicio backend.
 */
export async function verificarHealth(): Promise<HealthCheck> {
  const response = await api.get<HealthCheck>('/health');
  return response.data;
}

/**
 * Obtiene todas las recetas con filtros opcionales.
 */
export async function obtenerRecetas(filtros?: FiltrosReceta): Promise<RecetaListaRespuesta> {
  const params = new URLSearchParams();
  
  if (filtros?.busqueda) {
    params.append('busqueda', filtros.busqueda);
  }
  if (filtros?.sin_tacc !== undefined) {
    params.append('sin_tacc', String(filtros.sin_tacc));
  }
  if (filtros?.vegetariana !== undefined) {
    params.append('vegetariana', String(filtros.vegetariana));
  }
  if (filtros?.vegana !== undefined) {
    params.append('vegana', String(filtros.vegana));
  }
  
  const response = await api.get<RecetaListaRespuesta>(`/recetas?${params.toString()}`);
  return response.data;
}

/**
 * Obtiene una receta por su ID.
 */
export async function obtenerReceta(id: number): Promise<Receta> {
  const response = await api.get<Receta>(`/recetas/${id}`);
  return response.data;
}

/**
 * Scrapea una nueva receta desde una URL.
 */
export async function scrapearReceta(url: string): Promise<ScrapingRespuesta> {
  const response = await api.post<ScrapingRespuesta>('/recetas/scrapear', { url });
  return response.data;
}

/**
 * Actualiza una receta existente.
 */
export async function actualizarReceta(id: number, datos: RecetaActualizar): Promise<Receta> {
  const response = await api.put<Receta>(`/recetas/${id}`, datos);
  return response.data;
}

/**
 * Elimina una receta.
 */
export async function eliminarReceta(id: number): Promise<void> {
  await api.delete(`/recetas/${id}`);
}

/**
 * Descarga una receta como PDF.
 */
export async function descargarPDF(id: number): Promise<Blob> {
  const response = await api.get(`/recetas/${id}/pdf`, {
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Descarga múltiples recetas como PDF.
 */
export async function descargarPDFMultiple(ids: number[]): Promise<Blob> {
  const response = await api.post('/recetas/pdf-multiple', { ids }, {
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Obtiene la lista de sitios soportados para scraping.
 */
export async function obtenerSitiosSoportados(): Promise<SitioSoportado[]> {
  const response = await api.get<{ sitios: SitioSoportado[] }>('/sitios-soportados');
  return response.data.sitios;
}

/**
 * Descarga un blob como archivo.
 */
export function descargarArchivo(blob: Blob, nombreArchivo: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = nombreArchivo;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
