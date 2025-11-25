import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Receta, RecetaActualizar } from '../types/recipe';
import { obtenerReceta, actualizarReceta, descargarPDF, descargarArchivo, eliminarReceta } from '../services/api';

/**
 * Vista detallada de una receta individual.
 */
const RecipeDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [receta, setReceta] = useState<Receta | null>(null);
  const [cargando, setCargando] = useState(true);
  const [editando, setEditando] = useState(false);
  const [notasTemp, setNotasTemp] = useState('');
  const [categorias, setCategorias] = useState({
    es_sin_tacc: false,
    es_vegetariana: false,
    es_vegana: false,
  });

  useEffect(() => {
    cargarReceta();
  }, [id]);

  const cargarReceta = async () => {
    if (!id) return;
    
    try {
      const data = await obtenerReceta(parseInt(id));
      setReceta(data);
      setNotasTemp(data.notas_personales || '');
      setCategorias({
        es_sin_tacc: data.es_sin_tacc,
        es_vegetariana: data.es_vegetariana,
        es_vegana: data.es_vegana,
      });
    } catch (error) {
      toast.error('Error al cargar la receta');
      navigate('/');
    } finally {
      setCargando(false);
    }
  };

  const handleGuardar = async () => {
    if (!receta) return;

    try {
      const datos: RecetaActualizar = {
        ...categorias,
        notas_personales: notasTemp || undefined,
      };
      
      const actualizada = await actualizarReceta(receta.id, datos);
      setReceta(actualizada);
      setEditando(false);
      toast.success('Receta actualizada');
    } catch (error) {
      toast.error('Error al actualizar la receta');
    }
  };

  const handleDescargarPDF = async () => {
    if (!receta) return;

    try {
      const blob = await descargarPDF(receta.id);
      descargarArchivo(blob, `${receta.titulo}.pdf`);
      toast.success('PDF descargado');
    } catch (error) {
      toast.error('Error al descargar el PDF');
    }
  };

  const handleEliminar = async () => {
    if (!receta) return;
    
    if (!confirm(`¿Estás seguro de eliminar "${receta.titulo}"?`)) {
      return;
    }

    try {
      await eliminarReceta(receta.id);
      toast.success('Receta eliminada');
      navigate('/');
    } catch (error) {
      toast.error('Error al eliminar la receta');
    }
  };

  if (cargando) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!receta) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Receta no encontrada</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header con imagen */}
      <div className="relative h-64 md:h-96 rounded-lg overflow-hidden mb-6">
        {receta.imagen_url ? (
          <img
            src={receta.imagen_url}
            alt={receta.titulo}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/800x400?text=Sin+imagen';
            }}
          />
        ) : (
          <div className="w-full h-full bg-gray-200 flex items-center justify-center">
            <span className="text-8xl">🍽️</span>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        <div className="absolute bottom-0 left-0 right-0 p-6">
          <h1 className="text-3xl font-bold text-white mb-2">{receta.titulo}</h1>
          <p className="text-white/80">De: {receta.sitio_origen}</p>
        </div>
      </div>

      {/* Acciones */}
      <div className="flex flex-wrap gap-4 mb-6">
        <button
          onClick={() => setEditando(!editando)}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          {editando ? '✕ Cancelar' : '✏️ Editar'}
        </button>
        <button
          onClick={handleDescargarPDF}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          📄 Descargar PDF
        </button>
        <button
          onClick={handleEliminar}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          🗑️ Eliminar
        </button>
        <a
          href={receta.url_origen}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          🔗 Ver original
        </a>
      </div>

      {/* Metadatos y categorías */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-wrap gap-6 mb-4">
          {receta.tiempo_preparacion && (
            <div>
              <span className="text-gray-500 text-sm">Preparación</span>
              <p className="font-medium">⏱️ {receta.tiempo_preparacion}</p>
            </div>
          )}
          {receta.tiempo_coccion && (
            <div>
              <span className="text-gray-500 text-sm">Cocción</span>
              <p className="font-medium">🍳 {receta.tiempo_coccion}</p>
            </div>
          )}
          {receta.porciones && (
            <div>
              <span className="text-gray-500 text-sm">Porciones</span>
              <p className="font-medium">👥 {receta.porciones}</p>
            </div>
          )}
        </div>

        {/* Categorías (editables) */}
        <div className="flex flex-wrap gap-4">
          {editando ? (
            <>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={categorias.es_sin_tacc}
                  onChange={(e) => setCategorias({ ...categorias, es_sin_tacc: e.target.checked })}
                  className="w-4 h-4 text-primary-600"
                />
                <span>🌾 Sin TACC</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={categorias.es_vegetariana}
                  onChange={(e) => setCategorias({ ...categorias, es_vegetariana: e.target.checked })}
                  className="w-4 h-4 text-primary-600"
                />
                <span>🥬 Vegetariana</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={categorias.es_vegana}
                  onChange={(e) => setCategorias({ ...categorias, es_vegana: e.target.checked })}
                  className="w-4 h-4 text-primary-600"
                />
                <span>🌱 Vegana</span>
              </label>
            </>
          ) : (
            <>
              {receta.es_sin_tacc && (
                <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                  🌾 Sin TACC
                </span>
              )}
              {receta.es_vegetariana && (
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                  🥬 Vegetariana
                </span>
              )}
              {receta.es_vegana && (
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                  🌱 Vegana
                </span>
              )}
            </>
          )}
        </div>

        {editando && (
          <button
            onClick={handleGuardar}
            className="mt-4 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            💾 Guardar cambios
          </button>
        )}
      </div>

      {/* Descripción */}
      {receta.descripcion && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">📝 Descripción</h2>
          <p className="text-gray-700">{receta.descripcion}</p>
        </div>
      )}

      {/* Ingredientes */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">🥘 Ingredientes</h2>
        {receta.ingredientes.length > 0 ? (
          <ul className="space-y-2">
            {receta.ingredientes.map((ingrediente, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-primary-600">•</span>
                <span>{ingrediente}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No hay ingredientes disponibles</p>
        )}
      </div>

      {/* Pasos */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">👨‍🍳 Preparación</h2>
        {receta.pasos.length > 0 ? (
          <ol className="space-y-4">
            {receta.pasos.map((paso, index) => (
              <li key={index} className="flex gap-4">
                <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-semibold">
                  {index + 1}
                </span>
                <p className="pt-1">{paso}</p>
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-gray-500">No hay pasos de preparación disponibles</p>
        )}
      </div>

      {/* Notas personales */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">📌 Notas Personales</h2>
        {editando ? (
          <textarea
            value={notasTemp}
            onChange={(e) => setNotasTemp(e.target.value)}
            placeholder="Agrega tus notas personales..."
            className="w-full h-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none"
          />
        ) : receta.notas_personales ? (
          <p className="text-gray-700">{receta.notas_personales}</p>
        ) : (
          <p className="text-gray-500 italic">Sin notas personales</p>
        )}
      </div>
    </div>
  );
};

export default RecipeDetail;
