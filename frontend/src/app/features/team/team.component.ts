import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { DatePipe } from '@angular/common';

interface TeamMember {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  bio: string;
  is_active: boolean;
  date_joined: string;
}

interface TeamData {
  is_master: boolean;
  role: string;
  role_display: string;
  members: TeamMember[];
}

@Component({
  selector: 'app-team',
  standalone: true,
  imports: [FormsModule, DatePipe],
  template: `
    <div class="team-page">
      <div class="header">
        <h1>Můj tým</h1>
        @if (teamData()?.is_master) {
          <button class="btn-primary" (click)="showCreateModal.set(true)">
            + Přidat člena
          </button>
        }
      </div>

      @if (loading()) {
        <p>Načítám...</p>
      } @else if (!teamData()?.is_master) {
        <div class="card">
          <p>Nemáte oprávnění spravovat tým.</p>
        </div>
      } @else {
        <div class="card">
          <p class="role-info">
            Role: <strong>{{ teamData()!.role_display }}</strong> —
            {{ teamData()!.members.length }} členů týmu
          </p>

          @if (teamData()!.members.length === 0) {
            <p class="empty">Zatím nemáte žádné členy týmu.</p>
          } @else {
            <table>
              <thead>
                <tr>
                  <th>Jméno</th>
                  <th>Email</th>
                  <th>Telefon</th>
                  <th>Registrace</th>
                  <th>Status</th>
                  <th>Akce</th>
                </tr>
              </thead>
              <tbody>
                @for (member of teamData()!.members; track member.id) {
                  <tr>
                    <td>
                      <strong>{{ member.first_name }} {{ member.last_name }}</strong>
                      <br />
                      <small>&#64;{{ member.username }}</small>
                    </td>
                    <td>{{ member.email }}</td>
                    <td>{{ member.phone || '—' }}</td>
                    <td>{{ member.date_joined | date: 'shortDate' }}</td>
                    <td>
                      <span
                        class="status"
                        [class.active]="member.is_active"
                        [class.inactive]="!member.is_active"
                      >
                        {{ member.is_active ? 'Aktivní' : 'Neaktivní' }}
                      </span>
                    </td>
                    <td>
                      <button
                        class="btn-small btn-danger"
                        (click)="deactivateMember(member)"
                        [disabled]="!member.is_active"
                      >
                        Deaktivovat
                      </button>
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          }
        </div>
      }

      <!-- Create Modal -->
      @if (showCreateModal()) {
        <div class="modal-backdrop" (click)="showCreateModal.set(false)">
          <div class="modal" (click)="$event.stopPropagation()">
            <h2>Nový člen týmu</h2>
            <form (ngSubmit)="createMember()">
              <div class="form-row">
                <div class="form-group">
                  <label>Uživatelské jméno *</label>
                  <input
                    type="text"
                    [(ngModel)]="newMember.username"
                    name="username"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>Email *</label>
                  <input
                    type="email"
                    [(ngModel)]="newMember.email"
                    name="email"
                    required
                  />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Jméno</label>
                  <input
                    type="text"
                    [(ngModel)]="newMember.first_name"
                    name="first_name"
                  />
                </div>
                <div class="form-group">
                  <label>Příjmení</label>
                  <input
                    type="text"
                    [(ngModel)]="newMember.last_name"
                    name="last_name"
                  />
                </div>
              </div>
              <div class="form-group">
                <label>Telefon</label>
                <input type="tel" [(ngModel)]="newMember.phone" name="phone" />
              </div>
              <div class="form-group">
                <label>Heslo *</label>
                <input
                  type="password"
                  [(ngModel)]="newMember.password"
                  name="password"
                  required
                />
              </div>

              @if (createError()) {
                <p class="error">{{ createError() }}</p>
              }

              <div class="modal-actions">
                <button
                  type="button"
                  class="btn-secondary"
                  (click)="showCreateModal.set(false)"
                >
                  Zrušit
                </button>
                <button
                  type="submit"
                  class="btn-primary"
                  [disabled]="creating()"
                >
                  {{ creating() ? 'Vytvářím...' : 'Vytvořit' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .team-page {
        max-width: 1000px;
        margin: 0 auto;
      }
      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
      }
      .card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
      .role-info {
        margin-bottom: 1rem;
        color: #666;
      }
      .empty {
        color: #888;
        text-align: center;
        padding: 2rem;
      }
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th,
      td {
        padding: 0.75rem;
        text-align: left;
        border-bottom: 1px solid #eee;
      }
      th {
        font-weight: 600;
        color: #555;
      }
      .status {
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
      }
      .status.active {
        background: #dcfce7;
        color: #166534;
      }
      .status.inactive {
        background: #fee2e2;
        color: #991b1b;
      }
      .btn-primary {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        cursor: pointer;
      }
      .btn-secondary {
        background: #e5e7eb;
        color: #374151;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        cursor: pointer;
      }
      .btn-small {
        padding: 0.35rem 0.75rem;
        font-size: 0.85rem;
        border-radius: 4px;
        cursor: pointer;
        border: none;
      }
      .btn-danger {
        background: #fee2e2;
        color: #991b1b;
      }
      .btn-danger:hover:not(:disabled) {
        background: #fecaca;
      }
      .btn-danger:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }
      .modal {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        width: 500px;
        max-width: 90%;
      }
      .modal h2 {
        margin-top: 0;
      }
      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
      }
      .form-group {
        margin-bottom: 1rem;
      }
      label {
        display: block;
        margin-bottom: 0.25rem;
        font-weight: 500;
      }
      input {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
      }
      .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        margin-top: 1rem;
      }
      .error {
        color: #ef4444;
        font-size: 0.9rem;
      }
    `,
  ],
})
export class TeamComponent implements OnInit {
  teamData = signal<TeamData | null>(null);
  loading = signal(true);
  showCreateModal = signal(false);
  creating = signal(false);
  createError = signal('');

  newMember = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    password: '',
  };

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadTeam();
  }

  loadTeam(): void {
    this.http.get<TeamData>('api/v1/accounts/team/').subscribe({
      next: (data) => {
        this.teamData.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  createMember(): void {
    this.creating.set(true);
    this.createError.set('');

    this.http.post<TeamMember>('api/v1/accounts/team/', this.newMember).subscribe({
      next: (member) => {
        this.creating.set(false);
        this.showCreateModal.set(false);
        this.newMember = {
          username: '',
          email: '',
          first_name: '',
          last_name: '',
          phone: '',
          password: '',
        };
        this.loadTeam();
      },
      error: (err) => {
        this.creating.set(false);
        this.createError.set(
          err.error?.username?.[0] ||
            err.error?.email?.[0] ||
            err.error?.password?.[0] ||
            'Chyba při vytváření'
        );
      },
    });
  }

  deactivateMember(member: TeamMember): void {
    if (!confirm(`Opravdu chcete deaktivovat ${member.first_name} ${member.last_name}?`)) {
      return;
    }
    this.http.delete(`api/v1/accounts/team/${member.id}/`).subscribe({
      next: () => this.loadTeam(),
    });
  }
}
