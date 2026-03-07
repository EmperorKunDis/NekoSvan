import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * Factory function that creates a route guard checking user role.
 * Usage: canActivate: [authGuard, roleGuard('adam', 'nekosvan')]
 */
export function roleGuard(...allowedRoles: string[]): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    // If still loading, wait for user check to finish
    if (auth.isLoading()) {
      return new Promise<boolean>((resolve) => {
        const interval = setInterval(() => {
          if (!auth.isLoading()) {
            clearInterval(interval);
            if (auth.isAuthenticated && allowedRoles.includes(auth.userRole)) {
              resolve(true);
            } else {
              router.navigate(['/dashboard']);
              resolve(false);
            }
          }
        }, 50);
      });
    }

    if (auth.isAuthenticated && allowedRoles.includes(auth.userRole)) {
      return true;
    }

    router.navigate(['/dashboard']);
    return false;
  };
}
