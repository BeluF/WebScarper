import React from 'react';
import { FiltrosReceta } from '../types/recipe';

interface FiltersProps {
  filtros: FiltrosReceta;
  onFiltrosChange: (filtros: FiltrosReceta) => void;
}

/**
 * Componente de filtros para buscar y filtrar recetas.
 */
const Filters: React.FC<FiltersProps> = ({ filtros, onFiltrosChange }) => {
  const handleBusquedaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltrosChange({ ...filtros, busqueda: e.target.value || undefined });
  };

  const handleCheckboxChange = (campo: 'sin_tacc' | 'vegetariana' | 'vegana') => {
    const nuevoValor = filtros[campo] === true ? undefined : true;
    onFiltrosChange({ ...filtros, [campo]: nuevoValor });
  };

  const limpiarFiltros = () => {
    onFiltrosChange({});
  };

  const hayFiltrosActivos = filtros.busqueda || filtros.sin_tacc || filtros.vegetariana || filtros.vegana;

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="flex flex-wrap gap-4 items-center">
        {/* Búsqueda por texto */}
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            value={filtros.busqueda || ''}
            onChange={handleBusquedaChange}
            placeholder="🔍 Buscar receta por nombre..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>

        {/* Filtros por categoría */}
        <div className="flex gap-4 items-center">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filtros.sin_tacc === true}
              onChange={() => handleCheckboxChange('sin_tacc')}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">🌾 Sin TACC</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filtros.vegetariana === true}
              onChange={() => handleCheckboxChange('vegetariana')}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">🥬 Vegetariana</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filtros.vegana === true}
              onChange={() => handleCheckboxChange('vegana')}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">🌱 Vegana</span>
          </label>
        </div>

        {/* Botón limpiar filtros */}
        {hayFiltrosActivos && (
          <button
            onClick={limpiarFiltros}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            ✕ Limpiar filtros
          </button>
        )}
      </div>
    </div>
  );
};

export default Filters;
