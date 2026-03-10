import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  CompanyService,
  Company,
  Contact,
  Communication,
  CompanyDocument,
  ContactCreate,
  CommunicationCreate,
} from './company.service';
import { ToastService } from '../../core/services/toast.service';

type Tab = 'overview' | 'deals' | 'communications' | 'documents';

@Component({
  selector: 'app-company-detail',
  standalone: true,
  imports: [RouterLink, DatePipe, FormsModule],
  templateUrl: './company-detail.component.html',
})
export class CompanyDetailComponent implements OnInit {
  company = signal<Company | null>(null);
  activeTab = signal<Tab>('overview');

  // Overview tab
  contacts = signal<Contact[]>([]);
  showContactForm = signal(false);
  newContactName = signal('');
  newContactEmail = signal('');
  newContactPhone = signal('');
  newContactPosition = signal('');
  newContactNotes = signal('');

  // Deals tab
  deals = signal<any[]>([]);
  newDealDescription = signal('');
  showNewDealForm = signal(false);

  // Communications tab
  communications = signal<Communication[]>([]);
  showCommForm = signal(false);
  newCommType = signal('email');
  newCommSubject = signal('');
  newCommContent = signal('');

  commTypes = [
    { value: 'email', label: 'Email' },
    { value: 'phone', label: 'Telefon' },
    { value: 'meeting', label: 'Schůzka' },
    { value: 'note', label: 'Poznámka' },
  ];

  // Documents tab
  documents = signal<CompanyDocument[]>([]);
  uploadingFile = signal(false);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private companyService: CompanyService,
    private toast: ToastService,
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadCompany(id);
    this.loadContacts(id);
    this.loadDeals(id);
    this.loadCommunications(id);
    this.loadDocuments(id);
  }

  loadCompany(id: number): void {
    this.companyService.getCompany(id).subscribe({
      next: (c) => this.company.set(c),
      error: (err) => {
        console.error('Failed to load company:', err);
        this.toast.error('Nepodařilo se načíst firmu');
      },
    });
  }

  loadContacts(id: number): void {
    this.companyService.getContacts(id).subscribe({
      next: (c) => this.contacts.set(c),
      error: (err) => console.error('Failed to load contacts:', err),
    });
  }

  loadDeals(id: number): void {
    this.companyService.getDeals(id).subscribe({
      next: (d) => this.deals.set(d),
      error: (err) => console.error('Failed to load deals:', err),
    });
  }

  loadCommunications(id: number): void {
    this.companyService.getCommunications(id).subscribe({
      next: (c) => this.communications.set(c),
      error: (err) => console.error('Failed to load communications:', err),
    });
  }

  loadDocuments(id: number): void {
    this.companyService.getDocuments(id).subscribe({
      next: (d) => this.documents.set(d),
      error: (err) => console.error('Failed to load documents:', err),
    });
  }

  setTab(tab: Tab): void {
    this.activeTab.set(tab);
  }

  // Contact methods
  toggleContactForm(): void {
    this.showContactForm.update((v) => !v);
    if (!this.showContactForm()) {
      this.resetContactForm();
    }
  }

  resetContactForm(): void {
    this.newContactName.set('');
    this.newContactEmail.set('');
    this.newContactPhone.set('');
    this.newContactPosition.set('');
    this.newContactNotes.set('');
  }

  createContact(): void {
    const company = this.company();
    if (!company) return;

    if (!this.newContactName().trim()) {
      this.toast.error('Jméno kontaktu je povinné');
      return;
    }

    const data: ContactCreate = {
      name: this.newContactName(),
      email: this.newContactEmail() || undefined,
      phone: this.newContactPhone() || undefined,
      position: this.newContactPosition() || undefined,
      notes: this.newContactNotes() || undefined,
    };

    this.companyService.createContact(company.id, data).subscribe({
      next: () => {
        this.toast.success('Kontakt přidán');
        this.loadContacts(company.id);
        this.showContactForm.set(false);
        this.resetContactForm();
      },
      error: (err) => {
        console.error('Failed to create contact:', err);
        this.toast.error('Nepodařilo se přidat kontakt');
      },
    });
  }

  deleteContact(contactId: number): void {
    const company = this.company();
    if (!company) return;

    if (!confirm('Opravdu smazat tento kontakt?')) {
      return;
    }

    this.companyService.deleteContact(company.id, contactId).subscribe({
      next: () => {
        this.toast.success('Kontakt smazán');
        this.loadContacts(company.id);
      },
      error: (err) => {
        console.error('Failed to delete contact:', err);
        this.toast.error('Nepodařilo se smazat kontakt');
      },
    });
  }

  // Deal methods
  toggleNewDealForm(): void {
    this.showNewDealForm.update((v) => !v);
    if (!this.showNewDealForm()) {
      this.newDealDescription.set('');
    }
  }

  createDeal(): void {
    const company = this.company();
    if (!company) return;

    if (!this.newDealDescription().trim()) {
      this.toast.error('Popis dealu je povinný');
      return;
    }

    this.companyService
      .createDealFromCompany(company.id, { description: this.newDealDescription() })
      .subscribe({
        next: (deal) => {
          this.toast.success('Deal vytvořen');
          this.router.navigate(['/deals', deal.id]);
        },
        error: (err) => {
          console.error('Failed to create deal:', err);
          this.toast.error('Nepodařilo se vytvořit deal');
        },
      });
  }

  // Communication methods
  toggleCommForm(): void {
    this.showCommForm.update((v) => !v);
    if (!this.showCommForm()) {
      this.resetCommForm();
    }
  }

  resetCommForm(): void {
    this.newCommType.set('email');
    this.newCommSubject.set('');
    this.newCommContent.set('');
  }

  createCommunication(): void {
    const company = this.company();
    if (!company) return;

    if (!this.newCommContent().trim()) {
      this.toast.error('Obsah komunikace je povinný');
      return;
    }

    const data: CommunicationCreate = {
      type: this.newCommType(),
      subject: this.newCommSubject() || undefined,
      content: this.newCommContent(),
    };

    this.companyService.createCommunication(company.id, data).subscribe({
      next: () => {
        this.toast.success('Komunikace přidána');
        this.loadCommunications(company.id);
        this.showCommForm.set(false);
        this.resetCommForm();
      },
      error: (err) => {
        console.error('Failed to create communication:', err);
        this.toast.error('Nepodařilo se přidat komunikaci');
      },
    });
  }

  // Document methods
  onFileSelected(event: Event): void {
    const company = this.company();
    if (!company) return;

    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.uploadingFile.set(true);

    this.companyService.uploadDocument(company.id, file).subscribe({
      next: () => {
        this.toast.success('Dokument nahrán');
        this.loadDocuments(company.id);
        this.uploadingFile.set(false);
        input.value = '';
      },
      error: (err) => {
        console.error('Failed to upload document:', err);
        this.toast.error('Nepodařilo se nahrát dokument');
        this.uploadingFile.set(false);
      },
    });
  }

  deleteDocument(docId: number): void {
    const company = this.company();
    if (!company) return;

    if (!confirm('Opravdu smazat tento dokument?')) {
      return;
    }

    this.companyService.deleteDocument(company.id, docId).subscribe({
      next: () => {
        this.toast.success('Dokument smazán');
        this.loadDocuments(company.id);
      },
      error: (err) => {
        console.error('Failed to delete document:', err);
        this.toast.error('Nepodařilo se smazat dokument');
      },
    });
  }
}
