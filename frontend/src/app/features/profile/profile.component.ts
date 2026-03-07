import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface Profile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  bio: string;
  avatar: string | null;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="profile-page">
      <h1>Můj profil</h1>

      @if (loading()) {
        <p>Načítám...</p>
      } @else if (profile()) {
        <div class="profile-sections">
          <!-- Profile Info -->
          <div class="card">
            <h3>Osobní údaje</h3>
            <form (ngSubmit)="saveProfile()">
              <div class="form-row">
                <div class="form-group">
                  <label>Uživatelské jméno</label>
                  <input type="text" [value]="profile()!.username" disabled />
                </div>
                <div class="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    [(ngModel)]="profile()!.email"
                    name="email"
                  />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>Jméno</label>
                  <input
                    type="text"
                    [(ngModel)]="profile()!.first_name"
                    name="first_name"
                  />
                </div>
                <div class="form-group">
                  <label>Příjmení</label>
                  <input
                    type="text"
                    [(ngModel)]="profile()!.last_name"
                    name="last_name"
                  />
                </div>
              </div>
              <div class="form-group">
                <label>Telefon</label>
                <input type="tel" [(ngModel)]="profile()!.phone" name="phone" />
              </div>
              <div class="form-group">
                <label>Bio</label>
                <textarea
                  [(ngModel)]="profile()!.bio"
                  name="bio"
                  rows="3"
                ></textarea>
              </div>
              <button type="submit" class="btn-primary" [disabled]="saving()">
                {{ saving() ? 'Ukládám...' : 'Uložit změny' }}
              </button>
              @if (profileMessage()) {
                <span class="message success">{{ profileMessage() }}</span>
              }
            </form>
          </div>

          <!-- Change Password -->
          <div class="card">
            <h3>Změna hesla</h3>
            <form (ngSubmit)="changePassword()">
              <div class="form-group">
                <label>Staré heslo</label>
                <input
                  type="password"
                  [(ngModel)]="passwordForm.old_password"
                  name="old_password"
                  required
                />
              </div>
              <div class="form-group">
                <label>Nové heslo</label>
                <input
                  type="password"
                  [(ngModel)]="passwordForm.new_password"
                  name="new_password"
                  required
                />
              </div>
              <div class="form-group">
                <label>Potvrdit nové heslo</label>
                <input
                  type="password"
                  [(ngModel)]="passwordForm.new_password_confirm"
                  name="new_password_confirm"
                  required
                />
              </div>
              <button
                type="submit"
                class="btn-primary"
                [disabled]="changingPassword()"
              >
                {{ changingPassword() ? 'Měním...' : 'Změnit heslo' }}
              </button>
              @if (passwordMessage()) {
                <span
                  class="message"
                  [class.success]="passwordSuccess()"
                  [class.error]="!passwordSuccess()"
                >
                  {{ passwordMessage() }}
                </span>
              }
            </form>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .profile-page {
        max-width: 800px;
        margin: 0 auto;
      }
      .profile-sections {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
      }
      .card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
      h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        color: #333;
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
        color: #555;
      }
      input,
      textarea {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
      }
      input:disabled {
        background: #f5f5f5;
        color: #888;
      }
      .btn-primary {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1rem;
      }
      .btn-primary:hover:not(:disabled) {
        background: #2563eb;
      }
      .btn-primary:disabled {
        background: #93c5fd;
        cursor: not-allowed;
      }
      .message {
        margin-left: 1rem;
        font-size: 0.9rem;
      }
      .message.success {
        color: #22c55e;
      }
      .message.error {
        color: #ef4444;
      }
    `,
  ],
})
export class ProfileComponent implements OnInit {
  profile = signal<Profile | null>(null);
  loading = signal(true);
  saving = signal(false);
  profileMessage = signal('');

  passwordForm = {
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  };
  changingPassword = signal(false);
  passwordMessage = signal('');
  passwordSuccess = signal(false);

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.http.get<Profile>('api/v1/accounts/profile/').subscribe({
      next: (data) => {
        this.profile.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  saveProfile(): void {
    this.saving.set(true);
    this.profileMessage.set('');

    this.http.patch<Profile>('api/v1/accounts/profile/', this.profile()).subscribe({
      next: (data) => {
        this.profile.set(data);
        this.saving.set(false);
        this.profileMessage.set('Uloženo!');
        setTimeout(() => this.profileMessage.set(''), 3000);
      },
      error: () => {
        this.saving.set(false);
        this.profileMessage.set('Chyba při ukládání');
      },
    });
  }

  changePassword(): void {
    this.changingPassword.set(true);
    this.passwordMessage.set('');

    this.http
      .post('api/v1/accounts/profile/password/', this.passwordForm)
      .subscribe({
        next: () => {
          this.changingPassword.set(false);
          this.passwordSuccess.set(true);
          this.passwordMessage.set('Heslo změněno!');
          this.passwordForm = {
            old_password: '',
            new_password: '',
            new_password_confirm: '',
          };
          setTimeout(() => this.passwordMessage.set(''), 3000);
        },
        error: (err) => {
          this.changingPassword.set(false);
          this.passwordSuccess.set(false);
          const msg =
            err.error?.old_password?.[0] ||
            err.error?.new_password?.[0] ||
            err.error?.new_password_confirm?.[0] ||
            'Chyba při změně hesla';
          this.passwordMessage.set(msg);
        },
      });
  }
}
