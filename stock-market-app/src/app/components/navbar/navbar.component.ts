import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { WatchlistService } from '../../services/watchlist.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent implements OnInit {
  watchlistCount = 0;

  constructor(
    private router: Router,
    private watchlistService: WatchlistService
  ) {}

  ngOnInit() {
    this.watchlistService.watchlist$.subscribe({
      next: (items) => {
        this.watchlistCount = items.length;
      }
    });
  }

  search(event: any) {
    const value = event.target.value.trim().toUpperCase();
    if (value) {
      let ticker = value;
      if (!ticker.startsWith('^') && !ticker.endsWith('.NS') && !ticker.endsWith('.BO')) {
        ticker = `${ticker}.NS`;
      }
      this.router.navigate(['/stock', ticker]);
      event.target.value = '';
    }
  }
}
