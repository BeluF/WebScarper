/**
 * Tipos TypeScript para el sistema de recetario.
 */

/** Representa una receta del sistema */
export interface Receta {
  id: number;
  url_origen: string;
  sitio_origen: string;
  titulo: string;
  descripcion: string | null;
  imagen_url: string | null;
  ingredientes: string[];
  pasos: string[];
  tiempo_preparacion: string | null;
  tiempo_coccion: string | null;
  porciones: string | null;
  es_sin_tacc: boolean;
  es_vegetariana: boolean;
  es_vegana: boolean;
  notas_personales: string | null;
  fecha_agregada: string;
  fecha_actualizada: string;
}

/** Respuesta de lista de recetas */
export interface RecetaListaRespuesta {
  total: number;
  recetas: Receta[];
}

/** Respuesta del proceso de scraping */
export interface ScrapingRespuesta {
  exito: boolean;
  mensaje: string;
  receta: Receta | null;
}

/** Datos para actualizar una receta */
export interface RecetaActualizar {
  titulo?: string;
  descripcion?: string;
  ingredientes?: string[];
  pasos?: string[];
  tiempo_preparacion?: string;
  tiempo_coccion?: string;
  porciones?: string;
  es_sin_tacc?: boolean;
  es_vegetariana?: boolean;
  es_vegana?: boolean;
  notas_personales?: string;
}

/** Filtros para buscar recetas */
export interface FiltrosReceta {
  busqueda?: string;
  sin_tacc?: boolean;
  vegetariana?: boolean;
  vegana?: boolean;
}

/** Sitio web soportado para scraping */
export interface SitioSoportado {
  nombre: string;
  dominios: string[];
}

/** Respuesta del health check */
export interface HealthCheck {
  status: string;
  version: string;
}

// ============================================
// Tipos para Búsqueda Automática de Recetas
// ============================================

/** Filtros dietéticos para búsqueda automática */
export interface FiltrosDieteticos {
  sin_tacc: boolean;
  vegetariana: boolean;
  vegana: boolean;
}

/** Request para iniciar búsqueda automática */
export interface BusquedaRequest {
  palabra_clave?: string | null;
  filtros: FiltrosDieteticos;
  sitios: string[];
  limite: number;
}

/** Respuesta al iniciar una búsqueda */
export interface BusquedaIniciadaResponse {
  busqueda_id: string;
  mensaje: string;
  tipo_busqueda: 'paralelo' | 'secuencial';
}

/** Estado de búsqueda para un sitio */
export interface EstadoSitio {
  nombre: string;
  estado: 'pendiente' | 'en_progreso' | 'completado' | 'error';
  encontradas: number;
  nuevas: number;
  duplicadas: number;
  descartadas_vacias?: number;
  descartadas_idioma?: number;
  error_mensaje?: string | null;
}

/** Progreso de una búsqueda en curso */
export interface BusquedaProgreso {
  busqueda_id: string;
  estado: 'en_progreso' | 'completado' | 'error' | 'cancelado';
  progreso_porcentaje: number;
  sitios: EstadoSitio[];
  total_encontradas: number;
  total_nuevas: number;
  total_duplicadas: number;
  total_descartadas_vacias?: number;
  total_descartadas_idioma?: number;
  errores: string[];
  tiempo_transcurrido?: number | null;
}

/** Resultado final de una búsqueda */
export interface BusquedaResultado {
  busqueda_id: string;
  estado: 'completado' | 'error' | 'cancelado';
  total_encontradas: number;
  total_nuevas: number;
  total_duplicadas: number;
  total_descartadas_vacias?: number;
  total_descartadas_idioma?: number;
  sitios: EstadoSitio[];
  errores: string[];
  tiempo_total: number;
}
