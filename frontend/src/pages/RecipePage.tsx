import React from 'react';
import RecipeDetail from '../components/RecipeDetail';

/**
 * Página que muestra el detalle de una receta individual.
 */
const RecipePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <RecipeDetail />
    </div>
  );
};

export default RecipePage;
