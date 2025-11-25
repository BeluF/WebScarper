import React from 'react';
import { Receta } from '../types/recipe';
import RecipeCard from './RecipeCard';

interface RecipeListProps {
  recetas: Receta[];
  seleccionadas: number[];
  onSeleccionar: (id: number) => void;
  onEliminar: (id: number) => void;
  cargando: boolean;
}

/**
 * Lista de recetas con soporte para selección múltiple.
 */
const RecipeList: React.FC<RecipeListProps> = ({ 
  recetas, 
  seleccionadas,
  onSeleccionar,
  onEliminar,
  cargando 
}) => {
  if (cargando) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (recetas.length === 0) {
    return (
      <div className="text-center py-12">
        <span className="text-6xl mb-4 block">📭</span>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">
          No hay recetas todavía
        </h3>
        <p className="text-gray-500">
          Agrega tu primera receta pegando una URL arriba
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {recetas.map((receta) => (
        <RecipeCard
          key={receta.id}
          receta={receta}
          seleccionada={seleccionadas.includes(receta.id)}
          onSeleccionar={onSeleccionar}
          onEliminar={onEliminar}
        />
      ))}
    </div>
  );
};

export default RecipeList;
