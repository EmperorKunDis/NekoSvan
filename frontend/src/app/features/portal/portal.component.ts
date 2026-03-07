import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CurrencyPipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-portal',
  standalone: true,
  imports: [FormsModule, CurrencyPipe],
  templateUrl: './portal.component.html',
})
export class PortalComponent implements OnInit {
  token = '';
  data = signal<Record<string, any> | null>(null);
  feedback = '';
  error = signal('');

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
  ) {}

  ngOnInit(): void {
    this.token = this.route.snapshot.paramMap.get('token') ?? '';
    this.loadData();
  }

  loadData(): void {
    this.http.get(`api/v1/portal/${this.token}/`).subscribe({
      next: (data) => this.data.set(data as Record<string, any>),
      error: () => this.error.set('Neplatny odkaz'),
    });
  }

  acceptProposal(): void {
    this.http.post(`api/v1/portal/${this.token}/proposal/accept/`, {}).subscribe({
      next: () => this.loadData(),
    });
  }

  rejectProposal(): void {
    if (!this.feedback) return;
    this.http
      .post(`api/v1/portal/${this.token}/proposal/reject/`, { feedback: this.feedback })
      .subscribe({
        next: () => {
          this.loadData();
          this.feedback = '';
        },
      });
  }

  approveMilestone(id: number): void {
    this.http.post(`api/v1/portal/${this.token}/milestone/${id}/approve/`, {}).subscribe({
      next: () => this.loadData(),
    });
  }

  rejectMilestone(id: number): void {
    const fb = prompt('Pripominky:');
    if (!fb) return;
    this.http
      .post(`api/v1/portal/${this.token}/milestone/${id}/reject/`, { feedback: fb })
      .subscribe({
        next: () => this.loadData(),
      });
  }

  asRecord(val: unknown): Record<string, any> {
    return val && typeof val === 'object' ? (val as Record<string, any>) : {};
  }

  asArray(val: unknown): Record<string, any>[] {
    return Array.isArray(val) ? val : [];
  }
}
