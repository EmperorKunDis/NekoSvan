import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-stat-card',
  standalone: true,
  template: `
    <div class="stat-card">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-label">{{ label }}</div>
    </div>
  `,
  styles: [
    `
      .stat-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        text-align: center;
      }
      .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
      }
      .stat-label {
        font-size: 0.875rem;
        color: #666;
        margin-top: 4px;
      }
    `,
  ],
})
export class StatCardComponent {
  @Input({ required: true }) value: string | number = 0;
  @Input({ required: true }) label = '';
}
