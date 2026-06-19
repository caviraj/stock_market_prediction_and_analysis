import { Component } from '@angular/core';
import { StockGridComponent } from '../../components/stock-grid/stock-grid.component';
import { GainersLosersComponent } from '../../components/gainers-losers/gainers-losers.component';
import { WatchlistComponent } from '../watchlist/watchlist.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [StockGridComponent, GainersLosersComponent, WatchlistComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {

}
