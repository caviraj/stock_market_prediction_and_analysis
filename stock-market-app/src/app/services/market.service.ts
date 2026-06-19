import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { MarketOverview } from '../models/stock.model';

@Injectable({
  providedIn: 'root'
})
export class MarketService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getMarketOverview(): Observable<MarketOverview> {
    return this.http.get<MarketOverview>(`${this.apiUrl}/market/overview`);
  }
}
