import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { App } from './app';
import { BackendService } from './services/backend.service';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        {
          provide: BackendService,
          useValue: {
            listarVisitas: () => of([]),
            crearVisita: () => of({}),
            simularRespuestaLenta: () => of({ status: 'ok', message: 'ok', delay_seconds: 3 }),
            simularDbLenta: () => of({ status: 'ok', message: 'ok', delay_seconds: 2 }),
            simularError: () => of(undefined),
          },
        },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should render the page title', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Registro de visitas');
  });
});
