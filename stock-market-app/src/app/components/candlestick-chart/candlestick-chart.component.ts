import { Component, ElementRef, Input, OnChanges, OnDestroy, OnInit, ViewChild, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts';
import { StockService } from '../../services/stock.service';

@Component({
  selector: 'app-candlestick-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './candlestick-chart.component.html',
  styleUrl: './candlestick-chart.component.scss'
})
export class CandlestickChartComponent implements OnInit, OnChanges, OnDestroy {
  @Input() ticker: string = '';
  @ViewChild('chartContainer', { static: true }) chartContainer!: ElementRef;

  private chart!: IChartApi;
  private candlestickSeries!: ISeriesApi<"Candlestick">;
  private volumeSeries!: ISeriesApi<"Histogram">;
  private sma20Series?: ISeriesApi<"Line">;
  private sma50Series?: ISeriesApi<"Line">;
  private ema20Series?: ISeriesApi<"Line">;

  timeframes = ['1D', '1W', '1M', '3M', '6M', '1Y'];
  activeTimeframe = '1Y';

  showSma20 = false;
  showSma50 = false;
  showEma20 = false;

  tooltipData: any = null;

  constructor(private stockService: StockService) {}

  ngOnInit() {
    this.initChart();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['ticker'] && this.ticker) {
      this.fetchChartData();
    }
  }

  ngOnDestroy() {
    if (this.chart) {
      this.chart.remove();
    }
  }

  private initChart() {
    this.chart = createChart(this.chartContainer.nativeElement, {
      layout: {
        background: { color: '#0D1B2A' },
        textColor: '#94A3B8',
      },
      grid: {
        vertLines: { color: '#1E3A4A' },
        horzLines: { color: '#1E3A4A' },
      },
      crosshair: {
        mode: 1, // Normal mode
        vertLine: { color: '#94A3B8', style: 3, labelBackgroundColor: '#162032' },
        horzLine: { color: '#94A3B8', style: 3, labelBackgroundColor: '#162032' }
      },
      timeScale: {
        borderColor: '#1E3A4A',
        timeVisible: true,
      },
      rightPriceScale: {
        borderColor: '#1E3A4A',
      }
    });

    this.candlestickSeries = this.chart.addCandlestickSeries({
      upColor: '#10B981',
      downColor: '#EF4444',
      borderVisible: false,
      wickUpColor: '#10B981',
      wickDownColor: '#EF4444'
    });

    this.volumeSeries = this.chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: { type: 'volume' },
      priceScaleId: '', // set as an overlay
    });

    this.volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.7, // highest point of the series will be at 70% of the chart
        bottom: 0,
      },
    });

    // Handle crosshair move for tooltip
    this.chart.subscribeCrosshairMove(param => {
      if (param.time && param.point && param.seriesData.size > 0) {
        const candleData: any = param.seriesData.get(this.candlestickSeries);
        const volData: any = param.seriesData.get(this.volumeSeries);
        if (candleData) {
          this.tooltipData = {
            date: param.time,
            open: candleData.open,
            high: candleData.high,
            low: candleData.low,
            close: candleData.close,
            volume: volData ? volData.value : 0
          };
        }
      } else {
        this.tooltipData = null;
      }
    });

    new ResizeObserver(entries => {
      if (entries.length === 0 || entries[0].target !== this.chartContainer.nativeElement) { return; }
      const newRect = entries[0].contentRect;
      this.chart.applyOptions({ height: newRect.height, width: newRect.width });
    }).observe(this.chartContainer.nativeElement);
  }

  fetchChartData() {
    let period = '1y';
    if (this.activeTimeframe === '1M') period = '1mo';
    if (this.activeTimeframe === '3M') period = '3mo';
    if (this.activeTimeframe === '6M') period = '6mo';
    if (this.activeTimeframe === '1D') period = '1d';
    if (this.activeTimeframe === '1W') period = '5d';

    this.stockService.getStockData(this.ticker).subscribe({
      next: (data: any[]) => {
        if (data && data.length) {
          // Format for lightweight-charts
          const candleData = data.map(d => ({
            time: d.date.split('T')[0],
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close
          })).sort((a: any, b: any) => new Date(a.time).getTime() - new Date(b.time).getTime());

          const volumeData = data.map(d => ({
            time: d.date.split('T')[0],
            value: d.volume,
            color: d.close >= d.open ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)'
          })).sort((a: any, b: any) => new Date(a.time).getTime() - new Date(b.time).getTime());

          this.candlestickSeries.setData(candleData);
          this.volumeSeries.setData(volumeData);
          this.chart.timeScale().fitContent();
        }
      }
    });
  }

  setTimeframe(tf: string) {
    this.activeTimeframe = tf;
    this.fetchChartData();
  }

  toggleIndicator(type: string) {
    if (type === 'sma20') this.showSma20 = !this.showSma20;
    if (type === 'sma50') this.showSma50 = !this.showSma50;
    if (type === 'ema20') this.showEma20 = !this.showEma20;
    // In a full implementation, this would fetch SMA data from API and add line series
  }
}
