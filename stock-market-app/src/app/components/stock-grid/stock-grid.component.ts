import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockCardComponent } from '../stock-card/stock-card.component';
import { StockService } from '../../services/stock.service';
import { gsap } from 'gsap';

@Component({
  selector: 'app-stock-grid',
  standalone: true,
  imports: [CommonModule, StockCardComponent],
  templateUrl: './stock-grid.component.html',
  styleUrl: './stock-grid.component.scss'
})
export class StockGridComponent implements OnInit {
  topStocks: any[] = [];
  loading = true;

  // Fallback mock data
  private mockStocks = [
    { ticker: 'TCS.NS', name: 'Tata Consultancy Services', price: 3842.50, change: 45.20, change_pct: 1.19, signal: 'BUY' },
    { ticker: 'RELIANCE.NS', name: 'Reliance Industries Ltd', price: 2930.10, change: -15.40, change_pct: -0.52, signal: 'HOLD' },
    { ticker: 'HDFCBANK.NS', name: 'HDFC Bank Ltd', price: 1530.25, change: -20.10, change_pct: -1.30, signal: 'SELL' },
    { ticker: 'INFY.NS', name: 'Infosys Ltd', price: 1480.90, change: 12.30, change_pct: 0.84, signal: 'BUY' },
    { ticker: 'ITC.NS', name: 'ITC Ltd', price: 420.50, change: 5.10, change_pct: 1.23, signal: 'BUY' },
    { ticker: 'SBIN.NS', name: 'State Bank of India', price: 760.15, change: -2.50, change_pct: -0.33, signal: 'HOLD' }
  ];

  constructor(private stockService: StockService) {}

  ngOnInit() {
    // In a real scenario, you'd fetch a list of featured/top stocks.
    // We'll simulate this by using mock data if the API doesn't provide a direct "top stocks" list
    // Let's use the mock data for now, as the API only returns a specific stock or watchlist.
    setTimeout(() => {
      this.topStocks = this.mockStocks;
      this.loading = false;
      
      // Wait for Angular to update the DOM, then run GSAP stagger animation
      setTimeout(() => {
        gsap.from('.grid-container .stock-card:not(.skeleton)', {
          opacity: 0,
          y: 24,
          scale: 0.95,
          duration: 0.5,
          stagger: 0.06,
          ease: 'power2.out'
        });
      }, 50);
    }, 800);
  }
}
