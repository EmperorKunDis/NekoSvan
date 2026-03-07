import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CurrencyPipe } from '@angular/common';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-contract',
  standalone: true,
  imports: [CurrencyPipe],
  templateUrl: './contract.component.html',
})
export class ContractComponent implements OnInit {
  dealId = 0;
  dealInfo = signal('');
  contract = signal<Record<string, any> | null>(null);
  payments = signal<Record<string, any>[]>([]);

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
  ) {}

  ngOnInit(): void {
    this.dealId = Number(this.route.snapshot.paramMap.get('id'));
    this.api.get<{ client_company: string }>(`pipeline/deals/${this.dealId}/`).subscribe({
      next: (deal) => this.dealInfo.set(deal.client_company),
    });
    this.loadContract();
    this.loadPayments();
  }

  loadContract(): void {
    this.api
      .get<{
        results: Record<string, any>[];
      }>('contracts/contracts/', { deal: String(this.dealId) })
      .subscribe({
        next: (data) => {
          if (data.results.length > 0) this.contract.set(data.results[0]);
        },
      });
  }

  loadPayments(): void {
    this.api
      .get<{
        results: Record<string, any>[];
      }>('contracts/payments/', { deal: String(this.dealId) })
      .subscribe({
        next: (data) => this.payments.set(data.results),
      });
  }

  generateContract(): void {
    this.api.post(`contracts/contracts/generate/${this.dealId}/`).subscribe({
      next: () => this.loadContract(),
    });
  }

  sendContract(): void {
    const c = this.contract();
    if (!c) return;
    this.api.post(`contracts/contracts/${c['id']}/send_to_client/`).subscribe({
      next: () => this.loadContract(),
    });
  }

  markSigned(): void {
    const c = this.contract();
    if (!c) return;
    this.api.post(`contracts/contracts/${c['id']}/mark_signed/`).subscribe({
      next: () => this.loadContract(),
    });
  }

  markPaid(paymentId: number): void {
    this.api.post(`contracts/payments/${paymentId}/mark_paid/`).subscribe({
      next: () => this.loadPayments(),
    });
  }
}
