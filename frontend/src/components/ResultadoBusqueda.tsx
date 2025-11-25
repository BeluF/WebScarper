import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BusquedaResultado } from '../types/recipe';

interface ResultadoBusquedaProps {
  resultado: BusquedaResultado;
  onNuevaBusqueda: () => void;
}

/**
 * Componente que muestra el resultado final de una búsqueda automática.
 */
const ResultadoBusqueda: React.FC<ResultadoBusquedaProps> = ({ resultado, onNuevaBusqueda }) => {
  const navigate = useNavigate();

  const formatTiempo = (segundos: number): string => {
    const mins = Math.floor(segundos / 60);
    const secs = Math.floor(segundos % 60);
    if (mins > 0) {
      return `${mins} minuto${mins !== 1 ? 's' : ''} ${secs} segundo${secs !== 1 ? 's' : ''}`;
    }
    return `${secs} segundo${secs !== 1 ? 's' : ''}`;
  };

  const getEstadoIcon = (): { icon: string; color: string; texto: string } => {
    switch (resultado.estado) {
      case 'completado':
        return { icon: '✅', color: 'text-green-600', texto: 'Búsqueda Completada' };
      case 'cancelado':
        return { icon: '⏹️', color: 'text-amber-600', texto: 'Búsqueda Cancelada' };
      case 'error':
        return { icon: '❌', color: 'text-red-600', texto: 'Búsqueda con Errores' };
      default:
        return { icon: '❓', color: 'text-gray-600', texto: 'Estado Desconocido' };
    }
  };

  const estadoInfo = getEstadoIcon();

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      {/* Encabezado */}
      <div className="text-center mb-6">
        <span className="text-4xl">{estadoInfo.icon}</span>
        <h2 className={`text-2xl font-bold ${estadoInfo.color} mt-2`}>
          {estadoInfo.texto}
        </h2>
      </div>

      {/* Estadísticas principales */}
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <p className="text-lg text-gray-700 text-center mb-4">
          Se encontraron <span className="font-bold text-primary-600">{resultado.total_encontradas}</span> recetas en total:
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg border-2 border-green-200 text-center">
            <div className="text-3xl font-bold text-green-600">📥 {resultado.total_nuevas}</div>
            <div className="text-sm text-gray-600 mt-1">recetas nuevas guardadas</div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border-2 border-amber-200 text-center">
            <div className="text-3xl font-bold text-amber-600">🔄 {resultado.total_duplicadas}</div>
            <div className="text-sm text-gray-600 mt-1">recetas ya existían (omitidas)</div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border-2 border-red-200 text-center">
            <div className="text-3xl font-bold text-red-600">❌ {resultado.errores.length}</div>
            <div className="text-sm text-gray-600 mt-1">errores</div>
          </div>
        </div>

        <p className="text-center text-gray-500 mt-4">
          ⏱️ Tiempo total: {formatTiempo(resultado.tiempo_total)}
        </p>
      </div>

      {/* Desglose por sitio */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-3">Desglose por sitio:</h3>
        <div className="space-y-2">
          {resultado.sitios.map((sitio) => (
            <div
              key={sitio.nombre}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center gap-2">
                <span>{sitio.estado === 'completado' ? '✅' : sitio.estado === 'error' ? '❌' : '⏹️'}</span>
                <span className="font-medium">{sitio.nombre}</span>
              </div>
              <div className="text-sm text-gray-600">
                {sitio.estado === 'error' ? (
                  <span className="text-red-600">{sitio.error_mensaje || 'Error'}</span>
                ) : (
                  <span>
                    {sitio.encontradas} encontradas • 
                    <span className="text-green-600"> {sitio.nuevas} nuevas</span> • 
                    <span className="text-amber-600"> {sitio.duplicadas} duplicadas</span>
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Errores si los hay */}
      {resultado.errores.length > 0 && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-md font-semibold text-red-800 mb-2">Errores durante la búsqueda:</h3>
          <ul className="text-sm text-red-700 list-disc list-inside space-y-1">
            {resultado.errores.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Botones de acción */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={() => navigate('/')}
          className="flex-1 py-3 px-4 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
        >
          <span>📖</span>
          Ver mi recetario
        </button>
        
        <button
          onClick={onNuevaBusqueda}
          className="flex-1 py-3 px-4 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
        >
          <span>🔍</span>
          Nueva búsqueda
        </button>
      </div>
    </div>
  );
};

export default ResultadoBusqueda;
