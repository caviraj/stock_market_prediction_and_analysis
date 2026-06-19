import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './watchlist.component.html',
  styleUrl: './watchlist.component.scss'
})
export class WatchlistComponent {
  watchlist = [
    { ticker: 'TCS.NS', price: '3,842.50', change: '+1.19%', isPositive: true },
    { ticker: 'RELIANCE.NS', price: '2,950.80', change: '-0.52%', isPositive: false },
    { ticker: 'INFY.NS', price: '1,654.20', change: '+1.56%', isPositive: true },
    { ticker: 'HDFCBANK.NS', price: '1,432.10', change: '+0.87%', isPositive: true },
    { ticker: 'WIPRO.NS', price: '520.10', change: '+3.80%', isPositive: true },
  ];
}
