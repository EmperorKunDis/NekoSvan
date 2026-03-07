import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import { PaginatedResponse } from '../../core/services/deal.service';
import { StatCardComponent } from '../../shared/components/stat-card/stat-card.component';

interface Milestone {
  id: number;
  project: number;
  title: string;
  status: string;
  status_display: string;
  demo_url: string;
  dev_completed_at: string;
  project_deal_id: number;
  project_deal_company: string;
  description: string;
}

@Component({
  selector: 'app-qa-queue',
  standalone: true,
  imports: [RouterLink, DatePipe, FormsModule, StatCardComponent],
  template: `
    <div class="page-header">
      <h1>QA fronta</h1>
    </div>

    <div
      style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        margin-bottom: 16px;
      "
    >
      <app-stat-card [value]="milestones().length" label="K review"></app-stat-card>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Milestone</th>
            <th>Projekt</th>
            <th>Popis</th>
            <th>Demo</th>
            <th>Dev dokonceno</th>
            <th>Akce</th>
          </tr>
        </thead>
        <tbody>
          @for (m of milestones(); track m.id) {
            <tr>
              <td>{{ m.title }}</td>
              <td>
                <a [routerLink]="['/deals', m.project_deal_id, 'project']">{{
                  m.project_deal_company
                }}</a>
              </td>
              <td>{{ m.description || '-' }}</td>
              <td>
                @if (m.demo_url) {
                  <a [href]="m.demo_url" target="_blank" class="btn btn-secondary btn-sm"
                    >Demo ↗</a
                  >
                } @else {
                  -
                }
              </td>
              <td>{{ m.dev_completed_at | date: 'short' }}</td>
              <td>
                <button class="btn btn-success btn-sm" (click)="approve(m.id)">✓ Schvalit</button>
                <button class="btn btn-danger btn-sm" (click)="reject(m.id)">✗ Zamitnout</button>
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="6" style="text-align: center; color: #888">Zadne milniky k review</td>
            </tr>
          }
        </tbody>
      </table>
    </div>

    @if (showRejectModal()) {
      <div class="modal-overlay" (click)="closeRejectModal()">
        <div class="modal" (click)="$event.stopPropagation()">
          <h3>Duvod zamítnuti</h3>
          <textarea
            [(ngModel)]="rejectFeedback"
            rows="4"
            style="width: 100%; margin-bottom: 16px"
            placeholder="Popiste duvod zamítnuti..."
          ></textarea>
          <div style="display: flex; gap: 8px; justify-content: flex-end">
            <button class="btn btn-secondary" (click)="closeRejectModal()">Zrusit</button>
            <button class="btn btn-danger" (click)="confirmReject()">Zamitnout</button>
          </div>
        </div>
      </div>
    }
  `,
  styles: [
    `
      .btn-sm {
        padding: 4px 8px;
        font-size: 12px;
        margin-right: 4px;
      }
      .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }
      .modal {
        background: white;
        padding: 24px;
        border-radius: 8px;
        width: 400px;
        max-width: 90vw;
      }
    `,
  ],
})
export class QAQueueComponent implements OnInit {
  milestones = signal<Milestone[]>([]);
  showRejectModal = signal(false);
  rejectingMilestoneId = 0;
  rejectFeedback = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadMilestones();
  }

  loadMilestones(): void {
    this.api
      .get<PaginatedResponse<Milestone>>('projects/milestones/', { status: 'qa_review' })
      .subscribe({
        next: (data) => this.milestones.set(data.results),
      });
  }

  approve(id: number): void {
    this.api.post(`projects/milestones/${id}/qa_approve/`).subscribe({
      next: () => this.loadMilestones(),
    });
  }

  reject(id: number): void {
    this.rejectingMilestoneId = id;
    this.rejectFeedback = '';
    this.showRejectModal.set(true);
  }

  closeRejectModal(): void {
    this.showRejectModal.set(false);
    this.rejectingMilestoneId = 0;
    this.rejectFeedback = '';
  }

  confirmReject(): void {
    if (!this.rejectFeedback.trim()) return;
    this.api
      .post(`projects/milestones/${this.rejectingMilestoneId}/qa_reject/`, {
        feedback: this.rejectFeedback,
      })
      .subscribe({
        next: () => {
          this.closeRejectModal();
          this.loadMilestones();
        },
      });
  }
}
