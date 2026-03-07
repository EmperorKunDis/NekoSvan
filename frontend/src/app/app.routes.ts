import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: 'login',
    loadComponent: () => import('./features/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
    canActivate: [authGuard],
  },
  {
    path: 'deals',
    loadComponent: () =>
      import('./features/deals/deal-list.component').then((m) => m.DealListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'deals/new',
    loadComponent: () =>
      import('./features/deals/deal-create.component').then((m) => m.DealCreateComponent),
    canActivate: [authGuard],
  },
  {
    path: 'deals/from-document',
    loadComponent: () =>
      import('./features/deals/deal-from-document.component').then(
        (m) => m.DealFromDocumentComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'deals/:id',
    loadComponent: () =>
      import('./features/deals/deal-detail.component').then((m) => m.DealDetailComponent),
    canActivate: [authGuard],
  },
  {
    path: 'deals/:id/questionnaire',
    loadComponent: () =>
      import('./features/questionnaire/questionnaire-form.component').then(
        (m) => m.QuestionnaireFormComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'deals/:id/pricing',
    loadComponent: () =>
      import('./features/pricing/pricing.component').then((m) => m.PricingComponent),
    canActivate: [authGuard],
  },
  {
    path: 'deals/:id/contract',
    loadComponent: () =>
      import('./features/contracts/contract.component').then((m) => m.ContractComponent),
    canActivate: [authGuard],
  },
  {
    path: 'deals/:id/project',
    loadComponent: () =>
      import('./features/projects/project-detail.component').then((m) => m.ProjectDetailComponent),
    canActivate: [authGuard],
  },
  {
    path: 'projects',
    loadComponent: () =>
      import('./features/projects/project-list.component').then((m) => m.ProjectListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'qa-queue',
    loadComponent: () => import('./features/qa/qa-queue.component').then((m) => m.QAQueueComponent),
    canActivate: [authGuard],
  },
  {
    path: 'payments',
    loadComponent: () =>
      import('./features/payments/payment-list.component').then((m) => m.PaymentListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'templates',
    loadComponent: () =>
      import('./features/templates/template-list.component').then((m) => m.TemplateListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'documents',
    loadComponent: () =>
      import('./features/documents/document-list.component').then(
        (m) => m.DocumentListComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'documents/:id',
    loadComponent: () =>
      import('./features/documents/document-detail.component').then(
        (m) => m.DocumentDetailComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'pricing-matrix',
    loadComponent: () =>
      import('./features/pricing/pricing-matrix.component').then((m) => m.PricingMatrixComponent),
    canActivate: [authGuard],
  },
  {
    path: 'milestone-templates',
    loadComponent: () =>
      import('./features/templates/milestone-templates.component').then(
        (m) => m.MilestoneTemplatesComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'notifications',
    loadComponent: () =>
      import('./features/notifications/notification-list.component').then(
        (m) => m.NotificationListComponent,
      ),
    canActivate: [authGuard],
  },
  {
    path: 'portal/:token',
    loadComponent: () =>
      import('./features/portal/portal.component').then((m) => m.PortalComponent),
  },
  {
    path: 'profile',
    loadComponent: () =>
      import('./features/profile/profile.component').then((m) => m.ProfileComponent),
    canActivate: [authGuard],
  },
  {
    path: 'team',
    loadComponent: () =>
      import('./features/team/team.component').then((m) => m.TeamComponent),
    canActivate: [authGuard],
  },
];
