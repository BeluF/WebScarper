import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { scrapearReceta } from '../services/api';
import { Receta } from '../types/recipe';

interface RecipeFormProps {
  onRecetaAgregada: (receta: Receta) => void;
}

/**
 * Formulario para agregar una nueva receta mediante scraping.
 */
const RecipeForm: React.FC<RecipeFormProps> = ({ onRecetaAgregada }) => {
  const [url, setUrl] = useState('');
  const [cargando, setCargando] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      toast.error('Por favor, ingresa una URL válida');
      return;
    }

    setCargando(true);
    
    try {
      const resultado = await scrapearReceta(url);
      
      if (resultado.exito && resultado.receta) {
        toast.success(`¡Receta "${resultado.receta.titulo}" agregada exitosamente!`);
        onRecetaAgregada(resultado.receta);
        setUrl('');
      } else {
        toast.error(resultado.mensaje || 'Error al scrapear la receta');
      }
    } catch (error) {
      toast.error('Error de conexión con el servidor');
      console.error('Error:', error);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        📥 Agregar Nueva Receta
      </h2>
      <form onSubmit={handleSubmit} className="flex gap-4">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Pega aquí la URL de la receta..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          disabled={cargando}
        />
        <button
          type="submit"
          disabled={cargando}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {cargando ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle 
                  className="opacity-25" 
                  cx="12" 
                  cy="12" 
                  r="10" 
                  stroke="currentColor" 
                  strokeWidth="4"
                  fill="none"
                />
                <path 
                  className="opacity-75" 
                  fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Scrapeando...
            </>
          ) : (
            <>
              <span>🔍</span>
              Scrapear
            </>
          )}
        </button>
      </form>
      <p className="text-sm text-gray-500 mt-2">
        Sitios soportados: Cookpad, AllRecipes, Tasty, Directo al Paladar, Paulina Cocina, HelloFresh y más
      </p>
    </div>
  );
};

export default RecipeForm;
