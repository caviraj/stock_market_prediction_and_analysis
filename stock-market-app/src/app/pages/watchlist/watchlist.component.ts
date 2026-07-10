import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { WatchlistService } from '../../services/watchlist.service';
import { WatchlistItem } from '../../models/stock.model';

@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './watchlist.component.html',
  styleUrl: './watchlist.component.scss'
})
export class WatchlistComponent implements OnInit {
  watchlist: WatchlistItem[] = [];
  loading = true;
  showAddInput = false;
  newTicker = '';

  constructor(private watchlistService: WatchlistService) {}

  ngOnInit() {
    this.watchlistService.watchlist$.subscribe({
      next: (items) => {
        this.watchlist = items;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  toggleAddInput() {
    this.showAddInput = !this.showAddInput;
    if (!this.showAddInput) {
      this.newTicker = '';
    }
  }

  quickAdd() {
    const value = this.newTicker.trim().toUpperCase();
    if (value) {
      let ticker = value;
      if (!ticker.startsWith('^') && !ticker.endsWith('.NS') && !ticker.endsWith('.BO')) {
        ticker = `${ticker}.NS`;
      }
      this.watchlistService.addToWatchlist(ticker).subscribe({
        next: () => {
          this.newTicker = '';
          this.showAddInput = false;
        },
        error: (err) => {
          alert(err?.error?.detail || 'Error adding stock to watchlist');
        }
      });
    }
  }

  removeFromWatchlist(ticker: string, event: Event) {
    event.preventDefault();
    event.stopPropagation();
    this.watchlistService.removeFromWatchlist(ticker).subscribe();
  }
}
