import { Component, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { BackendService, mensajeDeError } from '../../services/backend.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-simulate-buttons',
  imports: [],
  templateUrl: './simulate-buttons.html',
  styleUrl: './simulate-buttons.scss',
})
export class SimulateButtonsComponent {
  private readonly backend = inject(BackendService);
  private readonly toast = inject(ToastService);

  protected readonly cargandoLenta = signal(false);
  protected readonly cargandoDbLenta = signal(false);
  protected readonly cargandoError = signal(false);

  protected async simularLenta(): Promise<void> {
    if (this.cargandoLenta()) {
      return;
    }

    this.cargandoLenta.set(true);
    try {
      const respuesta = await firstValueFrom(this.backend.simularRespuestaLenta());
      this.toast.mostrar(respuesta.message, 'ok');
    } catch (error) {
      this.toast.mostrar(mensajeDeError(error), 'error');
    } finally {
      this.cargandoLenta.set(false);
    }
  }

  protected async simularDbLenta(): Promise<void> {
    if (this.cargandoDbLenta()) {
      return;
    }

    this.cargandoDbLenta.set(true);
    try {
      const respuesta = await firstValueFrom(this.backend.simularDbLenta());
      this.toast.mostrar(respuesta.message, 'ok');
    } catch (error) {
      this.toast.mostrar(mensajeDeError(error), 'error');
    } finally {
      this.cargandoDbLenta.set(false);
    }
  }

  protected async simularError(): Promise<void> {
    if (this.cargandoError()) {
      return;
    }

    this.cargandoError.set(true);
    try {
      await firstValueFrom(this.backend.simularError());
    } catch (error) {
      this.toast.mostrar(mensajeDeError(error), 'error');
    } finally {
      this.cargandoError.set(false);
    }
  }
}
