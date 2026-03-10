import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../core/services/api.service';

export interface Company {
  id: number;
  name: string;
  ico: string;
  dic?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  email?: string;
  phone?: string;
  website?: string;
  sector?: string;
  status: string;
  status_display: string;
  notes?: string;
  deal_count?: number;
  last_activity?: string;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreate {
  name: string;
  ico: string;
  dic?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  email?: string;
  phone?: string;
  website?: string;
  sector?: string;
  status?: string;
  notes?: string;
}

export interface CompanyUpdate extends Partial<CompanyCreate> {}

export interface Contact {
  id: number;
  company: number;
  name: string;
  email?: string;
  phone?: string;
  position?: string;
  notes?: string;
  created_at: string;
}

export interface ContactCreate {
  name: string;
  email?: string;
  phone?: string;
  position?: string;
  notes?: string;
}

export interface Communication {
  id: number;
  company: number;
  type: string;
  type_display: string;
  subject?: string;
  content: string;
  user: number;
  user_name: string;
  created_at: string;
}

export interface CommunicationCreate {
  type: string;
  subject?: string;
  content: string;
}

export interface CompanyDocument {
  id: number;
  company: number;
  name: string;
  file_url: string;
  uploaded_by: number;
  uploaded_by_name: string;
  uploaded_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({ providedIn: 'root' })
export class CompanyService {
  constructor(private api: ApiService) {}

  // Companies
  getCompanies(params?: { status?: string; sector?: string; search?: string }): Observable<PaginatedResponse<Company>> {
    return this.api.get('companies/', params as Record<string, string>);
  }

  getCompany(id: number): Observable<Company> {
    return this.api.get(`companies/${id}/`);
  }

  createCompany(data: CompanyCreate): Observable<Company> {
    return this.api.post('companies/', data);
  }

  updateCompany(id: number, data: CompanyUpdate): Observable<Company> {
    return this.api.patch(`companies/${id}/`, data);
  }

  deleteCompany(id: number): Observable<void> {
    return this.api.delete(`companies/${id}/`);
  }

  // Contacts
  getContacts(companyId: number): Observable<Contact[]> {
    return this.api.get(`companies/${companyId}/contacts/`);
  }

  createContact(companyId: number, data: ContactCreate): Observable<Contact> {
    return this.api.post(`companies/${companyId}/contacts/`, data);
  }

  deleteContact(companyId: number, contactId: number): Observable<void> {
    return this.api.delete(`companies/${companyId}/contacts/${contactId}/`);
  }

  // Communications
  getCommunications(companyId: number): Observable<Communication[]> {
    return this.api.get(`companies/${companyId}/communications/`);
  }

  createCommunication(companyId: number, data: CommunicationCreate): Observable<Communication> {
    return this.api.post(`companies/${companyId}/communications/`, data);
  }

  // Documents
  getDocuments(companyId: number): Observable<CompanyDocument[]> {
    return this.api.get(`companies/${companyId}/documents/`);
  }

  uploadDocument(companyId: number, file: File): Observable<CompanyDocument> {
    const formData = new FormData();
    formData.append('file', file);
    // Note: This will need special handling in ApiService or use HttpClient directly
    return this.api.post(`companies/${companyId}/documents/`, formData);
  }

  deleteDocument(companyId: number, docId: number): Observable<void> {
    return this.api.delete(`companies/${companyId}/documents/${docId}/`);
  }

  // Deals for company
  getDeals(companyId: number): Observable<any[]> {
    return this.api.get(`companies/${companyId}/deals/`);
  }

  createDealFromCompany(companyId: number, data: { description: string }): Observable<any> {
    return this.api.post(`companies/${companyId}/create-deal/`, data);
  }
}
