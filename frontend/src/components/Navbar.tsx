import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Barra de navegación principal de la aplicación.
 */
const Navbar: React.FC = () => {
  return (
    <nav className="bg-primary-700 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl">🍳</span>
            <span className="text-white text-xl font-bold">WebScarper</span>
          </Link>
          <div className="flex items-center space-x-4">
            <Link 
              to="/" 
              className="text-white hover:text-primary-200 transition-colors"
            >
              Mis Recetas
            </Link>
            <Link 
              to="/busqueda-automatica" 
              className="text-white hover:text-primary-200 transition-colors flex items-center gap-1"
            >
              <span>🔍</span>
              Búsqueda Automática
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
