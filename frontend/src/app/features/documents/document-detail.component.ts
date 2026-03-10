import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { DocumentEditorComponent } from './document-editor.component';

interface Document {
  id: string;
  title: string;
  document_type: string;
  document_type_display: string;
  file_url: string;
  file_type: string;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

@Component({
  selector: 'app-document-detail',
  standalone: true,
  imports: [RouterLink, DocumentEditorComponent],
  template: `
    <div class="document-detail">
      @if (loading()) {
        <p>Načítám...</p>
      } @else if (document()) {
        <div class="header">
          <div class="title-section">
            <a routerLink="/documents" class="back-link">← Zpět na dokumenty</a>
            <h1>{{ document()!.title }}</h1>
            <div class="meta">
              <span class="badge">{{ document()!.document_type_display }}</span>
              <span>{{ document()!.file_type.toUpperCase() }}</span>
              <span>Vytvořil: {{ document()!.created_by_name }}</span>
            </div>
          </div>
          <div class="actions">
            <a
              [href]="document()!.file_url"
              target="_blank"
              class="btn btn-secondary"
            >
              Stáhnout
            </a>
          </div>
        </div>

        <app-document-editor
          [documentId]="document()!.id"
          [documentServerUrl]="documentServerUrl"
        />
      } @else {
        <p>Dokument nenalezen</p>
      }
    </div>
  `,
  styles: [
    `
      .document-detail {
        height: 100%;
      }
      .header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
      }
      .back-link {
        color: #7c3aed;
        text-decoration: none;
        font-size: 14px;
        display: block;
        margin-bottom: 8px;
      }
      .back-link:hover {
        text-decoration: underline;
      }
      h1 {
        margin: 0 0 8px;
        font-size: 24px;
      }
      .meta {
        display: flex;
        gap: 12px;
        font-size: 14px;
        color: #6b7280;
      }
      .badge {
        background: #f3e8ff;
        color: #7c3aed;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
      }
      .actions {
        display: flex;
        gap: 8px;
      }
    `,
  ],
})
export class DocumentDetailComponent implements OnInit {
  document = signal<Document | null>(null);
  loading = signal(true);

  // Use relative URL - works on any domain (posthub.work, app.praut.cz, etc.)
  documentServerUrl = window.location.origin + "/app/onlyoffice";

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadDocument(id);
    }
  }

  loadDocument(id: string): void {
    this.http.get<Document>(`api/v1/documents/documents/${id}/`).subscribe({
      next: (doc) => {
        this.document.set(doc);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }
}
