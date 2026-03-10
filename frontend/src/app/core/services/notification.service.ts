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
  private pollingInterval: ReturnType<typeof setInterval> | null = null;
  private sseFailCount = 0;
  private readonly SSE_MAX_FAILS = 3;

  constructor(private api: ApiService) {}

  loadUnreadCount(): void {
    this.api.get<{ unread_count: number }>('notifications/notifications/unread_count/').subscribe({
      next: (data) => this.unreadCount.set(data.unread_count),
      error: () => console.warn('Failed to load unread count'),
    });
  }

  connectSSE(): void {
    if (this.eventSource || this.sseFailCount >= this.SSE_MAX_FAILS) {
      // Fall back to polling if SSE failed too many times
      if (this.sseFailCount >= this.SSE_MAX_FAILS && !this.pollingInterval) {
        this.startPolling();
      }
      return;
    }

    this.eventSource = new EventSource('/api/v1/notifications/stream/', { withCredentials: true });

    this.eventSource.addEventListener('unread_count', (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      this.unreadCount.set(data.unread_count);
      this.sseFailCount = 0; // Reset fail count on success
    });

    this.eventSource.onerror = () => {
      this.sseFailCount++;
      this.disconnectSSE();
      
      if (this.sseFailCount >= this.SSE_MAX_FAILS) {
        console.warn('SSE failed multiple times, switching to polling');
        this.startPolling();
      } else {
        // Try reconnecting SSE
        this.reconnectTimeout = setTimeout(() => this.connectSSE(), 30000);
      }
    };
  }

  disconnectSSE(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  private startPolling(): void {
    if (this.pollingInterval) return;
    
    // Poll every 30 seconds
    this.loadUnreadCount();
    this.pollingInterval = setInterval(() => this.loadUnreadCount(), 30000);
  }

  private stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
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
    this.stopPolling();
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
  }
}
