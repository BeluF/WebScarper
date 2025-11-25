import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import RecipeForm from '../components/RecipeForm';
import Filters from '../components/Filters';
import RecipeList from '../components/RecipeList';
import { Receta, FiltrosReceta } from '../types/recipe';
import { obtenerRecetas, eliminarReceta, descargarPDFMultiple, descargarArchivo } from '../services/api';

/**
 * Página principal que muestra el listado de recetas.
 */
const Home: React.FC = () => {
  const [recetas, setRecetas] = useState<Receta[]>([]);
  const [filtros, setFiltros] = useState<FiltrosReceta>({});
  const [seleccionadas, setSeleccionadas] = useState<number[]>([]);
  const [cargando, setCargando] = useState(true);
  const [total, setTotal] = useState(0);

  // Cargar recetas al montar y cuando cambien los filtros
  const cargarRecetas = useCallback(async () => {
    setCargando(true);
    try {
      const data = await obtenerRecetas(filtros);
      setRecetas(data.recetas);
      setTotal(data.total);
    } catch (error) {
      toast.error('Error al cargar las recetas');
      console.error('Error:', error);
    } finally {
      setCargando(false);
    }
  }, [filtros]);

  useEffect(() => {
    cargarRecetas();
  }, [cargarRecetas]);

  // Manejar nueva receta agregada
  const handleRecetaAgregada = (receta: Receta) => {
    setRecetas((prev) => [receta, ...prev]);
    setTotal((prev) => prev + 1);
  };

  // Manejar selección de recetas
  const handleSeleccionar = (id: number) => {
    setSeleccionadas((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  // Manejar eliminación de receta
  const handleEliminar = async (id: number) => {
    try {
      await eliminarReceta(id);
      setRecetas((prev) => prev.filter((r) => r.id !== id));
      setSeleccionadas((prev) => prev.filter((i) => i !== id));
      setTotal((prev) => prev - 1);
      toast.success('Receta eliminada');
    } catch (error) {
      toast.error('Error al eliminar la receta');
    }
  };

  // Descargar PDF de recetas seleccionadas
  const handleDescargarPDFMultiple = async () => {
    if (seleccionadas.length === 0) {
      toast.error('Selecciona al menos una receta');
      return;
    }

    try {
      const blob = await descargarPDFMultiple(seleccionadas);
      descargarArchivo(blob, 'mi_recetario.pdf');
      toast.success('PDF descargado');
    } catch (error) {
      toast.error('Error al descargar el PDF');
    }
  };

  // Seleccionar/deseleccionar todas
  const handleSeleccionarTodas = () => {
    if (seleccionadas.length === recetas.length) {
      setSeleccionadas([]);
    } else {
      setSeleccionadas(recetas.map((r) => r.id));
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        🍳 Mi Recetario Personal
      </h1>

      {/* Formulario para agregar recetas */}
      <RecipeForm onRecetaAgregada={handleRecetaAgregada} />

      {/* Filtros */}
      <Filters filtros={filtros} onFiltrosChange={setFiltros} />

      {/* Barra de acciones para selección múltiple */}
      {recetas.length > 0 && (
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-4">
            <button
              onClick={handleSeleccionarTodas}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              {seleccionadas.length === recetas.length
                ? '✕ Deseleccionar todas'
                : '☑️ Seleccionar todas'}
            </button>
            {seleccionadas.length > 0 && (
              <span className="text-sm text-gray-600">
                {seleccionadas.length} seleccionada(s)
              </span>
            )}
          </div>
          
          {seleccionadas.length > 0 && (
            <button
              onClick={handleDescargarPDFMultiple}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              📄 Descargar PDF ({seleccionadas.length})
            </button>
          )}
        </div>
      )}

      {/* Contador de resultados */}
      {!cargando && (
        <p className="text-gray-600 mb-4">
          {total} receta(s) encontrada(s)
        </p>
      )}

      {/* Lista de recetas */}
      <RecipeList
        recetas={recetas}
        seleccionadas={seleccionadas}
        onSeleccionar={handleSeleccionar}
        onEliminar={handleEliminar}
        cargando={cargando}
      />
    </div>
  );
};

export default Home;
