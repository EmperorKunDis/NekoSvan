import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

interface Milestone {
  id: number;
  title: string;
  description: string;
  order: number;
  status: string;
  status_display: string;
  demo_url: string;
  due_date: string;
  client_feedback: string;
}

interface Project {
  id: number;
  status: string;
  status_display: string;
  milestones: Milestone[];
  progress_percent: number;
  start_date: string;
  estimated_end_date: string;
  implementation_plan: string;
}

interface MilestoneTemplate {
  id: number;
  name: string;
  category: string;
  is_default: boolean;
}

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './project-detail.component.html',
})
export class ProjectDetailComponent implements OnInit {
  dealId = 0;
  project = signal<Project | null>(null);
  templates = signal<MilestoneTemplate[]>([]);
  selectedTemplateId = 0;
  demoUrl = '';

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    protected auth: AuthService,
  ) {}

  ngOnInit(): void {
    this.dealId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadProject();
    this.loadTemplates();
  }

  loadProject(): void {
    this.api
      .get<{ results: Project[] }>('projects/projects/', { deal: String(this.dealId) })
      .subscribe({
        next: (data) => {
          if (data.results.length > 0) this.project.set(data.results[0]);
        },
      });
  }

  loadTemplates(): void {
    this.api.get<{ results: MilestoneTemplate[] }>('projects/milestone-templates/').subscribe({
      next: (data) => this.templates.set(data.results),
    });
  }

  createProject(): void {
    const url = this.selectedTemplateId
      ? `projects/projects/create-from-deal/${this.dealId}/?template_id=${this.selectedTemplateId}`
      : `projects/projects/create-from-deal/${this.dealId}/`;
    this.api.post(url).subscribe({
      next: () => this.loadProject(),
    });
  }

  devComplete(milestoneId: number): void {
    this.api
      .post(`projects/milestones/${milestoneId}/dev_complete/`, { demo_url: this.demoUrl })
      .subscribe({
        next: () => {
          this.loadProject();
          this.demoUrl = '';
        },
      });
  }

  qaApprove(milestoneId: number): void {
    this.api.post(`projects/milestones/${milestoneId}/qa_approve/`).subscribe({
      next: () => this.loadProject(),
    });
  }

  qaReject(milestoneId: number): void {
    const feedback = prompt('Duvod zamitnuti:');
    if (!feedback) return;
    this.api.post(`projects/milestones/${milestoneId}/qa_reject/`, { feedback }).subscribe({
      next: () => this.loadProject(),
    });
  }

  clientApprove(milestoneId: number): void {
    this.api.post(`projects/milestones/${milestoneId}/client_approve/`).subscribe({
      next: () => this.loadProject(),
    });
  }

  clientReject(milestoneId: number): void {
    const feedback = prompt('Připomínky klienta:');
    if (!feedback) return;
    this.api.post(`projects/milestones/${milestoneId}/client_reject/`, { feedback }).subscribe({
      next: () => this.loadProject(),
    });
  }
}
