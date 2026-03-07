import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from './core/services/auth.service';
import { NotificationService } from './core/services/notification.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  sidebarOpen = signal(false);

  constructor(
    protected auth: AuthService,
    protected notifications: NotificationService,
  ) {}

  ngOnInit(): void {
    this.auth.loadCurrentUser();
    this.notifications.loadUnreadCount();
    setInterval(() => this.notifications.loadUnreadCount(), 30000);
  }

  toggleSidebar(): void {
    this.sidebarOpen.update((v) => !v);
  }

  closeSidebar(): void {
    this.sidebarOpen.set(false);
  }

  logout(): void {
    this.auth.logout();
  }
}
