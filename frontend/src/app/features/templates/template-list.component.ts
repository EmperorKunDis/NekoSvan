import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { ApiService } from '../../core/services/api.service';
import { PaginatedResponse } from '../../core/services/deal.service';

interface ContractTemplate {
  id: number;
  name: string;
  body_template: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-template-list',
  standalone: true,
  imports: [FormsModule, DatePipe],
  template: `
    <div class="page-header">
      <h1>Sablony</h1>
      <button class="btn btn-primary" (click)="showForm()">+ Nova sablona</button>
    </div>

    <!-- Template form (create/edit) -->
    @if (editing()) {
      <div class="card" style="margin-bottom: 16px">
        <h3>{{ editingId() ? 'Upravit sablonu' : 'Nova sablona' }}</h3>
        <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 12px">
          <div>
            <label><strong>Nazev</strong></label>
            <input
              type="text"
              class="form-control"
              [(ngModel)]="formName"
              placeholder="Nazev sablony"
            />
          </div>
          <div>
            <label><strong>Aktivni</strong></label>
            <input type="checkbox" [(ngModel)]="formActive" style="margin-left: 8px" />
          </div>
          <div>
            <label
              ><strong>Telo sablony</strong>
              <small style="color: #888"> — pouzijte {{ placeholderHint }}</small></label
            >
            <textarea
              class="form-control"
              [(ngModel)]="formBody"
              rows="15"
              placeholder="HTML sablona s placeholders..."
              style="font-family: monospace; font-size: 0.85rem"
            ></textarea>
          </div>
          <div style="display: flex; gap: 8px">
            <button class="btn btn-primary" (click)="save()">Ulozit</button>
            <button class="btn" (click)="cancelEdit()">Zrusit</button>
            @if (editingId()) {
              <button class="btn btn-danger" (click)="deleteTemplate()">Smazat</button>
            }
          </div>
        </div>
      </div>
    }

    <!-- Template list -->
    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Nazev</th>
            <th>Aktivni</th>
            <th>Aktualizovano</th>
            <th>Akce</th>
          </tr>
        </thead>
        <tbody>
          @for (tmpl of templates(); track tmpl.id) {
            <tr>
              <td>{{ tmpl.name }}</td>
              <td>{{ tmpl.is_active ? 'Ano' : 'Ne' }}</td>
              <td>{{ tmpl.updated_at | date: 'short' }}</td>
              <td>
                <button class="btn btn-sm" (click)="editTemplate(tmpl)">Upravit</button>
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="4" style="text-align: center; color: #888">Zadne sablony</td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
})
export class TemplateListComponent implements OnInit {
  templates = signal<ContractTemplate[]>([]);
  editing = signal(false);
  editingId = signal<number | null>(null);

  placeholderHint =
    '{{client_name}}, {{total_price}}, {{deposit_amount}}, {{client_company}}, {{client_ico}}, {{date}}';

  formName = '';
  formBody = '';
  formActive = true;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.api.get<PaginatedResponse<ContractTemplate>>('contracts/contract-templates/').subscribe({
      next: (data) => this.templates.set(data.results),
    });
  }

  showForm(): void {
    this.formName = '';
    this.formBody = '';
    this.formActive = true;
    this.editingId.set(null);
    this.editing.set(true);
  }

  editTemplate(tmpl: ContractTemplate): void {
    this.formName = tmpl.name;
    this.formBody = tmpl.body_template;
    this.formActive = tmpl.is_active;
    this.editingId.set(tmpl.id);
    this.editing.set(true);
  }

  cancelEdit(): void {
    this.editing.set(false);
    this.editingId.set(null);
  }

  save(): void {
    const data = {
      name: this.formName,
      body_template: this.formBody,
      is_active: this.formActive,
    };

    const id = this.editingId();
    const req = id
      ? this.api.patch<ContractTemplate>(`contracts/contract-templates/${id}/`, data)
      : this.api.post<ContractTemplate>('contracts/contract-templates/', data);

    req.subscribe({
      next: () => {
        this.editing.set(false);
        this.editingId.set(null);
        this.loadTemplates();
      },
    });
  }

  deleteTemplate(): void {
    const id = this.editingId();
    if (!id || !confirm('Opravdu smazat tuto sablonu?')) return;
    this.api.delete(`contracts/contract-templates/${id}/`).subscribe({
      next: () => {
        this.editing.set(false);
        this.editingId.set(null);
        this.loadTemplates();
      },
    });
  }
}
