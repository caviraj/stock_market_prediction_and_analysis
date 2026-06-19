import { Component, AfterViewInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts';

@Component({
  selector: 'app-candle-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './candle-chart.component.html',
  styleUrl: './candle-chart.component.scss'
})
export class CandleChartComponent implements AfterViewInit, OnDestroy {
  @ViewChild('chartContainer') container!: ElementRef;
  
  activeTab: string = '1M';
  showSMA20: boolean = false;
  showSMA50: boolean = false;
  showEMA20: boolean = false;

  private chart!: IChartApi;
  private candlestickSeries!: ISeriesApi<'Candlestick'>;
  private volumeSeries!: ISeriesApi<'Histogram'>;

  ngAfterViewInit() {
    this.initChart();
  }

  ngOnDestroy() {
    if (this.chart) {
      this.chart.remove();
    }
  }

  private initChart() {
    this.chart = createChart(this.container.nativeElement, {
      layout: {
        background: { color: '#0D1B2A' },
        textColor: '#94A3B8',
      },
      grid: {
        vertLines: { color: '#1E3A4A' },
        horzLines: { color: '#1E3A4A' },
      },
      crosshair: {
        mode: 1,
      },
      timeScale: {
        borderColor: '#1E3A4A',
      },
    });

    this.candlestickSeries = this.chart.addCandlestickSeries({
      upColor: '#10B981',
      downColor: '#EF4444',
      borderVisible: false,
      wickUpColor: '#10B981',
      wickDownColor: '#EF4444',
    });

    this.volumeSeries = this.chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });

    this.chart.priceScale('').applyOptions({
      scaleMargins: {
        top: 0.7,
        bottom: 0,
      },
    });

    // Dummy data
    const data: any[] = [];
    const volumeData: any[] = [];
    let time = new Date('2024-01-01').getTime() / 1000;
    
    for (let i = 0; i < 60; i++) {
      const open = 150 + Math.random() * 10;
      const close = open + (Math.random() - 0.5) * 10;
      const high = Math.max(open, close) + Math.random() * 5;
      const low = Math.min(open, close) - Math.random() * 5;
      const isUp = close > open;
      
      data.push({ time, open, high, low, close });
      volumeData.push({
        time,
        value: Math.random() * 1000,
        color: isUp ? '#10B981' : '#EF4444'
      });
      
      time += 86400;
    }

    this.candlestickSeries.setData(data);
    this.volumeSeries.setData(volumeData);
    this.chart.timeScale().fitContent();

    // Handle resize
    new ResizeObserver(entries => {
      if (entries.length === 0 || entries[0].target !== this.container.nativeElement) return;
      const newRect = entries[0].contentRect;
      this.chart.applyOptions({ width: newRect.width, height: newRect.height });
    }).observe(this.container.nativeElement);
  }
}
