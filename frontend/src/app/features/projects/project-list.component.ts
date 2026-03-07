import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { ApiService } from '../../core/services/api.service';
import { PaginatedResponse } from '../../core/services/deal.service';
import { StatCardComponent } from '../../shared/components/stat-card/stat-card.component';

interface Project {
  id: number;
  deal: number;
  deal_company: string;
  status: string;
  status_display: string;
  progress: number;
  total_milestones: number;
  approved_milestones: number;
  created_at: string;
}

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports: [RouterLink, DatePipe, StatCardComponent],
  template: `
    <div class="page-header">
      <h1>Projekty ({{ totalCount() }})</h1>
    </div>

    <div
      style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 16px"
    >
      <app-stat-card [value]="totalCount()" label="Celkem projektu"></app-stat-card>
      <app-stat-card [value]="activeCount()" label="Aktivnich"></app-stat-card>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Firma</th>
            <th>Status</th>
            <th>Progress</th>
            <th>Milniky</th>
            <th>Vytvoreno</th>
          </tr>
        </thead>
        <tbody>
          @for (project of projects(); track project.id) {
            <tr>
              <td>
                <a [routerLink]="['/deals', project.deal, 'project']">{{ project.deal_company }}</a>
              </td>
              <td>{{ project.status_display }}</td>
              <td>{{ project.progress }}%</td>
              <td>{{ project.approved_milestones }} / {{ project.total_milestones }}</td>
              <td>{{ project.created_at | date: 'short' }}</td>
            </tr>
          } @empty {
            <tr>
              <td colspan="5" style="text-align: center; color: #888">Zadne projekty</td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
})
export class ProjectListComponent implements OnInit {
  projects = signal<Project[]>([]);
  totalCount = signal(0);
  activeCount = signal(0);

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<PaginatedResponse<Project>>('projects/projects/').subscribe({
      next: (data) => {
        this.projects.set(data.results);
        this.totalCount.set(data.count);
        this.activeCount.set(data.results.filter((p) => p.status === 'active').length);
      },
    });
  }
}
