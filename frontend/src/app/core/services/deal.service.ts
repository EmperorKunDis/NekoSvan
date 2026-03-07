import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Deal {
  id: number;
  client_company: string;
  client_contact_name: string;
  client_email: string;
  client_phone: string;
  description: string;
  phase: string;
  phase_display: string;
  status: string;
  status_display: string;
  assigned_to: number | null;
  assigned_to_name: string;
  revision_count: number;
  portal_token: string;
  created_at: string;
  updated_at: string;
  phase_changed_at: string;
  created_by: number;
}

export interface DealActivity {
  id: number;
  deal: number;
  user: number;
  user_name: string;
  action: string;
  note: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({ providedIn: 'root' })
export class DealService {
  constructor(private api: ApiService) {}

  list(params?: Record<string, string>): Observable<PaginatedResponse<Deal>> {
    return this.api.get('pipeline/deals/', params);
  }

  get(id: number): Observable<Deal> {
    return this.api.get(`pipeline/deals/${id}/`);
  }

  create(data: Partial<Deal>): Observable<Deal> {
    return this.api.post('pipeline/deals/', data);
  }

  update(id: number, data: Partial<Deal>): Observable<Deal> {
    return this.api.patch(`pipeline/deals/${id}/`, data);
  }

  advance(id: number, note: string = ''): Observable<Deal> {
    return this.api.post(`pipeline/deals/${id}/advance/`, { note });
  }

  requestRevision(id: number, feedback: string): Observable<Deal> {
    return this.api.post(`pipeline/deals/${id}/revision/`, { feedback });
  }

  getTimeline(id: number): Observable<DealActivity[]> {
    return this.api.get(`pipeline/deals/${id}/timeline/`);
  }

  delete(id: number): Observable<void> {
    return this.api.delete(`pipeline/deals/${id}/`);
  }

  hardDelete(id: number): Observable<void> {
    return this.api.delete(`pipeline/deals/${id}/hard-delete/`);
  }
}
