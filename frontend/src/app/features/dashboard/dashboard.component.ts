import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { DashboardService, DashboardData } from '../../core/services/dashboard.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  data = signal<DashboardData | null>(null);

  constructor(
    private dashboardService: DashboardService,
    protected auth: AuthService,
  ) {}

  ngOnInit(): void {
    this.dashboardService.getDashboard().subscribe({
      next: (data) => this.data.set(data),
    });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  asArray(val: unknown): Record<string, any>[] {
    return Array.isArray(val) ? val : [];
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  asRecord(val: unknown): Record<string, any> {
    return val && typeof val === 'object' ? (val as Record<string, any>) : {};
  }

  pipelineCount(d: DashboardData): number {
    const overview = d['pipeline_overview'];
    if (!overview || typeof overview !== 'object') return 0;
    return Object.keys(overview).length;
  }
}
