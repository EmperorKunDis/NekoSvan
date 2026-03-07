import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import { PaginatedResponse } from '../../core/services/deal.service';

interface TemplateItem {
  id: number;
  title: string;
  description: string;
  order: number;
  estimated_hours: number;
}

interface MilestoneTemplate {
  id: number;
  name: string;
  category: string;
  is_default: boolean;
  is_active: boolean;
  items: TemplateItem[];
}

@Component({
  selector: 'app-milestone-templates',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="page-header">
      <h1>Šablony milníků</h1>
    </div>

    @for (t of templates(); track t.id) {
      <div class="card" style="margin-bottom: 24px">
        <div class="card-header">
          <h3>
            {{ t.name }}
            <span style="font-weight: normal; font-size: 14px; color: #888"
              >({{ t.category }})</span
            >
            @if (t.is_default) {
              <span
                style="
                  background: #2ecc71;
                  color: white;
                  padding: 2px 8px;
                  border-radius: 4px;
                  font-size: 12px;
                  margin-left: 8px;
                "
                >Výchozí</span
              >
            }
          </h3>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th style="width: 50px">Pořadí</th>
              <th>Název</th>
              <th>Popis</th>
              <th style="width: 100px">Hodiny</th>
              <th style="width: 100px">Akce</th>
            </tr>
          </thead>
          <tbody>
            @for (item of t.items; track item.id) {
              <tr>
                <td>{{ item.order }}</td>
                <td>
                  <input type="text" [(ngModel)]="item.title" class="form-input" />
                </td>
                <td>
                  <input
                    type="text"
                    [(ngModel)]="item.description"
                    class="form-input"
                    style="width: 100%"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    [(ngModel)]="item.estimated_hours"
                    class="form-input"
                    style="width: 60px"
                  />
                </td>
                <td>
                  <button class="btn btn-primary btn-sm" (click)="saveItem(item)">Uložit</button>
                </td>
              </tr>
            }
          </tbody>
        </table>

        <div style="padding: 16px; border-top: 1px solid #eee">
          <h4 style="margin-bottom: 12px">Přidat milník</h4>
          <div style="display: flex; gap: 8px; flex-wrap: wrap">
            <input
              type="text"
              [(ngModel)]="newItems[t.id].title"
              placeholder="Název"
              class="form-input"
            />
            <input
              type="text"
              [(ngModel)]="newItems[t.id].description"
              placeholder="Popis"
              class="form-input"
              style="flex: 1"
            />
            <input
              type="number"
              [(ngModel)]="newItems[t.id].estimated_hours"
              placeholder="Hodiny"
              class="form-input"
              style="width: 80px"
            />
            <button class="btn btn-success" (click)="addItem(t.id)">Přidat</button>
          </div>
        </div>
      </div>
    }
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
export class MilestoneTemplatesComponent implements OnInit {
  templates = signal<MilestoneTemplate[]>([]);
  newItems: Record<number, { title: string; description: string; estimated_hours: number }> = {};

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.api.get<PaginatedResponse<MilestoneTemplate>>('projects/milestone-templates/').subscribe({
      next: (data) => {
        this.templates.set(data.results);
        data.results.forEach((t) => {
          this.newItems[t.id] = { title: '', description: '', estimated_hours: 0 };
        });
      },
    });
  }

  saveItem(item: TemplateItem): void {
    // Note: We'd need a separate endpoint for updating items
    // For now, just show alert
    alert('Položka uložena (implementace na backendu potřebná)');
  }

  addItem(templateId: number): void {
    const newItem = this.newItems[templateId];
    if (!newItem.title.trim()) return;

    const template = this.templates().find((t) => t.id === templateId);
    const order = template ? template.items.length + 1 : 1;

    this.api
      .post(`projects/milestone-templates/${templateId}/add_item/`, {
        ...newItem,
        order,
      })
      .subscribe({
        next: () => {
          this.newItems[templateId] = { title: '', description: '', estimated_hours: 0 };
          this.loadData();
        },
      });
  }
}
