import { Component, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common';
import { ApiService } from '../../core/services/api.service';
import { NotificationService, Notification } from '../../core/services/notification.service';

@Component({
  selector: 'app-notification-list',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './notification-list.component.html',
})
export class NotificationListComponent implements OnInit {
  notifications = signal<Notification[]>([]);

  constructor(
    private api: ApiService,
    private notificationService: NotificationService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.api
      .get<{ results: Notification[] }>('notifications/notifications/', { ordering: '-created_at' })
      .subscribe({
        next: (data) => this.notifications.set(data.results),
      });
  }

  markRead(notification: Notification): void {
    if (!notification.read) {
      this.notificationService.markRead(notification.id).subscribe({
        next: () => {
          this.loadNotifications();
          this.notificationService.loadUnreadCount();
        },
      });
    }
    if (notification.link) {
      this.router.navigateByUrl(notification.link);
    }
  }

  markAllRead(): void {
    this.notificationService.markAllRead().subscribe({
      next: () => {
        this.loadNotifications();
        this.notificationService.loadUnreadCount();
      },
    });
  }
}
