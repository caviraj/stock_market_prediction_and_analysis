import { Injectable } from '@angular/core';
import { Observable, from } from 'rxjs';
import { tap } from 'rxjs/operators';
import { createClient } from '@supabase/supabase-js';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private supabase = createClient(
    'https://ugauufqrhlhjyrfqptlv.supabase.co',
    'sb_publishable_QpS3z27S9K56OVQQIyjHYA_0WMZnk1F'
  );

  constructor() {
    this.supabase.auth.onAuthStateChange((event, session) => {
      if (session && session.access_token) {
        this.setSession(session.access_token);
      } else if (event === 'SIGNED_OUT') {
        this.logout();
      }
    });
  }

  login(credentials: any): Observable<any> {
    return from(this.supabase.auth.signInWithPassword({
      email: credentials.email,
      password: credentials.password
    })).pipe(
      tap((res: any) => {
        if (res.error) throw res.error;
        this.setSession(res.data.session.access_token);
      })
    );
  }

  signup(userData: any): Observable<any> {
    return from(this.supabase.auth.signUp({
      email: userData.email,
      password: userData.password,
      options: {
        data: {
          full_name: userData.name
        }
      }
    })).pipe(
      tap((res: any) => {
        if (res.error) throw res.error;
        if (res.data.session) {
          this.setSession(res.data.session.access_token);
        } else if (res.data.user) {
          throw new Error('Signup successful! Please check your email to confirm your account.');
        }
      })
    );
  }

  private setSession(token: string) {
    localStorage.setItem('stockai_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('stockai_token');
  }

  logout() {
    this.supabase.auth.signOut();
    localStorage.removeItem('stockai_token');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('stockai_token');
  }
}
