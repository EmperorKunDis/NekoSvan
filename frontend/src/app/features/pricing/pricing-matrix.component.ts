import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import { PaginatedResponse } from '../../core/services/deal.service';

interface PricingMatrix {
  id: number;
  category: string;
  category_label: string;
  base_hours: number;
  hourly_rate: number;
  is_active: boolean;
}

interface PricingModifier {
  id: number;
  modifier_type: string;
  modifier_type_display: string;
  key: string;
  label: string;
  multiplier: number;
  extra_hours: number;
  is_active: boolean;
}

@Component({
  selector: 'app-pricing-matrix',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="page-header">
      <h1>Cenová matice</h1>
    </div>

    <div class="card">
      <div class="card-header">
        <h3>Kategorie projektů</h3>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>Kategorie</th>
            <th>Název</th>
            <th>Základní hodiny</th>
            <th>Hodinová sazba</th>
            <th>Akce</th>
          </tr>
        </thead>
        <tbody>
          @for (m of matrices(); track m.id) {
            <tr>
              <td>{{ m.category }}</td>
              <td>
                <input type="text" [(ngModel)]="m.category_label" class="form-input" />
              </td>
              <td>
                <input
                  type="number"
                  [(ngModel)]="m.base_hours"
                  class="form-input"
                  style="width: 80px"
                />
              </td>
              <td>
                <input
                  type="number"
                  [(ngModel)]="m.hourly_rate"
                  class="form-input"
                  style="width: 100px"
                />
                Kč
              </td>
              <td>
                <button class="btn btn-primary btn-sm" (click)="saveMatrix(m)">Uložit</button>
              </td>
            </tr>
          }
        </tbody>
      </table>
    </div>

    <div class="card" style="margin-top: 24px">
      <div class="card-header">
        <h3>Modifikátory</h3>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>Typ</th>
            <th>Klíč</th>
            <th>Název</th>
            <th>Násobič</th>
            <th>Extra hodiny</th>
            <th>Akce</th>
          </tr>
        </thead>
        <tbody>
          @for (m of modifiers(); track m.id) {
            <tr>
              <td>{{ m.modifier_type_display }}</td>
              <td>{{ m.key }}</td>
              <td>
                <input type="text" [(ngModel)]="m.label" class="form-input" />
              </td>
              <td>
                <input
                  type="number"
                  [(ngModel)]="m.multiplier"
                  step="0.1"
                  class="form-input"
                  style="width: 80px"
                />
              </td>
              <td>
                <input
                  type="number"
                  [(ngModel)]="m.extra_hours"
                  class="form-input"
                  style="width: 80px"
                />
              </td>
              <td>
                <button class="btn btn-primary btn-sm" (click)="saveModifier(m)">Uložit</button>
              </td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
  styles: [
    `
      .form-input {
        padding: 4px 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
      }
      .btn-sm {
        padding: 4px 8px;
        font-size: 12px;
      }
    `,
  ],
})
export class PricingMatrixComponent implements OnInit {
  matrices = signal<PricingMatrix[]>([]);
  modifiers = signal<PricingModifier[]>([]);

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.api.get<PaginatedResponse<PricingMatrix>>('pricing/pricing-matrix/').subscribe({
      next: (data) => this.matrices.set(data.results),
    });
    this.api.get<PaginatedResponse<PricingModifier>>('pricing/pricing-modifiers/').subscribe({
      next: (data) => this.modifiers.set(data.results),
    });
  }

  saveMatrix(m: PricingMatrix): void {
    this.api.patch(`pricing/pricing-matrix/${m.id}/`, m).subscribe({
      next: () => alert('Uloženo'),
    });
  }

  saveModifier(m: PricingModifier): void {
    this.api.patch(`pricing/pricing-modifiers/${m.id}/`, m).subscribe({
      next: () => alert('Uloženo'),
    });
  }
}
