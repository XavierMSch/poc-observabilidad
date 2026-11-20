import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Service, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { SimulacionRespuesta, Visita, VisitaCreate } from '../models/visita';

@Service()
export class BackendService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  listarVisitas(): Observable<Visita[]> {
    return this.http.get<Visita[]>(`${this.baseUrl}/api/visitas`);
  }

  crearVisita(visita: VisitaCreate): Observable<Visita> {
    return this.http.post<Visita>(`${this.baseUrl}/api/visitas`, visita);
  }

  simularRespuestaLenta(): Observable<SimulacionRespuesta> {
    return this.http.get<SimulacionRespuesta>(`${this.baseUrl}/api/simulate/slow`);
  }

  simularDbLenta(): Observable<SimulacionRespuesta> {
    return this.http.get<SimulacionRespuesta>(`${this.baseUrl}/api/simulate/slow-db`);
  }

  simularError(): Observable<never> {
    return this.http.get<never>(`${this.baseUrl}/api/simulate/error`);
  }
}

/** Extrae un mensaje legible de un error HTTP, usando el `detail` del backend si existe. */
export function mensajeDeError(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    const body: unknown = error.error;
    if (typeof body === 'object' && body !== null && 'detail' in body) {
      const detail = (body as { detail: unknown }).detail;
      if (typeof detail === 'string' && detail.length > 0) {
        return detail;
      }
    }
    return `Error ${error.status}: ${error.statusText || 'fallo en la petición'}`;
  }
  return 'Ha ocurrido un error inesperado';
}
