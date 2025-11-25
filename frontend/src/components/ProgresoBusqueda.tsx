import React from 'react';
import { BusquedaProgreso, EstadoSitio } from '../types/recipe';

interface ProgresoBusquedaProps {
  progreso: BusquedaProgreso;
  onCancelar: () => void;
}

/**
 * Componente que muestra el progreso de una búsqueda automática en tiempo real.
 */
const ProgresoBusqueda: React.FC<ProgresoBusquedaProps> = ({ progreso, onCancelar }) => {
  const formatTiempo = (segundos: number | null | undefined): string => {
    if (!segundos) return '0s';
    const mins = Math.floor(segundos / 60);
    const secs = Math.floor(segundos % 60);
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const getEstadoIcon = (estado: EstadoSitio['estado']): string => {
    switch (estado) {
      case 'pendiente':
        return '⏸️';
      case 'en_progreso':
        return '⏳';
      case 'completado':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '⏸️';
    }
  };

  const getEstadoColor = (estado: EstadoSitio['estado']): string => {
    switch (estado) {
      case 'pendiente':
        return 'text-gray-500';
      case 'en_progreso':
        return 'text-blue-600';
      case 'completado':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  const getEstadoTexto = (estado: EstadoSitio): string => {
    switch (estado.estado) {
      case 'pendiente':
        return 'En espera...';
      case 'en_progreso':
        return `Buscando... ${estado.encontradas} encontradas`;
      case 'completado':
        return `${estado.encontradas} recetas (${estado.nuevas} nuevas, ${estado.duplicadas} duplicadas)`;
      case 'error':
        return estado.error_mensaje || 'Error desconocido';
      default:
        return '';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="text-2xl">📊</span>
        Progreso de Búsqueda
      </h2>

      {/* Barra de progreso */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progreso general</span>
          <span>{progreso.progreso_porcentaje}% completado</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className="bg-primary-600 h-full rounded-full transition-all duration-300"
            style={{ width: `${progreso.progreso_porcentaje}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Tiempo transcurrido: {formatTiempo(progreso.tiempo_transcurrido)}
        </p>
      </div>

      {/* Lista de sitios con su estado */}
      <div className="space-y-2 mb-6 max-h-64 overflow-y-auto">
        {progreso.sitios.map((sitio) => (
          <div
            key={sitio.nombre}
            className={`flex items-center justify-between p-2 rounded ${
              sitio.estado === 'en_progreso' ? 'bg-blue-50' : 'bg-gray-50'
            }`}
          >
            <div className="flex items-center gap-2">
              <span>{getEstadoIcon(sitio.estado)}</span>
              <span className={`font-medium ${getEstadoColor(sitio.estado)}`}>
                {sitio.nombre}
              </span>
            </div>
            <span className={`text-sm ${getEstadoColor(sitio.estado)}`}>
              {getEstadoTexto(sitio)}
            </span>
          </div>
        ))}
      </div>

      {/* Resumen de estadísticas */}
      <div className="grid grid-cols-3 gap-4 p-4 bg-gray-100 rounded-lg mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            📥 {progreso.total_nuevas}
          </div>
          <div className="text-xs text-gray-600">Guardadas</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-amber-600">
            🔄 {progreso.total_duplicadas}
          </div>
          <div className="text-xs text-gray-600">Duplicadas</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">
            ❌ {progreso.errores.length}
          </div>
          <div className="text-xs text-gray-600">Errores</div>
        </div>
      </div>

      {/* Errores si los hay */}
      {progreso.errores.length > 0 && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-800 mb-1">Errores:</p>
          <ul className="text-xs text-red-700 list-disc list-inside">
            {progreso.errores.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Botón de cancelar */}
      {progreso.estado === 'en_progreso' && (
        <button
          onClick={onCancelar}
          className="w-full py-2 px-4 bg-red-100 text-red-700 font-medium rounded-lg hover:bg-red-200 transition-colors flex items-center justify-center gap-2"
        >
          <span>❌</span>
          Cancelar búsqueda
        </button>
      )}
    </div>
  );
};

export default ProgresoBusqueda;
