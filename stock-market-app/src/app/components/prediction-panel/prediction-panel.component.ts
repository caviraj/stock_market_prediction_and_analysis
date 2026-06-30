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
  modelBreakdown: any[] = [];
  
  ngOnChanges(changes: SimpleChanges) {
    if (changes['predictionData'] && this.predictionData) {
      this.generateForecastTable();
      this.generateModelBreakdown();
    }
  }
  
  generateForecastTable() {
    if (!this.predictionData || !this.predictionData.forecast_7d) return;
    
    const currentPrice = this.predictionData.forecast_7d[0];
    const today = new Date();
    
    this.forecastDays = this.predictionData.forecast_7d.map((price: number, idx: number) => {
      const date = new Date(today);
      // Generate subsequent dates skipping weekends for realism (optional, simple addition is fine)
      date.setDate(date.getDate() + idx + 1);
      const changePct = currentPrice !== 0 ? ((price - currentPrice) / currentPrice) * 100 : 0;
      
      return {
        day: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
        price: price,
        change_pct: changePct
      };
    });
  }
  
  generateModelBreakdown() {
    if (!this.predictionData || !this.predictionData.model_predictions) return;
    
    const preds = this.predictionData.model_predictions;
    const modelNames: { [key: string]: { label: string, category: string } } = {
      'arima': { label: 'ARIMA', category: 'Time Series (Baseline)' },
      'sarimax': { label: 'SARIMAX', category: 'Time Series (Seasonal)' },
      'prophet': { label: 'Prophet (Meta)', category: 'Time Series (Advanced)' },
      'linear_regression': { label: 'Linear Regression', category: 'Machine Learning' },
      'random_forest': { label: 'Random Forest', category: 'Machine Learning' },
      'xgboost': { label: 'XGBoost', category: 'Machine Learning' },
      'svr': { label: 'SVR', category: 'Machine Learning' },
      'lstm': { label: 'LSTM', category: 'Deep Learning' },
      'gru': { label: 'GRU', category: 'Deep Learning' }
    };
    
    this.modelBreakdown = Object.keys(preds).map(key => {
      const forecast = preds[key];
      const nameInfo = modelNames[key] || { label: key.toUpperCase(), category: 'Custom' };
      
      let changePct = 0;
      let direction = 'NEUTRAL';
      let avgPrice = 0;
      
      if (forecast && forecast.length > 0) {
        const firstVal = forecast[0];
        const lastVal = forecast[forecast.length - 1];
        changePct = firstVal !== 0 ? ((lastVal - firstVal) / firstVal) * 100 : 0;
        direction = changePct > 0.3 ? 'BULLISH' : changePct < -0.3 ? 'BEARISH' : 'NEUTRAL';
        avgPrice = forecast.reduce((a: number, b: number) => a + b, 0) / forecast.length;
      }
      
      return {
        key,
        label: nameInfo.label,
        category: nameInfo.category,
        avgPrice: avgPrice,
        changePct: changePct,
        direction: direction
      };
    });
  }
}
