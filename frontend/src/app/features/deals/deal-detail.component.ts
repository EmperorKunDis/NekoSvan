import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { DealService, Deal, DealActivity } from '../../core/services/deal.service';
import { AuthService } from '../../core/services/auth.service';

// Which roles are "on duty" for each phase (used for visual highlight only)
const PHASE_PRIMARY_ROLE: Record<string, string[]> = {
  lead: ['adam'],
  qualification: ['vadim'],
  pricing: ['martin'],
  presentation: ['vadim'],
  contract: ['adam'],
  planning: ['martin'],
  development: ['martin', 'nekosvan'],
  completed: [],
};

@Component({
  selector: 'app-deal-detail',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './deal-detail.component.html',
})
export class DealDetailComponent implements OnInit {
  deal = signal<Deal | null>(null);
  activities = signal<DealActivity[]>([]);

  constructor(
    private route: ActivatedRoute,
    private dealService: DealService,
    protected auth: AuthService,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.dealService.get(id).subscribe({ next: (d) => this.deal.set(d) });
    this.dealService.getTimeline(id).subscribe({ next: (a) => this.activities.set(a) });
  }

  /** Is the current user the primary handler for this phase? (visual highlight) */
  isMyTurn(phase: string): boolean {
    const role = this.auth.userRole;
    if (role === 'nekosvan') return true;
    const primary = PHASE_PRIMARY_ROLE[phase] ?? [];
    return primary.includes(role);
  }

  advance(): void {
    const deal = this.deal();
    if (!deal) return;
    this.dealService.advance(deal.id).subscribe({
      next: (d) => {
        this.deal.set(d);
        this.loadTimeline();
      },
    });
  }

  private loadTimeline(): void {
    const deal = this.deal();
    if (!deal) return;
    this.dealService.getTimeline(deal.id).subscribe({ next: (a) => this.activities.set(a) });
  }
}
