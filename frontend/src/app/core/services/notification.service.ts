import { Injectable, signal } from '@angular/core';
import { ApiService } from './api.service';

export interface Notification {
  id: number;
  title: string;
  message: string;
  link: string;
  read: boolean;
  created_at: string;
  deal: number | null;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  unreadCount = signal(0);

  constructor(private api: ApiService) {}

  loadUnreadCount(): void {
    this.api.get<{ unread_count: number }>('notifications/notifications/unread_count/').subscribe({
      next: (data) => this.unreadCount.set(data.unread_count),
    });
  }

  markRead(id: number) {
    return this.api.post(`notifications/notifications/${id}/mark_read/`);
  }

  markAllRead() {
    return this.api.post('notifications/notifications/mark_all_read/');
  }
}
