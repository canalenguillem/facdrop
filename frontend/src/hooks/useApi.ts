import api from '../services/api';

/** Devuelve el cliente axios ya configurado (baseURL + JWT). */
export function useApi() {
  return api;
}
