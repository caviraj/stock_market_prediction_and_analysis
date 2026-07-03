import { Component, Input, OnChanges, SimpleChanges, ViewChild, ElementRef, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as THREE from 'three';

@Component({
  selector: 'app-prediction-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './prediction-panel.component.html',
  styleUrl: './prediction-panel.component.scss'
})
export class PredictionPanelComponent implements OnChanges, AfterViewInit, OnDestroy {
  @Input() predictionData: any;
  @ViewChild('threeForecastCanvas') threeForecastCanvas!: ElementRef<HTMLCanvasElement>;
  
  viewMode: '2D' | '3D' = '2D';
  forecastDays: any[] = [];
  modelBreakdown: any[] = [];

  private renderer?: THREE.WebGLRenderer;
  private scene?: THREE.Scene;
  private camera?: THREE.PerspectiveCamera;
  private sceneGroup?: THREE.Group;
  private animationFrameId?: number;

  // Orbit rotation controls
  private isDragging = false;
  private previousMousePosition = { x: 0, y: 0 };
  private rotation = { x: 0.3, y: -0.4 };
  private resizeObserver?: ResizeObserver;
  
  ngOnChanges(changes: SimpleChanges) {
    if (changes['predictionData'] && this.predictionData) {
      this.generateForecastTable();
      this.generateModelBreakdown();
      
      if (this.viewMode === '3D') {
        setTimeout(() => {
          this.cleanupThree();
          this.initThreeForecast();
        }, 50);
      }
    }
  }

  ngAfterViewInit() {
    if (this.viewMode === '3D') {
      this.initThreeForecast();
    }
  }

  ngOnDestroy() {
    this.cleanupThree();
  }

  toggleViewMode(mode: '2D' | '3D') {
    this.viewMode = mode;
    if (mode === '3D') {
      setTimeout(() => {
        if (!this.scene) {
          this.initThreeForecast();
        } else {
          this.triggerResize();
        }
      }, 50);
    } else {
      this.cleanupThree();
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

  private initThreeForecast() {
    if (!this.threeForecastCanvas) return;
    const canvas = this.threeForecastCanvas.nativeElement;
    const container = canvas.parentElement;
    if (!container) return;

    const width = container.clientWidth || 300;
    const height = container.clientHeight || 200;

    // 1. Create Scene
    this.scene = new THREE.Scene();
    
    // 2. Create Camera
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    this.camera.position.set(0, 1.2, 8);
    this.camera.lookAt(0, 0, 0);

    // 3. Create Group to rotate the graph items together
    this.sceneGroup = new THREE.Group();
    const group = this.sceneGroup;
    this.scene.add(group);

    // 4. Create Renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      antialias: true,
      alpha: true
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(width, height);

    // 5. Draw 3D Grid Floor
    const gridHelper = new THREE.GridHelper(8, 8, 0x1E3A4A, 0x1E3A4A);
    gridHelper.position.y = -1.2;
    group.add(gridHelper);

    // 6. Draw glowing forecast line
    const forecast = this.predictionData?.forecast_7d || [];
    if (forecast.length > 0) {
      const points: THREE.Vector3[] = [];
      const basePrice = forecast[0];
      
      // Calculate max price diff to scale nicely on grid
      let maxDiff = 0.01;
      forecast.forEach((price: number) => {
        const diff = Math.abs(price - basePrice);
        if (diff > maxDiff) maxDiff = diff;
      });
      const scaleY = 1.2 / maxDiff; // Max height offset is 1.2 units

      forecast.forEach((price: number, idx: number) => {
        const x = (idx - 3) * 1.1; // Center on X axis (-3.3 to +3.3)
        const y = (price - basePrice) * scaleY - 0.4;
        points.push(new THREE.Vector3(x, y, 0));
      });

      // Neon Tube line geometry
      const curve = new THREE.CatmullRomCurve3(points);
      const tubeGeom = new THREE.TubeGeometry(curve, 64, 0.06, 8, false);
      const tubeMat = new THREE.MeshBasicMaterial({
        color: 0x0D9488, // Teal
        transparent: true,
        opacity: 0.9,
      });
      const tubeMesh = new THREE.Mesh(tubeGeom, tubeMat);
      group.add(tubeMesh);

      // Neon outer glow (halo)
      const haloGeom = new THREE.TubeGeometry(curve, 64, 0.14, 8, false);
      const haloMat = new THREE.MeshBasicMaterial({
        color: 0x14B8A6,
        transparent: true,
        opacity: 0.25,
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide
      });
      const haloMesh = new THREE.Mesh(haloGeom, haloMat);
      group.add(haloMesh);

      // Confidence uncertainty particle cloud
      const particleCount = 150;
      const pGeometry = new THREE.BufferGeometry();
      const pPositions = new Float32Array(particleCount * 3);
      const confidence = this.predictionData.confidence || 85;
      const spread = Math.max(0.12, (100 - confidence) * 0.015); // Less confidence = wider particle cloud

      for (let j = 0; j < particleCount; j++) {
        const t = Math.random();
        const pt = curve.getPoint(t);
        
        // Random spherical scatter
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(Math.random() * 2 - 1);
        const radius = Math.random() * spread;
        
        pPositions[j * 3] = pt.x + radius * Math.sin(phi) * Math.cos(theta);
        pPositions[j * 3 + 1] = pt.y + radius * Math.sin(phi) * Math.sin(theta);
        pPositions[j * 3 + 2] = pt.z + radius * Math.cos(phi);
      }

      pGeometry.setAttribute('position', new THREE.BufferAttribute(pPositions, 3));
      
      const pCanvas = document.createElement('canvas');
      pCanvas.width = 16;
      pCanvas.height = 16;
      const ctx = pCanvas.getContext('2d');
      if (ctx) {
        const grad = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
        grad.addColorStop(0, 'rgba(20, 184, 166, 1)');
        grad.addColorStop(1, 'rgba(20, 184, 166, 0)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 16, 16);
      }
      const pTexture = new THREE.CanvasTexture(pCanvas);

      const pMaterial = new THREE.PointsMaterial({
        size: 0.16,
        map: pTexture,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      });

      const cloud = new THREE.Points(pGeometry, pMaterial);
      group.add(cloud);

      // Node marker spheres for each day
      forecast.forEach((price: number, idx: number) => {
        const pos = points[idx];
        const sphereGeom = new THREE.SphereGeometry(0.1, 16, 16);
        const sphereMat = new THREE.MeshBasicMaterial({
          color: idx === 0 ? 0xF0F4F8 : 0x0D9488
        });
        const sphere = new THREE.Mesh(sphereGeom, sphereMat);
        sphere.position.copy(pos);
        group.add(sphere);
      });
    }

    // Bind drag-to-rotate events
    canvas.addEventListener('mousedown', this.onForecastMouseDown.bind(this));
    canvas.addEventListener('mousemove', this.onForecastMouseMove.bind(this));
    window.addEventListener('mouseup', this.onForecastMouseUp.bind(this));

    canvas.addEventListener('touchstart', this.onForecastTouchStart.bind(this), { passive: true });
    canvas.addEventListener('touchmove', this.onForecastTouchMove.bind(this), { passive: true });
    window.addEventListener('touchend', this.onForecastMouseUp.bind(this));

    // Handle container resize
    this.resizeObserver = new ResizeObserver(() => this.triggerResize());
    this.resizeObserver.observe(container);

    // Start loop
    this.animateForecast();
  }

  private onForecastMouseDown(e: MouseEvent) {
    this.isDragging = true;
    this.previousMousePosition = {
      x: e.clientX,
      y: e.clientY
    };
  }

  private onForecastMouseMove(e: MouseEvent) {
    if (!this.isDragging) return;
    const deltaX = e.clientX - this.previousMousePosition.x;
    const deltaY = e.clientY - this.previousMousePosition.y;

    this.rotation.y += deltaX * 0.005;
    this.rotation.x += deltaY * 0.005;
    
    // Clamp vertical rotation
    this.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, this.rotation.x));

    this.previousMousePosition = {
      x: e.clientX,
      y: e.clientY
    };
  }

  private onForecastTouchStart(e: TouchEvent) {
    if (e.touches.length === 1) {
      this.isDragging = true;
      this.previousMousePosition = {
        x: e.touches[0].clientX,
        y: e.touches[0].clientY
      };
    }
  }

  private onForecastTouchMove(e: TouchEvent) {
    if (!this.isDragging || e.touches.length !== 1) return;
    const deltaX = e.touches[0].clientX - this.previousMousePosition.x;
    const deltaY = e.touches[0].clientY - this.previousMousePosition.y;

    this.rotation.y += deltaX * 0.008;
    this.rotation.x += deltaY * 0.008;

    this.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, this.rotation.x));

    this.previousMousePosition = {
      x: e.touches[0].clientX,
      y: e.touches[0].clientY
    };
  }

  private onForecastMouseUp() {
    this.isDragging = false;
  }

  private triggerResize() {
    if (!this.renderer || !this.camera || !this.threeForecastCanvas) return;
    const canvas = this.threeForecastCanvas.nativeElement;
    const container = canvas.parentElement;
    if (!container) return;

    const width = container.clientWidth || 300;
    const height = container.clientHeight || 200;

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  private animateForecast() {
    this.animationFrameId = requestAnimationFrame(() => this.animateForecast());

    if (!this.renderer || !this.scene || !this.camera || !this.sceneGroup) return;

    // Apply rotation lerp for buttery smooth transitions
    this.sceneGroup.rotation.y += (this.rotation.y - this.sceneGroup.rotation.y) * 0.1;
    this.sceneGroup.rotation.x += (this.rotation.x - this.sceneGroup.rotation.x) * 0.1;

    // Gentle floating motion on the particles
    const time = Date.now() * 0.001;
    this.sceneGroup.children.forEach(child => {
      if (child instanceof THREE.Points) {
        child.rotation.z = time * 0.05;
      }
    });

    this.renderer.render(this.scene, this.camera);
  }

  private cleanupThree() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = undefined;
    }

    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = undefined;
    }

    if (this.sceneGroup) {
      this.sceneGroup.traverse(object => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose();
          if (Array.isArray(object.material)) {
            object.material.forEach(m => m.dispose());
          } else {
            object.material.dispose();
          }
        } else if (object instanceof THREE.Points) {
          object.geometry.dispose();
          if (Array.isArray(object.material)) {
            object.material.forEach(m => m.dispose());
          } else {
            object.material.dispose();
          }
        }
      });
      this.sceneGroup = undefined;
    }

    if (this.renderer) {
      this.renderer.dispose();
      this.renderer = undefined;
    }

    this.scene = undefined;
    this.camera = undefined;
  }
}
