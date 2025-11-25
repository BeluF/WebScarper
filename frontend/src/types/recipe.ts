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
