import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { WatchlistItem } from '../models/stock.model';

@Injectable({
  providedIn: 'root'
})
export class WatchlistService {
  private apiUrl = environment.apiUrl;
  private watchlistSubject = new BehaviorSubject<WatchlistItem[]>([]);
  watchlist$ = this.watchlistSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadWatchlist();
  }

  loadWatchlist(): void {
    this.http.get<WatchlistItem[]>(`${this.apiUrl}/watchlist`).subscribe({
      next: (items) => this.watchlistSubject.next(items),
      error: () => this.watchlistSubject.next([])
    });
  }

  getWatchlist(): Observable<WatchlistItem[]> {
    return this.http.get<WatchlistItem[]>(`${this.apiUrl}/watchlist`).pipe(
      tap(items => this.watchlistSubject.next(items))
    );
  }

  addToWatchlist(ticker: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/watchlist/add`, { ticker }).pipe(
      tap(() => this.loadWatchlist())
    );
  }

  removeFromWatchlist(ticker: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/watchlist/${ticker}`).pipe(
      tap(() => this.loadWatchlist())
    );
  }
}
