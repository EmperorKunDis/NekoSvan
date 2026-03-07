import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
  template: `
    <div class="login-wrapper">
      <div class="login-card">
        <h1>NekoSvan</h1>
        <p class="subtitle">Workflow Management System</p>

        @if (auth.loginError()) {
          <div class="error-msg">{{ auth.loginError() }}</div>
        }

        <form (ngSubmit)="onSubmit()">
          <div class="field">
            <label for="username">Uzivatelske jmeno</label>
            <input
              id="username"
              type="text"
              [(ngModel)]="username"
              name="username"
              autocomplete="username"
              required
            />
          </div>
          <div class="field">
            <label for="password">Heslo</label>
            <input
              id="password"
              type="password"
              [(ngModel)]="password"
              name="password"
              autocomplete="current-password"
              required
            />
          </div>
          <button type="submit" [disabled]="!username || !password">Prihlasit se</button>
        </form>
      </div>
    </div>
  `,
  styles: `
    .login-wrapper {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background: #1a1a2e;
    }

    .login-card {
      background: #fff;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      width: 100%;
      max-width: 380px;

      h1 {
        margin: 0 0 4px;
        font-size: 28px;
        color: #1a1a2e;
        text-align: center;
      }

      .subtitle {
        text-align: center;
        color: #888;
        margin: 0 0 24px;
        font-size: 14px;
      }
    }

    .error-msg {
      background: #ffe3e3;
      color: #c92a2a;
      padding: 10px 14px;
      border-radius: 6px;
      margin-bottom: 16px;
      font-size: 14px;
    }

    .field {
      margin-bottom: 16px;

      label {
        display: block;
        font-size: 13px;
        color: #555;
        margin-bottom: 4px;
        font-weight: 500;
      }

      input {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 15px;
        box-sizing: border-box;
        transition: border-color 0.2s;

        &:focus {
          outline: none;
          border-color: #4a9eff;
          box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.15);
        }
      }
    }

    button[type='submit'] {
      width: 100%;
      padding: 12px;
      background: #1a1a2e;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
      margin-top: 8px;

      &:hover:not(:disabled) {
        background: #2a2a4e;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  `,
})
export class LoginComponent {
  username = '';
  password = '';

  constructor(protected auth: AuthService) {}

  onSubmit(): void {
    this.auth.login(this.username, this.password);
  }
}
