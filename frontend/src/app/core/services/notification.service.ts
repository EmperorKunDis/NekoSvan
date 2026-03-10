import { Injectable, signal, OnDestroy } from '@angular/core';
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
export class NotificationService implements OnDestroy {
  unreadCount = signal(0);
  private eventSource: EventSource | null = null;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

  constructor(private api: ApiService) {}

  loadUnreadCount(): void {
    this.api.get<{ unread_count: number }>('notifications/notifications/unread_count/').subscribe({
      next: (data) => this.unreadCount.set(data.unread_count),
    });
  }

  connectSSE(): void {
    if (this.eventSource) return;

    this.eventSource = new EventSource('/api/v1/notifications/stream/', { withCredentials: true });

    this.eventSource.addEventListener('unread_count', (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      this.unreadCount.set(data.unread_count);
    });

    this.eventSource.onerror = () => {
      this.disconnectSSE();
      // Auto-reconnect after 30s, fallback to polling
      this.reconnectTimeout = setTimeout(() => this.connectSSE(), 30000);
    };
  }

  disconnectSSE(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  markRead(id: number) {
    return this.api.post(`notifications/notifications/${id}/mark_read/`);
  }

  markAllRead() {
    return this.api.post('notifications/notifications/mark_all_read/');
  }

  ngOnDestroy(): void {
    this.disconnectSSE();
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
  }
}
