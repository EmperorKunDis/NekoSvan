import { Component, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-deal-from-document',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="document-page">
      <h1>Lead z dokumentu</h1>
      <p class="subtitle">
        Nahrajte dokument nebo vložte text a AI automaticky vytvoří lead.
      </p>

      <div class="upload-area">
        <!-- File Upload -->
        <div
          class="drop-zone"
          [class.dragging]="dragging()"
          (dragover)="onDragOver($event)"
          (dragleave)="dragging.set(false)"
          (drop)="onDrop($event)"
        >
          <input
            type="file"
            #fileInput
            (change)="onFileSelect($event)"
            accept=".txt,.pdf,.doc,.docx,.eml"
            style="display: none"
          />
          @if (selectedFile()) {
            <div class="file-info">
              <span class="file-icon">📄</span>
              <span>{{ selectedFile()!.name }}</span>
              <button class="btn-remove" (click)="clearFile()">×</button>
            </div>
          } @else {
            <div class="drop-content" (click)="fileInput.click()">
              <span class="upload-icon">📁</span>
              <p>Přetáhněte soubor nebo klikněte pro výběr</p>
              <small>Podporované formáty: TXT, PDF, DOC, DOCX, EML</small>
            </div>
          }
        </div>

        <div class="divider">
          <span>nebo</span>
        </div>

        <!-- Text Input -->
        <div class="text-input">
          <label>Vložte text (email, poznámky, brief...)</label>
          <textarea
            [(ngModel)]="rawText"
            rows="8"
            placeholder="Vložte obsah emailu, poznámky ze schůzky, brief od klienta..."
          ></textarea>
        </div>

        <!-- Document Type -->
        <div class="form-group">
          <label>Typ dokumentu</label>
          <select [(ngModel)]="documentType">
            <option value="email">Email</option>
            <option value="brief">Brief</option>
            <option value="rfp">RFP</option>
            <option value="meeting_notes">Poznámky ze schůzky</option>
            <option value="other">Jiné</option>
          </select>
        </div>

        <!-- Submit -->
        <button
          class="btn-primary"
          (click)="process()"
          [disabled]="processing() || (!selectedFile() && !rawText)"
        >
          {{ processing() ? 'Zpracovávám...' : 'Vytvořit lead' }}
        </button>

        @if (error()) {
          <div class="error-box">
            <strong>Chyba:</strong> {{ error() }}
          </div>
        }

        @if (extractedData()) {
          <div class="preview-box">
            <h3>Extrahovaná data</h3>
            <dl>
              <dt>Firma</dt>
              <dd>{{ extractedData()!['client_company'] || '—' }}</dd>
              <dt>Kontakt</dt>
              <dd>{{ extractedData()!['client_contact_name'] || '—' }}</dd>
              <dt>Email</dt>
              <dd>{{ extractedData()!['client_email'] || '—' }}</dd>
              <dt>Telefon</dt>
              <dd>{{ extractedData()!['client_phone'] || '—' }}</dd>
              <dt>Spolehlivost</dt>
              <dd>{{ (extractedData()!['confidence'] * 100).toFixed(0) }}%</dd>
            </dl>
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      .document-page {
        max-width: 700px;
        margin: 0 auto;
      }
      .subtitle {
        color: #666;
        margin-bottom: 1.5rem;
      }
      .upload-area {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
      .drop-zone {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        transition: all 0.2s;
        cursor: pointer;
      }
      .drop-zone:hover,
      .drop-zone.dragging {
        border-color: #3b82f6;
        background: #eff6ff;
      }
      .drop-content {
        color: #666;
      }
      .upload-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 0.5rem;
      }
      .file-info {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
      }
      .file-icon {
        font-size: 1.5rem;
      }
      .btn-remove {
        background: #fee2e2;
        color: #991b1b;
        border: none;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 1rem;
        line-height: 1;
      }
      .divider {
        text-align: center;
        margin: 1.5rem 0;
        color: #999;
        position: relative;
      }
      .divider::before,
      .divider::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 40%;
        height: 1px;
        background: #ddd;
      }
      .divider::before {
        left: 0;
      }
      .divider::after {
        right: 0;
      }
      .text-input {
        margin-bottom: 1rem;
      }
      .text-input label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
      }
      textarea {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-family: inherit;
        font-size: 0.95rem;
        resize: vertical;
      }
      .form-group {
        margin-bottom: 1rem;
      }
      .form-group label {
        display: block;
        margin-bottom: 0.25rem;
        font-weight: 500;
      }
      select {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
      }
      .btn-primary {
        width: 100%;
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 4px;
        font-size: 1rem;
        cursor: pointer;
      }
      .btn-primary:hover:not(:disabled) {
        background: #2563eb;
      }
      .btn-primary:disabled {
        background: #93c5fd;
        cursor: not-allowed;
      }
      .error-box {
        margin-top: 1rem;
        padding: 1rem;
        background: #fee2e2;
        border-radius: 4px;
        color: #991b1b;
      }
      .preview-box {
        margin-top: 1rem;
        padding: 1rem;
        background: #f0fdf4;
        border-radius: 4px;
        border: 1px solid #bbf7d0;
      }
      .preview-box h3 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1rem;
      }
      dl {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 0.25rem 1rem;
        margin: 0;
      }
      dt {
        font-weight: 500;
        color: #666;
      }
      dd {
        margin: 0;
      }
    `,
  ],
})
export class DealFromDocumentComponent {
  selectedFile = signal<File | null>(null);
  rawText = '';
  documentType = 'other';
  dragging = signal(false);
  processing = signal(false);
  error = signal('');
  extractedData = signal<Record<string, any> | null>(null);

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragging.set(true);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.dragging.set(false);
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.selectedFile.set(files[0]);
    }
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile.set(input.files[0]);
    }
  }

  clearFile(): void {
    this.selectedFile.set(null);
  }

  process(): void {
    this.processing.set(true);
    this.error.set('');
    this.extractedData.set(null);

    const formData = new FormData();
    if (this.selectedFile()) {
      formData.append('file', this.selectedFile()!);
    }
    if (this.rawText) {
      formData.append('raw_text', this.rawText);
    }
    formData.append('document_type', this.documentType);

    this.http
      .post<{
        status: string;
        deal?: any;
        extracted_data?: Record<string, any>;
        error?: string;
      }>('/api/v1/pipeline/lead-from-document/', formData)
      .subscribe({
        next: (res) => {
          this.processing.set(false);
          this.extractedData.set(res.extracted_data || null);
          if (res.status === 'success' && res.deal) {
            this.router.navigate(['/deals', res.deal.id]);
          } else {
            this.error.set(res.error || 'Neznámá chyba');
          }
        },
        error: (err) => {
          this.processing.set(false);
          this.extractedData.set(err.error?.extracted_data || null);
          
          // Zpracování detailních validačních chyb z DRF
          let errorMsg = 'Chyba při zpracování';
          
          if (err.status === 400 && err.error) {
            // DRF validation errors (dict of field: [messages])
            if (typeof err.error === 'object') {
              const errors: string[] = [];
              
              // Field-specific errors
              for (const [field, messages] of Object.entries(err.error)) {
                if (Array.isArray(messages)) {
                  errors.push(...messages);
                } else if (typeof messages === 'string') {
                  errors.push(messages);
                }
              }
              
              if (errors.length > 0) {
                errorMsg = errors.join(' ');
              } else if (err.error.error) {
                errorMsg = err.error.error;
              } else if (err.error.detail) {
                errorMsg = err.error.detail;
              }
            } else if (typeof err.error === 'string') {
              errorMsg = err.error;
            }
          } else if (err.error?.error) {
            errorMsg = err.error.error;
          } else if (err.error?.detail) {
            errorMsg = err.error.detail;
          }
          
          this.error.set(errorMsg);
        },
      });
  }
}
