import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CompanyService, CompanyCreate, CompanyUpdate, Company } from './company.service';
import { ToastService } from '../../core/services/toast.service';

@Component({
  selector: 'app-company-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './company-form.component.html',
})
export class CompanyFormComponent implements OnInit {
  isEditMode = signal(false);
  companyId = signal<number | null>(null);
  isLoading = signal(false);

  // Form fields
  name = signal('');
  ico = signal('');
  dic = signal('');
  address = signal('');
  city = signal('');
  postalCode = signal('');
  email = signal('');
  phone = signal('');
  website = signal('');
  sector = signal('');
  status = signal('active');
  notes = signal('');

  sectors = [
    { value: '', label: '— Vyberte sektor —' },
    { value: 'it', label: 'IT' },
    { value: 'finance', label: 'Finance' },
    { value: 'manufacturing', label: 'Výroba' },
    { value: 'retail', label: 'Maloobchod' },
    { value: 'healthcare', label: 'Zdravotnictví' },
    { value: 'education', label: 'Vzdělávání' },
    { value: 'other', label: 'Ostatní' },
  ];

  statuses = [
    { value: 'active', label: 'Aktivní' },
    { value: 'inactive', label: 'Neaktivní' },
    { value: 'prospect', label: 'Potenciální' },
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private companyService: CompanyService,
    private toast: ToastService,
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode.set(true);
      this.companyId.set(Number(id));
      this.loadCompany(Number(id));
    }
  }

  loadCompany(id: number): void {
    this.isLoading.set(true);
    this.companyService.getCompany(id).subscribe({
      next: (company) => {
        this.name.set(company.name);
        this.ico.set(company.ico);
        this.dic.set(company.dic || '');
        this.address.set(company.address || '');
        this.city.set(company.city || '');
        this.postalCode.set(company.postal_code || '');
        this.email.set(company.email || '');
        this.phone.set(company.phone || '');
        this.website.set(company.website || '');
        this.sector.set(company.sector || '');
        this.status.set(company.status);
        this.notes.set(company.notes || '');
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Failed to load company:', err);
        this.toast.error('Nepodařilo se načíst firmu');
        this.isLoading.set(false);
      },
    });
  }

  onSubmit(): void {
    if (!this.name().trim()) {
      this.toast.error('Název firmy je povinný');
      return;
    }

    if (!this.ico().trim()) {
      this.toast.error('IČO je povinné');
      return;
    }

    this.isLoading.set(true);

    const data: CompanyCreate | CompanyUpdate = {
      name: this.name(),
      ico: this.ico(),
      dic: this.dic() || undefined,
      address: this.address() || undefined,
      city: this.city() || undefined,
      postal_code: this.postalCode() || undefined,
      email: this.email() || undefined,
      phone: this.phone() || undefined,
      website: this.website() || undefined,
      sector: this.sector() || undefined,
      status: this.status(),
      notes: this.notes() || undefined,
    };

    const request = this.isEditMode()
      ? this.companyService.updateCompany(this.companyId()!, data)
      : this.companyService.createCompany(data as CompanyCreate);

    request.subscribe({
      next: (company) => {
        this.toast.success(
          this.isEditMode() ? 'Firma byla aktualizována' : 'Firma byla vytvořena'
        );
        this.router.navigate(['/companies', company.id]);
      },
      error: (err) => {
        console.error('Failed to save company:', err);
        this.toast.error('Nepodařilo se uložit firmu');
        this.isLoading.set(false);
      },
    });
  }

  cancel(): void {
    if (this.isEditMode()) {
      this.router.navigate(['/companies', this.companyId()]);
    } else {
      this.router.navigate(['/companies']);
    }
  }
}
