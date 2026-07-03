import { Component, Input, HostListener, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-stock-card',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './stock-card.component.html',
  styleUrl: './stock-card.component.scss'
})
export class StockCardComponent {
  @Input() stock: any;

  constructor(private el: ElementRef) {}

  @HostListener('mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    const card = this.el.nativeElement.querySelector('.stock-card');
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Normalized coordinates from -1 to 1
    const mx = ((x / rect.width) * 2 - 1).toFixed(2);
    const my = ((y / rect.height) * 2 - 1).toFixed(2);
    
    card.style.setProperty('--mx', mx);
    card.style.setProperty('--my', my);
  }

  @HostListener('mouseleave')
  onMouseLeave() {
    const card = this.el.nativeElement.querySelector('.stock-card');
    if (!card) return;
    card.style.setProperty('--mx', '0');
    card.style.setProperty('--my', '0');
  }
}
