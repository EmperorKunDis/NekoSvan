import { Component } from '@angular/core';
import { ToastService } from '../../../core/services/toast.service';

@Component({
  selector: 'app-toast-container',
  standalone: true,
  template: `
    <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      @for (toast of toastService.toasts(); track toast.id) {
        <div
          class="px-4 py-3 rounded-lg shadow-lg text-white text-sm flex items-center justify-between gap-2"
          [class]="typeClasses[toast.type]"
        >
          <span>{{ toast.message }}</span>
          <button
            class="ml-2 text-white/80 hover:text-white font-bold"
            (click)="toastService.dismiss(toast.id)"
          >
            &times;
          </button>
        </div>
      }
    </div>
  `,
})
export class ToastContainerComponent {
  typeClasses: Record<string, string> = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    warning: 'bg-yellow-600',
    info: 'bg-blue-600',
  };

  constructor(protected toastService: ToastService) {}
}
