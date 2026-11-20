import { Component, computed, inject, output, signal } from '@angular/core';
import { FormField, email, form, maxLength, required } from '@angular/forms/signals';
import { firstValueFrom } from 'rxjs';

import { VisitaCreate } from '../../models/visita';
import { BackendService, mensajeDeError } from '../../services/backend.service';
import { ToastService } from '../../services/toast.service';

function visitaVacia(): VisitaCreate {
  return { nombre: '', correo: '', fecha: '', hora: '', motivo: '' };
}

@Component({
  selector: 'app-visita-form',
  imports: [FormField],
  templateUrl: './visita-form.html',
  styleUrl: './visita-form.scss',
})
export class VisitaFormComponent {
  private readonly backend = inject(BackendService);
  private readonly toast = inject(ToastService);

  readonly registrada = output<void>();

  protected readonly modelo = signal<VisitaCreate>(visitaVacia());
  protected readonly formulario = form(this.modelo, (visita) => {
    required(visita.nombre, { message: 'El nombre es obligatorio' });
    maxLength(visita.nombre, 150, { message: 'Máximo 150 caracteres' });
    required(visita.correo, { message: 'El correo es obligatorio' });
    maxLength(visita.correo, 255, { message: 'Máximo 255 caracteres' });
    email(visita.correo, { message: 'Introduce un correo válido' });
    required(visita.fecha, { message: 'La fecha es obligatoria' });
    required(visita.hora, { message: 'La hora es obligatoria' });
    required(visita.motivo, { message: 'El motivo es obligatorio' });
  });

  protected readonly enviando = signal(false);

  protected readonly nombreError = computed(() => this.primerError(this.formulario.nombre()));
  protected readonly correoError = computed(() => this.primerError(this.formulario.correo()));
  protected readonly fechaError = computed(() => this.primerError(this.formulario.fecha()));
  protected readonly horaError = computed(() => this.primerError(this.formulario.hora()));
  protected readonly motivoError = computed(() => this.primerError(this.formulario.motivo()));

  private primerError(campo: {
    errors: () => readonly { message?: string }[];
  }): string | undefined {
    const error = campo.errors()[0];
    return error ? (error.message ?? 'Valor no válido') : undefined;
  }

  protected async enviar(event: Event): Promise<void> {
    event.preventDefault();
    this.formulario().markAsTouched();

    if (this.enviando() || this.formulario().invalid()) {
      return;
    }

    this.enviando.set(true);
    try {
      await firstValueFrom(this.backend.crearVisita({ ...this.modelo() }));
      this.formulario().reset(visitaVacia());
      this.toast.mostrar('Visita registrada correctamente', 'ok');
      this.registrada.emit();
    } catch (error) {
      this.toast.mostrar(mensajeDeError(error), 'error');
    } finally {
      this.enviando.set(false);
    }
  }
}
