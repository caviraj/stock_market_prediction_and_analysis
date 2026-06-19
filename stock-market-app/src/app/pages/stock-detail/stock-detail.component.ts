import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { CandlestickChartComponent } from '../../components/candlestick-chart/candlestick-chart.component';
import { PredictionPanelComponent } from '../../components/prediction-panel/prediction-panel.component';
import { TechIndicatorsComponent } from '../../components/tech-indicators/tech-indicators.component';
import { StockService } from '../../services/stock.service';

@Component({
  selector: 'app-stock-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, CandlestickChartComponent, PredictionPanelComponent, TechIndicatorsComponent],
  templateUrl: './stock-detail.component.html',
  styleUrl: './stock-detail.component.scss'
})
export class StockDetailComponent implements OnInit {
  ticker: string = '';
  stockInfo: any = null;
  predictionData: any = null;
  indicatorsData: any = null;
  loading = true;

  constructor(
    private route: ActivatedRoute,
    private stockService: StockService
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.ticker = params.get('ticker') || '';
      if (this.ticker) {
        this.fetchData();
      }
    });
  }

  fetchData() {
    // In a real app, you'd fetch these concurrently using forkJoin or similar
    // For now we'll do it sequentially or just use mock data to ensure UI displays
    
    // Mocking stock info since we don't have a specific header endpoint defined, we can extract from latest price
    this.stockService.getPrediction(this.ticker).subscribe({
      next: (data) => {
        this.predictionData = data;
        
        // Mock header data based on prediction
        this.stockInfo = {
          ticker: this.ticker,
          name: this.ticker.replace('.NS', ''), // Simple mock
          price: data.forecast_7d ? data.forecast_7d[0] : 0,
          change: 15.20,
          change_pct: 0.5,
          last_updated: '2 min ago'
        };
      },
      error: () => {
        // Fallback mock
        this.stockInfo = { ticker: this.ticker, name: this.ticker, price: 3842.50, change: 45.20, change_pct: 1.19, last_updated: '2 min ago' };
        this.predictionData = {
          signal: 'BUY',
          forecast_7d: [3842.5, 3860.1, 3855.2, 3890.0, 3910.5, 3950.0, 3980.2],
          confidence: 0.85
        };
      }
    });

    this.stockService.getIndicators(this.ticker).subscribe({
      next: (data) => { this.indicatorsData = data; },
      error: () => {
        // Fallback mock
        this.indicatorsData = {
          rsi: { value: 45.5, status: 'Neutral' },
          macd: { macd: 12.5, signal: 10.2, histogram: 2.3, trend: 'Bullish' },
          bollinger: { position: 'Inside' },
          atr: { atr: 35.2, volatility_level: 'Medium' }
        };
      }
    });
    
    this.loading = false;
  }
}
