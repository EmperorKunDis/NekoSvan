import { Component, OnInit, signal } from '@angular/core';
import { DatePipe, CurrencyPipe } from '@angular/common';
import { ApiService } from '../../core/services/api.service';
import { PaginatedResponse } from '../../core/services/deal.service';
import { StatCardComponent } from '../../shared/components/stat-card/stat-card.component';

interface Payment {
  id: number;
  deal: number;
  deal_company: string;
  type: string;
  type_display: string;
  amount: string;
  status: string;
  status_display: string;
  due_date: string;
  paid_at: string | null;
  invoice_number: string;
}

@Component({
  selector: 'app-payment-list',
  standalone: true,
  imports: [DatePipe, CurrencyPipe, StatCardComponent],
  template: `
    <div class="page-header">
      <h1>Platby ({{ totalCount() }})</h1>
    </div>

    <div
      style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        margin-bottom: 16px;
      "
    >
      <app-stat-card [value]="totalCount()" label="Celkem plateb"></app-stat-card>
      <app-stat-card [value]="unpaidCount()" label="Nezaplacenych"></app-stat-card>
      <app-stat-card [value]="totalRevenue()" label="Celkovy prijem (CZK)"></app-stat-card>
    </div>

    <div class="card" style="margin-bottom: 16px">
      <div style="display: flex; gap: 8px">
        <button class="btn" [class.btn-primary]="filterStatus() === ''" (click)="setFilter('')">
          Vse
        </button>
        <button
          class="btn"
          [class.btn-primary]="filterStatus() === 'pending'"
          (click)="setFilter('pending')"
        >
          Cekajici
        </button>
        <button
          class="btn"
          [class.btn-primary]="filterStatus() === 'paid'"
          (click)="setFilter('paid')"
        >
          Zaplacene
        </button>
        <button
          class="btn"
          [class.btn-primary]="filterStatus() === 'overdue'"
          (click)="setFilter('overdue')"
        >
          Po splatnosti
        </button>
      </div>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Faktura</th>
            <th>Firma</th>
            <th>Typ</th>
            <th>Castka</th>
            <th>Status</th>
            <th>Splatnost</th>
            <th>Zaplaceno</th>
          </tr>
        </thead>
        <tbody>
          @for (p of payments(); track p.id) {
            <tr>
              <td>{{ p.invoice_number }}</td>
              <td>{{ p.deal_company }}</td>
              <td>{{ p.type_display }}</td>
              <td>{{ p.amount | currency: 'CZK' : 'symbol' : '1.0-0' }}</td>
              <td>{{ p.status_display }}</td>
              <td>{{ p.due_date | date: 'short' }}</td>
              <td>{{ p.paid_at ? (p.paid_at | date: 'short') : '-' }}</td>
            </tr>
          } @empty {
            <tr>
              <td colspan="7" style="text-align: center; color: #888">Zadne platby</td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
})
export class PaymentListComponent implements OnInit {
  payments = signal<Payment[]>([]);
  totalCount = signal(0);
  unpaidCount = signal(0);
  totalRevenue = signal('0');
  filterStatus = signal('');

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadPayments();
  }

  setFilter(status: string): void {
    this.filterStatus.set(status);
    this.loadPayments();
  }

  private loadPayments(): void {
    const params: Record<string, string> = {};
    if (this.filterStatus()) {
      params['status'] = this.filterStatus();
    }
    this.api.get<PaginatedResponse<Payment>>('contracts/payments/', params).subscribe({
      next: (data) => {
        this.payments.set(data.results);
        this.totalCount.set(data.count);
        this.unpaidCount.set(data.results.filter((p) => p.status !== 'paid').length);
        const revenue = data.results
          .filter((p) => p.status === 'paid')
          .reduce((sum, p) => sum + parseFloat(p.amount), 0);
        this.totalRevenue.set(revenue.toLocaleString('cs-CZ'));
      },
    });
  }
}
