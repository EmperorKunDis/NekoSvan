import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-phase-badge',
  standalone: true,
  template: `<span class="badge badge-{{ phase }}">{{ label || phase }}</span>`,
})
export class PhaseBadgeComponent {
  @Input({ required: true }) phase = '';
  @Input() label = '';
}
