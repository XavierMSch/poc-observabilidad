import { Component, OnInit, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { SimulateButtonsComponent } from './components/simulate-buttons/simulate-buttons';
import { ToastComponent } from './components/toast/toast';
import { VisitaFormComponent } from './components/visita-form/visita-form';
import { VisitasTableComponent } from './components/visitas-table/visitas-table';
import { Visita } from './models/visita';
import { BackendService, mensajeDeError } from './services/backend.service';
import { ToastService } from './services/toast.service';

@Component({
  selector: 'app-root',
  imports: [VisitaFormComponent, VisitasTableComponent, SimulateButtonsComponent, ToastComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private readonly backend = inject(BackendService);
  private readonly toast = inject(ToastService);

  protected readonly visitas = signal<Visita[]>([]);
  protected readonly cargandoVisitas = signal(false);

  async ngOnInit(): Promise<void> {
    await this.cargarVisitas();
  }

  protected async cargarVisitas(): Promise<void> {
    this.cargandoVisitas.set(true);
    try {
      this.visitas.set(await firstValueFrom(this.backend.listarVisitas()));
    } catch (error) {
      this.toast.mostrar(mensajeDeError(error), 'error');
    } finally {
      this.cargandoVisitas.set(false);
    }
  }
}
