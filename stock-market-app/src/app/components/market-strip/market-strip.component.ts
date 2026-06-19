import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockService } from '../../services/stock.service';

@Component({
  selector: 'app-market-strip',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './market-strip.component.html',
  styleUrl: './market-strip.component.scss'
})
export class MarketStripComponent implements OnInit {
  marketData: any = {
    sensex: { value: 74227.63, change: 350.81, change_pct: 0.47 },
    nifty50: { value: 22597.80, change: 112.50, change_pct: 0.50 },
    bank_nifty: { value: 48016.15, change: 200.10, change_pct: 0.42 },
    nifty_it: { value: 34820.50, change: -150.20, change_pct: -0.43 }
  };

  loading = true;

  constructor(private stockService: StockService) {}

  ngOnInit() {
    this.stockService.getMarketOverview().subscribe({
      next: (data) => {
        if (data && data.sensex) {
          // Assuming backend returns an array or object
          // For now we just use mock fallback if not matched
          this.marketData = data;
        }
        this.loading = false;
      },
      error: () => {
        // Fallback to mock data on error
        this.loading = false;
      }
    });
  }
}
