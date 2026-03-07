import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DealService } from '../../core/services/deal.service';

@Component({
  selector: 'app-deal-create',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './deal-create.component.html',
})
export class DealCreateComponent {
  form = {
    client_company: '',
    client_contact_name: '',
    client_email: '',
    client_phone: '',
    description: '',
  };

  constructor(
    private dealService: DealService,
    private router: Router,
  ) {}

  submit(): void {
    this.dealService.create(this.form).subscribe({
      next: (deal) => this.router.navigate(['/deals', deal.id]),
    });
  }
}
