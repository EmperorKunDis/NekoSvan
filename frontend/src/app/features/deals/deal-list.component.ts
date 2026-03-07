import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { DealService, Deal, PaginatedResponse } from '../../core/services/deal.service';
import { AuthService } from '../../core/services/auth.service';

interface PhaseFilter {
  value: string;
  label: string;
}

const ALL_PHASES: PhaseFilter[] = [
  { value: '', label: 'Vse' },
  { value: 'lead', label: 'Lead' },
  { value: 'qualification', label: 'Kvalifikace' },
  { value: 'pricing', label: 'Cenotvorba' },
  { value: 'presentation', label: 'Prezentace' },
  { value: 'contract', label: 'Smlouva' },
  { value: 'planning', label: 'Planovani' },
  { value: 'development', label: 'Vyvoj' },
  { value: 'completed', label: 'Dokonceno' },
];

// Primary phases per role — used for visual highlight only
const ROLE_PRIMARY_PHASES: Record<string, string[]> = {
  adam: ['lead', 'contract', 'completed'],
  vadim: ['qualification', 'presentation'],
  martin: ['pricing', 'planning', 'development'],
};

@Component({
  selector: 'app-deal-list',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './deal-list.component.html',
})
export class DealListComponent implements OnInit {
  deals = signal<Deal[]>([]);
  totalCount = signal(0);
  filterPhase = signal('');

  // All phases visible to all roles
  phases = ALL_PHASES;

  constructor(
    private dealService: DealService,
    protected auth: AuthService,
  ) {}

  ngOnInit(): void {
    this.loadDeals();
  }

  /** Is this phase a primary phase for the current user's role? */
  isMyPhase(phase: string): boolean {
    const role = this.auth.userRole;
    if (role === 'nekosvan') return true;
    const primary = ROLE_PRIMARY_PHASES[role];
    return !primary || primary.includes(phase);
  }

  loadDeals(): void {
    const params: Record<string, string> = {};
    if (this.filterPhase()) {
      params['phase'] = this.filterPhase();
    }
    this.dealService.list(params).subscribe({
      next: (data) => {
        this.deals.set(data.results);
        this.totalCount.set(data.count);
      },
    });
  }

  setPhaseFilter(phase: string): void {
    this.filterPhase.set(phase);
    this.loadDeals();
  }

  deleteDeal(deal: Deal, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    if (!confirm(`Opravdu smazat "${deal.client_company}"?`)) {
      return;
    }
    this.dealService.delete(deal.id).subscribe({
      next: () => this.loadDeals(),
    });
  }
}
