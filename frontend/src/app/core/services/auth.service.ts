import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  company: number | null;
  company_name: string;
  phone: string;
  is_master: boolean;
  bio: string;
  avatar: string | null;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  currentUser = signal<User | null>(null);
  isLoading = signal(true);
  loginError = signal('');

  private baseUrl = 'api/v1/accounts';

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {}

  loadCurrentUser(): void {
    this.isLoading.set(true);
    this.http.get<User>(`${this.baseUrl}/users/me/`).subscribe({
      next: (user) => {
        this.currentUser.set(user);
        this.isLoading.set(false);
      },
      error: () => {
        this.currentUser.set(null);
        this.isLoading.set(false);
      },
    });
  }

  fetchCsrfToken(): Observable<{ csrfToken: string }> {
    return this.http.get<{ csrfToken: string }>(`${this.baseUrl}/csrf/`);
  }

  login(username: string, password: string): void {
    this.loginError.set('');
    // First get CSRF token, then login
    this.fetchCsrfToken().subscribe({
      next: () => {
        this.http.post<User>(`${this.baseUrl}/login/`, { username, password }).subscribe({
          next: (user) => {
            this.currentUser.set(user);
            this.router.navigate(['/dashboard']);
          },
          error: () => {
            this.loginError.set('Neplatne prihlasovaci udaje');
          },
        });
      },
    });
  }

  logout(): void {
    this.http.post(`${this.baseUrl}/logout/`, {}).subscribe({
      next: () => {
        this.currentUser.set(null);
        this.router.navigate(['/login']);
      },
    });
  }

  get isAuthenticated(): boolean {
    return this.currentUser() !== null;
  }

  get userRole(): string {
    return this.currentUser()?.role ?? '';
  }
}
