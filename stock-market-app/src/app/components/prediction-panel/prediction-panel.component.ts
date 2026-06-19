import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-prediction-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './prediction-panel.component.html',
  styleUrl: './prediction-panel.component.scss'
})
export class PredictionPanelComponent implements OnChanges {
  @Input() predictionData: any;
  
  forecastDays: any[] = [];
  
  ngOnChanges(changes: SimpleChanges) {
    if (changes['predictionData'] && this.predictionData) {
      this.generateForecastTable();
    }
  }
  
  generateForecastTable() {
    if (!this.predictionData || !this.predictionData.forecast_7d) return;
    
    // Create mock days and calculate change from current price (mocked as the first predicted price for demo)
    const currentPrice = this.predictionData.forecast_7d[0];
    const today = new Date();
    
    this.forecastDays = this.predictionData.forecast_7d.map((price: number, idx: number) => {
      const date = new Date(today);
      date.setDate(date.getDate() + idx + 1);
      const changePct = ((price - currentPrice) / currentPrice) * 100;
      
      return {
        day: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
        price: price,
        change_pct: changePct
      };
    });
  }
}
