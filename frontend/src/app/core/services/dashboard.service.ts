import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface DashboardData {
  role: string;
  [key: string]: unknown;
}

@Injectable({ providedIn: 'root' })
export class DashboardService {
  constructor(private api: ApiService) {}

  getDashboard(): Observable<DashboardData> {
    return this.api.get('pipeline/dashboard/');
  }
}
