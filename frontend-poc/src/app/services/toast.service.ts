import { Service, signal } from '@angular/core';

export type ToastTipo = 'error' | 'ok';

export interface ToastMensaje {
  texto: string;
  tipo: ToastTipo;
}

const DURACION_MS = 5000;

@Service()
export class ToastService {
  private timeoutId: ReturnType<typeof setTimeout> | undefined;

  readonly mensaje = signal<ToastMensaje | null>(null);

  mostrar(texto: string, tipo: ToastTipo = 'error'): void {
    this.limpiarTimeout();
    this.mensaje.set({ texto, tipo });
    this.timeoutId = setTimeout(() => {
      this.mensaje.set(null);
      this.timeoutId = undefined;
    }, DURACION_MS);
  }

  ocultar(): void {
    this.limpiarTimeout();
    this.mensaje.set(null);
  }

  private limpiarTimeout(): void {
    if (this.timeoutId !== undefined) {
      clearTimeout(this.timeoutId);
      this.timeoutId = undefined;
    }
  }
}
