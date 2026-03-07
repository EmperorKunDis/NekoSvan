import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';

interface Document {
  id: string;
  title: string;
  document_type: string;
  document_type_display: string;
  file_url: string;
  file_type: string;
  deal: number | null;
  project: number | null;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-document-list',
  standalone: true,
  imports: [RouterLink, FormsModule, DatePipe],
  template: `
    <div class="page-header">
      <h1>Dokumenty</h1>
      <button class="btn btn-primary" (click)="showUploadModal.set(true)">
        + Nahrát dokument
      </button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Název</th>
            <th>Typ</th>
            <th>Formát</th>
            <th>Vytvořil</th>
            <th>Upraveno</th>
            <th>Akce</th>
          </tr>
        </thead>
        <tbody>
          @for (doc of documents(); track doc.id) {
            <tr>
              <td>
                <a [routerLink]="['/documents', doc.id]">{{ doc.title }}</a>
              </td>
              <td>
                <span class="badge">{{ doc.document_type_display }}</span>
              </td>
              <td>{{ doc.file_type.toUpperCase() }}</td>
              <td>{{ doc.created_by_name }}</td>
              <td>{{ doc.updated_at | date: 'short' }}</td>
              <td>
                <a
                  [href]="doc.file_url"
                  target="_blank"
                  class="btn btn-secondary btn-sm"
                >
                  Stáhnout
                </a>
                <a
                  [routerLink]="['/documents', doc.id]"
                  class="btn btn-primary btn-sm"
                >
                  Upravit
                </a>
                <button
                  class="btn-delete"
                  (click)="deleteDocument(doc)"
                  title="Smazat"
                >
                  🗑️
                </button>
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="6" style="text-align: center; color: #888">
                Žádné dokumenty
              </td>
            </tr>
          }
        </tbody>
      </table>
    </div>

    <!-- Upload Modal -->
    @if (showUploadModal()) {
      <div class="modal-backdrop" (click)="showUploadModal.set(false)">
        <div class="modal" (click)="$event.stopPropagation()">
          <h2>Nahrát dokument</h2>
          <form (ngSubmit)="uploadDocument()">
            <div class="form-group">
              <label>Název *</label>
              <input
                type="text"
                [(ngModel)]="newDocument.title"
                name="title"
                required
              />
            </div>
            <div class="form-group">
              <label>Typ dokumentu</label>
              <select [(ngModel)]="newDocument.document_type" name="document_type">
                <option value="contract">Smlouva</option>
                <option value="proposal">Nabídka</option>
                <option value="brief">Brief</option>
                <option value="meeting_notes">Poznámky</option>
                <option value="other">Jiné</option>
              </select>
            </div>
            <div class="form-group">
              <label>Soubor *</label>
              <input
                type="file"
                (change)="onFileSelect($event)"
                accept=".doc,.docx,.odt,.rtf,.txt,.xls,.xlsx,.ods,.csv,.ppt,.pptx,.odp,.pdf"
                required
              />
            </div>

            @if (uploadError()) {
              <p class="error">{{ uploadError() }}</p>
            }

            <div class="modal-actions">
              <button
                type="button"
                class="btn btn-secondary"
                (click)="showUploadModal.set(false)"
              >
                Zrušit
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                [disabled]="uploading()"
              >
                {{ uploading() ? 'Nahrávám...' : 'Nahrát' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    }
  `,
  styles: [
    `
      .btn-sm {
        padding: 4px 8px;
        font-size: 12px;
        margin-right: 4px;
      }
      .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }
      .modal {
        background: white;
        border-radius: 12px;
        padding: 24px;
        width: 450px;
        max-width: 90%;
      }
      .modal h2 {
        margin-top: 0;
        margin-bottom: 16px;
      }
      .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        margin-top: 16px;
      }
      .error {
        color: #ef4444;
        font-size: 14px;
      }
    `,
  ],
})
export class DocumentListComponent implements OnInit {
  documents = signal<Document[]>([]);
  showUploadModal = signal(false);
  uploading = signal(false);
  uploadError = signal('');

  newDocument = {
    title: '',
    document_type: 'other',
  };
  selectedFile: File | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.http
      .get<{ results: Document[] }>('api/v1/documents/documents/')
      .subscribe({
        next: (data) => this.documents.set(data.results),
      });
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      if (!this.newDocument.title) {
        this.newDocument.title = this.selectedFile.name.replace(/\.[^/.]+$/, '');
      }
    }
  }

  uploadDocument(): void {
    if (!this.selectedFile || !this.newDocument.title) return;

    this.uploading.set(true);
    this.uploadError.set('');

    const formData = new FormData();
    formData.append('file', this.selectedFile);
    formData.append('title', this.newDocument.title);
    formData.append('document_type', this.newDocument.document_type);

    this.http.post('api/v1/documents/documents/', formData).subscribe({
      next: () => {
        this.uploading.set(false);
        this.showUploadModal.set(false);
        this.newDocument = { title: '', document_type: 'other' };
        this.selectedFile = null;
        this.loadDocuments();
      },
      error: (err) => {
        this.uploading.set(false);
        this.uploadError.set('Chyba při nahrávání');
      },
    });
  }

  deleteDocument(doc: Document): void {
    if (!confirm(`Opravdu smazat "${doc.title}"?`)) return;

    this.http.delete(`api/v1/documents/documents/${doc.id}/`).subscribe({
      next: () => this.loadDocuments(),
    });
  }
}
