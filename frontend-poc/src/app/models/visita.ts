export interface VisitaCreate {
  nombre: string;
  correo: string;
  /** Fecha en formato `yyyy-MM-dd`. */
  fecha: string;
  /** Hora en formato `HH:mm`. */
  hora: string;
  motivo: string;
}

export interface Visita extends VisitaCreate {
  id: number;
  created_at: string;
}

export interface SimulacionRespuesta {
  status: string;
  message: string;
  delay_seconds: number;
}
