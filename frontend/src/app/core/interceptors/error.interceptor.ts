import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { ToastService } from '../services/toast.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  // Skip for portal URLs — portal components handle their own errors
  if (req.url.includes('/portal/')) {
    return next(req);
  }

  const toast = inject(ToastService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error) => {
      switch (error.status) {
        case 401:
          router.navigate(['/login']);
          break;
        case 403:
          toast.warning('Nemáte oprávnění k této akci.');
          break;
        case 429:
          toast.warning('Příliš mnoho požadavků. Zkuste to za chvíli.');
          break;
        default:
          if (error.status >= 500) {
            toast.error('Chyba serveru. Zkuste to prosím znovu.');
          }
          break;
      }
      return throwError(() => error);
    }),
  );
};
