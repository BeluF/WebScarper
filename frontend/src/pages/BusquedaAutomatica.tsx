import React, { useState, useEffect, useCallback, useRef } from 'react';
import toast from 'react-hot-toast';
import BusquedaForm from '../components/BusquedaForm';
import ProgresoBusqueda from '../components/ProgresoBusqueda';
import ResultadoBusqueda from '../components/ResultadoBusqueda';
import { 
  FiltrosDieteticos, 
  BusquedaProgreso, 
  BusquedaResultado 
} from '../types/recipe';
import {
  iniciarBusquedaAutomatica,
  obtenerProgresoBusqueda,
  cancelarBusqueda,
} from '../services/api';

/**
 * Página de búsqueda automática de recetas.
 * 
 * Permite buscar recetas en masa en todos los sitios configurados,
 * aplicando filtros dietéticos y mostrando el progreso en tiempo real.
 */
const BusquedaAutomatica: React.FC = () => {
  // Estado del flujo de búsqueda: 'formulario' | 'en_progreso' | 'completado'
  const [estadoFlujo, setEstadoFlujo] = useState<'formulario' | 'en_progreso' | 'completado'>('formulario');
  
  // ID de la búsqueda actual
  const [busquedaId, setBusquedaId] = useState<string | null>(null);
  
  // Progreso de la búsqueda
  const [progreso, setProgreso] = useState<BusquedaProgreso | null>(null);
  
  // Resultado final
  const [resultado, setResultado] = useState<BusquedaResultado | null>(null);
  
  // Estado de carga al iniciar
  const [iniciando, setIniciando] = useState(false);
  
  // Referencia para el intervalo de polling
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Limpiar polling al desmontar
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  // Función de polling para obtener el progreso
  const actualizarProgreso = useCallback(async (id: string) => {
    try {
      const nuevoProgreso = await obtenerProgresoBusqueda(id);
      setProgreso(nuevoProgreso);
      
      // Si la búsqueda terminó, detener polling y mostrar resultados
      if (nuevoProgreso.estado !== 'en_progreso') {
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        
        setResultado({
          busqueda_id: nuevoProgreso.busqueda_id,
          estado: nuevoProgreso.estado as BusquedaResultado['estado'],
          total_encontradas: nuevoProgreso.total_encontradas,
          total_nuevas: nuevoProgreso.total_nuevas,
          total_duplicadas: nuevoProgreso.total_duplicadas,
          sitios: nuevoProgreso.sitios,
          errores: nuevoProgreso.errores,
          tiempo_total: nuevoProgreso.tiempo_transcurrido || 0,
        });
        setEstadoFlujo('completado');
        
        if (nuevoProgreso.estado === 'completado') {
          toast.success(`¡Búsqueda completada! ${nuevoProgreso.total_nuevas} recetas nuevas guardadas.`);
        } else if (nuevoProgreso.estado === 'cancelado') {
          toast('Búsqueda cancelada', { icon: '⏹️' });
        }
      }
    } catch (error) {
      console.error('Error al obtener progreso:', error);
      // No detener el polling por un error temporal
    }
  }, []);

  // Iniciar búsqueda
  const handleIniciarBusqueda = async (
    palabraClave: string | null,
    filtros: FiltrosDieteticos,
    sitios: string[],
    limite: number
  ) => {
    setIniciando(true);
    
    try {
      const respuesta = await iniciarBusquedaAutomatica({
        palabra_clave: palabraClave,
        filtros,
        sitios,
        limite,
      });
      
      setBusquedaId(respuesta.busqueda_id);
      setEstadoFlujo('en_progreso');
      
      toast.success(`${respuesta.mensaje} (modo ${respuesta.tipo_busqueda})`);
      
      // Iniciar polling cada 2 segundos
      pollingRef.current = setInterval(() => {
        actualizarProgreso(respuesta.busqueda_id);
      }, 2000);
      
      // Primera actualización inmediata
      actualizarProgreso(respuesta.busqueda_id);
      
    } catch (error) {
      console.error('Error al iniciar búsqueda:', error);
      toast.error('Error al iniciar la búsqueda automática');
    } finally {
      setIniciando(false);
    }
  };

  // Cancelar búsqueda
  const handleCancelar = async () => {
    if (!busquedaId) return;
    
    try {
      await cancelarBusqueda(busquedaId);
      toast('Cancelando búsqueda...', { icon: '⏳' });
    } catch (error) {
      console.error('Error al cancelar:', error);
      toast.error('Error al cancelar la búsqueda');
    }
  };

  // Nueva búsqueda (reiniciar)
  const handleNuevaBusqueda = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    setBusquedaId(null);
    setProgreso(null);
    setResultado(null);
    setEstadoFlujo('formulario');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        🔍 Búsqueda Automática de Recetas
      </h1>
      
      <p className="text-gray-600 mb-6">
        Busca recetas automáticamente en todos los sitios configurados. 
        Las recetas encontradas se guardarán automáticamente en tu recetario.
      </p>

      {/* Formulario de búsqueda */}
      {estadoFlujo === 'formulario' && (
        <BusquedaForm 
          onIniciarBusqueda={handleIniciarBusqueda}
          cargando={iniciando}
        />
      )}

      {/* Progreso de búsqueda */}
      {estadoFlujo === 'en_progreso' && progreso && (
        <ProgresoBusqueda 
          progreso={progreso}
          onCancelar={handleCancelar}
        />
      )}

      {/* Resultados */}
      {estadoFlujo === 'completado' && resultado && (
        <ResultadoBusqueda 
          resultado={resultado}
          onNuevaBusqueda={handleNuevaBusqueda}
        />
      )}
    </div>
  );
};

export default BusquedaAutomatica;
