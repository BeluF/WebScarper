import React from 'react';
import { Link } from 'react-router-dom';
import { Receta } from '../types/recipe';

interface RecipeCardProps {
  receta: Receta;
  seleccionada?: boolean;
  onSeleccionar?: (id: number) => void;
  onEliminar?: (id: number) => void;
}

/**
 * Tarjeta que muestra la información básica de una receta.
 */
const RecipeCard: React.FC<RecipeCardProps> = ({ 
  receta, 
  seleccionada = false,
  onSeleccionar,
  onEliminar 
}) => {
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();
    onSeleccionar?.(receta.id);
  };

  const handleEliminar = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (confirm(`¿Estás seguro de eliminar "${receta.titulo}"?`)) {
      onEliminar?.(receta.id);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow ${seleccionada ? 'ring-2 ring-primary-500' : ''}`}>
      {/* Imagen de la receta */}
      <div className="relative h-48 bg-gray-200">
        {receta.imagen_url ? (
          <img
            src={receta.imagen_url}
            alt={receta.titulo}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=Sin+imagen';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="text-6xl">🍽️</span>
          </div>
        )}
        
        {/* Checkbox de selección */}
        {onSeleccionar && (
          <div className="absolute top-2 left-2">
            <input
              type="checkbox"
              checked={seleccionada}
              onChange={handleCheckboxChange}
              className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500 cursor-pointer"
            />
          </div>
        )}

        {/* Badges de categoría */}
        <div className="absolute top-2 right-2 flex gap-1">
          {receta.es_sin_tacc && (
            <span className="bg-yellow-500 text-white text-xs px-2 py-1 rounded-full">
              🌾 Sin TACC
            </span>
          )}
          {receta.es_vegetariana && (
            <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
              🥬 Vegetariana
            </span>
          )}
          {receta.es_vegana && (
            <span className="bg-green-700 text-white text-xs px-2 py-1 rounded-full">
              🌱 Vegana
            </span>
          )}
        </div>
      </div>

      {/* Contenido de la tarjeta */}
      <div className="p-4">
        <Link to={`/receta/${receta.id}`}>
          <h3 className="text-lg font-semibold text-gray-800 hover:text-primary-600 transition-colors line-clamp-2">
            {receta.titulo}
          </h3>
        </Link>
        
        <p className="text-sm text-gray-500 mt-1">
          De: {receta.sitio_origen}
        </p>

        {/* Metadatos */}
        <div className="flex gap-4 mt-3 text-sm text-gray-600">
          {receta.tiempo_coccion && (
            <span>⏱️ {receta.tiempo_coccion}</span>
          )}
          {receta.porciones && (
            <span>👥 {receta.porciones}</span>
          )}
        </div>

        {/* Acciones */}
        <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
          <Link 
            to={`/receta/${receta.id}`}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Ver receta →
          </Link>
          
          {onEliminar && (
            <button
              onClick={handleEliminar}
              className="text-red-500 hover:text-red-700 text-sm"
            >
              🗑️ Eliminar
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecipeCard;
