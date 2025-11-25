import React, { useState, useEffect } from 'react';
import { SitioSoportado, FiltrosDieteticos } from '../types/recipe';
import { obtenerSitiosSoportados } from '../services/api';

interface BusquedaFormProps {
  onIniciarBusqueda: (
    palabraClave: string | null,
    filtros: FiltrosDieteticos,
    sitios: string[],
    limite: number
  ) => void;
  cargando: boolean;
}

/**
 * Formulario para configurar y iniciar una búsqueda automática de recetas.
 */
const BusquedaForm: React.FC<BusquedaFormProps> = ({ onIniciarBusqueda, cargando }) => {
  const [palabraClave, setPalabraClave] = useState('');
  const [filtros, setFiltros] = useState<FiltrosDieteticos>({
    sin_tacc: false,
    vegetariana: false,
    vegana: false,
  });
  const [sitiosDisponibles, setSitiosDisponibles] = useState<SitioSoportado[]>([]);
  const [sitiosSeleccionados, setSitiosSeleccionados] = useState<string[]>([]);
  const [todosSitios, setTodosSitios] = useState(true);
  const [limite, setLimite] = useState<string>('');

  // Cargar sitios disponibles al montar
  useEffect(() => {
    const cargarSitios = async () => {
      try {
        const sitios = await obtenerSitiosSoportados();
        setSitiosDisponibles(sitios);
      } catch (error) {
        console.error('Error al cargar sitios:', error);
      }
    };
    cargarSitios();
  }, []);

  const handleFiltroChange = (campo: keyof FiltrosDieteticos) => {
    setFiltros((prev) => ({ ...prev, [campo]: !prev[campo] }));
  };

  const handleTodosSitiosChange = () => {
    setTodosSitios(!todosSitios);
    if (!todosSitios) {
      setSitiosSeleccionados([]);
    }
  };

  const handleSitioChange = (nombre: string) => {
    setSitiosSeleccionados((prev) =>
      prev.includes(nombre)
        ? prev.filter((s) => s !== nombre)
        : [...prev, nombre]
    );
    setTodosSitios(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const sitiosParaBuscar = todosSitios
      ? ['todos']
      : sitiosSeleccionados.length > 0
      ? sitiosSeleccionados
      : ['todos'];

    const limiteNum = limite ? parseInt(limite, 10) : 500;
    
    onIniciarBusqueda(
      palabraClave.trim() || null,
      filtros,
      sitiosParaBuscar,
      limiteNum > 0 ? limiteNum : 500
    );
  };

  const limiteNum = limite ? parseInt(limite, 10) : 500;
  const tipoBusqueda = limiteNum <= 50 ? 'paralelo' : 'secuencial';

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="text-2xl">🔍</span>
        Búsqueda Automática de Recetas
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Campo de palabra clave */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Palabra clave (opcional):
          </label>
          <input
            type="text"
            value={palabraClave}
            onChange={(e) => setPalabraClave(e.target.value)}
            placeholder="ej: milanesas, brownies, ensalada..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            disabled={cargando}
          />
          <p className="text-xs text-gray-500 mt-1">
            Dejar vacío para buscar todas las recetas disponibles
          </p>
        </div>

        {/* Filtros dietéticos */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filtros dietéticos:
          </label>
          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filtros.sin_tacc}
                onChange={() => handleFiltroChange('sin_tacc')}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                disabled={cargando}
              />
              <span className="text-sm text-gray-700">🌾 Sin TACC</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filtros.vegetariana}
                onChange={() => handleFiltroChange('vegetariana')}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                disabled={cargando}
              />
              <span className="text-sm text-gray-700">🥬 Vegetariana</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filtros.vegana}
                onChange={() => handleFiltroChange('vegana')}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                disabled={cargando}
              />
              <span className="text-sm text-gray-700">🌱 Vegana</span>
            </label>
          </div>
        </div>

        {/* Selector de sitios */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sitios donde buscar:
          </label>
          <div className="space-y-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={todosSitios}
                onChange={handleTodosSitiosChange}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                disabled={cargando}
              />
              <span className="text-sm font-medium text-gray-700">✅ Todos los sitios</span>
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2 ml-6">
              {sitiosDisponibles.map((sitio) => (
                <label key={sitio.nombre} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={!todosSitios && sitiosSeleccionados.includes(sitio.nombre)}
                    onChange={() => handleSitioChange(sitio.nombre)}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    disabled={cargando || todosSitios}
                  />
                  <span className={`text-sm ${todosSitios ? 'text-gray-400' : 'text-gray-700'}`}>
                    {sitio.nombre}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Límite de recetas */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Límite de recetas:
          </label>
          <div className="flex items-center gap-4">
            <input
              type="number"
              value={limite}
              onChange={(e) => setLimite(e.target.value)}
              placeholder="500"
              min="1"
              max="1000"
              className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              disabled={cargando}
            />
            <div className="text-sm text-gray-500">
              <p>Vacío = hasta 500 recetas</p>
              <p className={tipoBusqueda === 'paralelo' ? 'text-green-600 font-medium' : 'text-amber-600 font-medium'}>
                {tipoBusqueda === 'paralelo' 
                  ? '⚡ Búsqueda rápida (paralela)' 
                  : '🐢 Búsqueda segura (secuencial)'}
              </p>
            </div>
          </div>
        </div>

        {/* Botón de búsqueda */}
        <button
          type="submit"
          disabled={cargando}
          className="w-full py-3 px-6 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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
              Iniciando búsqueda...
            </>
          ) : (
            <>
              <span className="text-xl">🚀</span>
              Iniciar Búsqueda Automática
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default BusquedaForm;
