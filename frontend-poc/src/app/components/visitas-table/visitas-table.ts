import { Component, input } from '@angular/core';

import { Visita } from '../../models/visita';

@Component({
  selector: 'app-visitas-table',
  imports: [],
  templateUrl: './visitas-table.html',
  styleUrl: './visitas-table.scss',
})
export class VisitasTableComponent {
  readonly visitas = input.required<Visita[]>();
  readonly cargando = input(false);
}
