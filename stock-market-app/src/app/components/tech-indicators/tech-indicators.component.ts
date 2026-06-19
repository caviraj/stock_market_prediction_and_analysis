import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-tech-indicators',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './tech-indicators.component.html',
  styleUrl: './tech-indicators.component.scss'
})
export class TechIndicatorsComponent {
  @Input() indicatorsData: any;
  
  // Calculate rotation for RSI needle (0-100 maps to -90 to 90 degrees)
  getRsiRotation(rsiValue: number): string {
    if (!rsiValue) return 'rotate(-90deg)';
    const clamped = Math.max(0, Math.min(100, rsiValue));
    const degrees = (clamped / 100) * 180 - 90;
    return `rotate(${degrees}deg)`;
  }
}
