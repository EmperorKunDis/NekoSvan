import { Component, OnInit, signal, effect } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from './core/services/auth.service';
import { NotificationService } from './core/services/notification.service';
import { ToastContainerComponent } from './shared/components/toast-container/toast-container.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ToastContainerComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  sidebarOpen = signal(false);

  constructor(
    protected auth: AuthService,
    protected notifications: NotificationService,
  ) {
    // React to auth state changes - connect notifications when user logs in
    effect(() => {
      const user = this.auth.currentUser();
      if (user) {
        this.notifications.loadUnreadCount();
        this.notifications.connectSSE();
      } else {
        this.notifications.disconnectSSE();
      }
    });
  }

  ngOnInit(): void {
    // Load user session - effect will handle notifications
    this.auth.loadCurrentUser();
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
