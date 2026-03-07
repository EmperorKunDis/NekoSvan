import {
  Component,
  ElementRef,
  Input,
  OnDestroy,
  OnInit,
  ViewChild,
  signal,
} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

declare const DocsAPI: any;

interface OnlyOfficeConfig {
  document: {
    fileType: string;
    key: string;
    title: string;
    url: string;
  };
  documentType: string;
  editorConfig: any;
  height: string;
  width: string;
}

@Component({
  selector: 'app-document-editor',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="document-editor">
      @if (loading()) {
        <div class="loading">Načítám editor...</div>
      } @else if (error()) {
        <div class="error">{{ error() }}</div>
      }
      <div #editorContainer id="onlyoffice-editor"></div>
    </div>
  `,
  styles: [
    `
      .document-editor {
        width: 100%;
        height: calc(100vh - 150px);
        min-height: 600px;
        border-radius: 8px;
        overflow: hidden;
        background: white;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
      #onlyoffice-editor {
        width: 100%;
        height: 100%;
      }
      .loading,
      .error {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        font-size: 16px;
      }
      .error {
        color: #ef4444;
      }
    `,
  ],
})
export class DocumentEditorComponent implements OnInit, OnDestroy {
  @Input() documentId!: string;
  @Input() documentServerUrl = "https://posthub.work/app/onlyoffice";
  @ViewChild('editorContainer') editorContainer!: ElementRef;

  loading = signal(true);
  error = signal('');

  private docEditor: any = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadEditor();
  }

  ngOnDestroy(): void {
    if (this.docEditor) {
      this.docEditor.destroyEditor();
    }
  }

  private loadEditor(): void {
    // Load ONLYOFFICE API script
    this.loadScript(`${this.documentServerUrl}/web-apps/apps/api/documents/api.js`)
      .then(() => this.initEditor())
      .catch((err) => {
        this.loading.set(false);
        this.error.set(
          'Nepodařilo se načíst ONLYOFFICE editor. Zkontrolujte, že Document Server běží.'
        );
        console.error('Failed to load ONLYOFFICE API:', err);
      });
  }

  private loadScript(src: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (typeof DocsAPI !== 'undefined') {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = src;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load script'));
      document.head.appendChild(script);
    });
  }

  private initEditor(): void {
    this.http
      .get<OnlyOfficeConfig>(
        `api/v1/documents/documents/${this.documentId}/onlyoffice_config/`
      )
      .subscribe({
        next: (config) => {
          this.loading.set(false);

          // Initialize ONLYOFFICE editor
          this.docEditor = new DocsAPI.DocEditor('onlyoffice-editor', {
            ...config,
            events: {
              onAppReady: () => console.log('ONLYOFFICE editor ready'),
              onDocumentStateChange: (event: any) => {
                console.log('Document state changed:', event.data);
              },
              onError: (event: any) => {
                console.error('ONLYOFFICE error:', event.data);
                this.error.set('Chyba editoru: ' + event.data.errorDescription);
              },
              onWarning: (event: any) => {
                console.warn('ONLYOFFICE warning:', event.data);
              },
            },
          });
        },
        error: (err) => {
          this.loading.set(false);
          this.error.set('Nepodařilo se načíst konfiguraci dokumentu.');
          console.error('Failed to get ONLYOFFICE config:', err);
        },
      });
  }
}
