import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CompanyService, Company } from './company.service';

interface StatusFilter {
  value: string;
  label: string;
}

interface SectorFilter {
  value: string;
  label: string;
}

const STATUSES: StatusFilter[] = [
  { value: '', label: 'Všechny' },
  { value: 'active', label: 'Aktivní' },
  { value: 'inactive', label: 'Neaktivní' },
  { value: 'prospect', label: 'Potenciální' },
];

const SECTORS: SectorFilter[] = [
  { value: '', label: 'Všechny' },
  { value: 'it', label: 'IT' },
  { value: 'finance', label: 'Finance' },
  { value: 'manufacturing', label: 'Výroba' },
  { value: 'retail', label: 'Maloobchod' },
  { value: 'healthcare', label: 'Zdravotnictví' },
  { value: 'education', label: 'Vzdělávání' },
  { value: 'other', label: 'Ostatní' },
];

@Component({
  selector: 'app-company-list',
  standalone: true,
  imports: [RouterLink, DatePipe, FormsModule],
  templateUrl: './company-list.component.html',
})
export class CompanyListComponent implements OnInit {
  companies = signal<Company[]>([]);
  totalCount = signal(0);
  
  filterStatus = signal('');
  filterSector = signal('');
  searchQuery = signal('');

  statuses = STATUSES;
  sectors = SECTORS;

  constructor(private companyService: CompanyService) {}

  ngOnInit(): void {
    this.loadCompanies();
  }

  loadCompanies(): void {
    const params: Record<string, string> = {};
    
    if (this.filterStatus()) {
      params['status'] = this.filterStatus();
    }
    if (this.filterSector()) {
      params['sector'] = this.filterSector();
    }
    if (this.searchQuery()) {
      params['search'] = this.searchQuery();
    }

    this.companyService.getCompanies(params).subscribe({
      next: (data) => {
        this.companies.set(data.results);
        this.totalCount.set(data.count);
      },
      error: (err) => {
        console.error('Failed to load companies:', err);
      },
    });
  }

  onStatusChange(status: string): void {
    this.filterStatus.set(status);
    this.loadCompanies();
  }

  onSectorChange(sector: string): void {
    this.filterSector.set(sector);
    this.loadCompanies();
  }

  onSearch(): void {
    this.loadCompanies();
  }

  deleteCompany(company: Company, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    
    if (!confirm(`Opravdu smazat firmu "${company.name}"?`)) {
      return;
    }

    this.companyService.deleteCompany(company.id).subscribe({
      next: () => this.loadCompanies(),
      error: (err) => {
        console.error('Failed to delete company:', err);
        alert('Nepodařilo se smazat firmu.');
      },
    });
  }
}
