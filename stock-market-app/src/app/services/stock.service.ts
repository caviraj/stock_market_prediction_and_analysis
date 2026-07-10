import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface MarketOverview {
  sensex: any;
  nifty50: any;
  bank_nifty: any;
  nifty_it?: any;
  top_gainers: any[];
  top_losers: any[];
}

@Injectable({
  providedIn: 'root'
})
export class StockService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getTopStocks(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/stock/list/latest?tickers=TCS.NS,RELIANCE.NS,HDFCBANK.NS,INFY.NS,ITC.NS,SBIN.NS`);
  }

  getMarketOverview(): Observable<MarketOverview> {
    return this.http.get<MarketOverview>(`${this.apiUrl}/market/overview`);
  }

  getStockData(ticker: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/stock/${ticker}`);
  }

  getPrediction(ticker: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/predict/${ticker}`);
  }

  getIndicators(ticker: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/indicators/${ticker}`);
  }

  getWatchlist(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/watchlist`);
  }

  addToWatchlist(ticker: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/watchlist/add`, { ticker });
  }

  removeFromWatchlist(ticker: string): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/watchlist/${ticker}`);
  }
}
