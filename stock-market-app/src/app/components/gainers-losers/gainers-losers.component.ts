import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockService } from '../../services/stock.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-gainers-losers',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './gainers-losers.component.html',
  styleUrl: './gainers-losers.component.scss'
})
export class GainersLosersComponent implements OnInit {
  gainers: any[] = [];
  losers: any[] = [];
  loading = true;

  // Mock data
  private mockGainers = [
    { ticker: 'ITC.NS', price: 420.50, change_pct: 2.34 },
    { ticker: 'TCS.NS', price: 3842.50, change_pct: 1.19 },
    { ticker: 'INFY.NS', price: 1480.90, change_pct: 0.84 },
    { ticker: 'HINDUNILVR.NS', price: 2340.10, change_pct: 0.65 },
    { ticker: 'BHARTIARTL.NS', price: 1120.30, change_pct: 0.42 }
  ];

  private mockLosers = [
    { ticker: 'HDFCBANK.NS', price: 1530.25, change_pct: -1.30 },
    { ticker: 'RELIANCE.NS', price: 2930.10, change_pct: -0.52 },
    { ticker: 'SBIN.NS', price: 760.15, change_pct: -0.33 },
    { ticker: 'ICICIBANK.NS', price: 1080.40, change_pct: -0.21 },
    { ticker: 'AXISBANK.NS', price: 1045.20, change_pct: -0.15 }
  ];

  constructor(private stockService: StockService) {}

  ngOnInit() {
    this.stockService.getMarketOverview().subscribe({
      next: (data) => {
        if (data && data.top_gainers && data.top_losers) {
          this.gainers = data.top_gainers;
          this.losers = data.top_losers;
        } else {
          this.gainers = this.mockGainers;
          this.losers = this.mockLosers;
        }
        this.loading = false;
      },
      error: () => {
        this.gainers = this.mockGainers;
        this.losers = this.mockLosers;
        this.loading = false;
      }
    });
  }
}
