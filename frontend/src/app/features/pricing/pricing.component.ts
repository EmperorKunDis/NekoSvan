import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CurrencyPipe } from '@angular/common';
import { ApiService } from '../../core/services/api.service';

interface ProposalItem {
  name: string;
  hours: number;
  rate: number;
  total: number;
}

@Component({
  selector: 'app-pricing',
  standalone: true,
  imports: [FormsModule, CurrencyPipe],
  templateUrl: './pricing.component.html',
})
export class PricingComponent implements OnInit {
  dealId = 0;
  dealInfo = signal('');
  autoCalc = signal<{ items: ProposalItem[]; total_price: number; deposit_amount: number } | null>(
    null,
  );
  items = signal<ProposalItem[]>([]);
  totalPrice = signal(0);
  depositAmount = signal(0);
  demoUrl = '';
  demoDescription = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService,
  ) {}

  ngOnInit(): void {
    this.dealId = Number(this.route.snapshot.paramMap.get('id'));
    this.api.get<{ client_company: string }>(`pipeline/deals/${this.dealId}/`).subscribe({
      next: (deal) => this.dealInfo.set(deal.client_company),
    });
    this.api
      .get<{
        items: ProposalItem[];
        total_price: number;
        deposit_amount: number;
      }>(`pricing/proposals/auto-calculate/${this.dealId}/`)
      .subscribe({
        next: (data) => {
          this.autoCalc.set(data);
          this.items.set(data.items);
          this.recalculate();
        },
      });
  }

  recalculate(): void {
    const total = this.items().reduce((sum, item) => sum + item.total, 0);
    this.totalPrice.set(total);
    this.depositAmount.set(Math.round(total * 0.3));
  }

  updateItemTotal(index: number): void {
    const items = [...this.items()];
    items[index].total = items[index].hours * items[index].rate;
    this.items.set(items);
    this.recalculate();
  }

  addItem(): void {
    this.items.update((items) => [...items, { name: '', hours: 0, rate: 1500, total: 0 }]);
  }

  removeItem(index: number): void {
    this.items.update((items) => items.filter((_, i) => i !== index));
    this.recalculate();
  }

  saveAndSend(): void {
    const data = {
      deal: this.dealId,
      items: this.items(),
      base_price: this.totalPrice(),
      total_price: this.totalPrice(),
      deposit_amount: this.depositAmount(),
      demo_url: this.demoUrl,
      demo_description: this.demoDescription,
    };
    this.api.post<{ id: number }>('pricing/proposals/', data).subscribe({
      next: (proposal) => {
        this.api.post(`pricing/proposals/${proposal.id}/send/`).subscribe({
          next: () => this.router.navigate(['/deals', this.dealId]),
        });
      },
    });
  }
}
