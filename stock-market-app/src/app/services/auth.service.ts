import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;


  constructor(private http: HttpClient) { }

  login(credentials: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login`, credentials).pipe(
      tap((res: any) => this.setSession(res.access_token))
    );
  }

  signup(userData: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/signup`, userData).pipe(
      tap((res: any) => this.setSession(res.access_token))
    );
  }

  private setSession(token: string) {
    localStorage.setItem('stockai_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('stockai_token');
  }

  logout() {
    localStorage.removeItem('stockai_token');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('stockai_token');
  }
}
