import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockService } from '../../services/stock.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './watchlist.component.html',
  styleUrl: './watchlist.component.scss'
})
export class WatchlistComponent implements OnInit {
  watchlist: any[] = [];
  loading = true;

  // Mock data
  private mockWatchlist = [
    { ticker: 'TCS.NS', price: 3842.50, change_pct: 1.19 },
    { ticker: 'RELIANCE.NS', price: 2930.10, change_pct: -0.52 },
    { ticker: 'HDFCBANK.NS', price: 1530.25, change_pct: -1.30 },
    { ticker: 'INFY.NS', price: 1480.90, change_pct: 0.84 }
  ];

  constructor(private stockService: StockService) {}

  ngOnInit() {
    // In real app, check auth, if logged in fetch watchlist
    this.fetchWatchlist();
  }

  fetchWatchlist() {
    this.stockService.getWatchlist().subscribe({
      next: (data) => {
        if (data && data.length > 0) {
          this.watchlist = data;
        } else {
          this.watchlist = this.mockWatchlist;
        }
        this.loading = false;
      },
      error: () => {
        this.watchlist = this.mockWatchlist;
        this.loading = false;
      }
    });
  }

  removeFromWatchlist(ticker: string, event: Event) {
    event.preventDefault();
    event.stopPropagation();
    
    // Optimistic UI update
    this.watchlist = this.watchlist.filter(item => item.ticker !== ticker);
    
    // API call
    this.stockService.removeFromWatchlist(ticker).subscribe();
  }
}
