import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import * as THREE from 'three';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.scss'
})
export class AuthComponent implements AfterViewInit, OnDestroy {
  @ViewChild('threeCanvas') threeCanvas!: ElementRef<HTMLCanvasElement>;
  
  private renderer!: THREE.WebGLRenderer;
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private particles!: THREE.Points;
  private lines!: THREE.LineSegments;
  private animationFrameId!: number;
  private clock = new THREE.Clock();
  
  // Mouse coordinates in Normalized Device Coordinates (NDC)
  private mouse = { x: 0, y: 0 };
  private targetCameraPos = { x: 0, y: 4, z: 8 };
  
  // Motion settings
  private prefersReducedMotion = false;
  private motionQueryListener = (e: MediaQueryListEvent) => {
    this.prefersReducedMotion = e.matches;
  };

  activeTab: 'login' | 'signup' = 'login';
  showPassword = false;
  
  loginData = { email: '', password: '' };
  signupData = { name: '', email: '', password: '', confirmPassword: '' };
  
  errorMsg = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

  ngAfterViewInit() {
    this.initThree();
  }

  private initThree() {
    const canvas = this.threeCanvas.nativeElement;
    const container = canvas.parentElement;
    if (!container) return;

    // Check prefers-reduced-motion
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    this.prefersReducedMotion = mq.matches;
    mq.addEventListener('change', this.motionQueryListener);

    // Create scene
    this.scene = new THREE.Scene();

    // Create camera
    const width = container.clientWidth || window.innerWidth / 2;
    const height = container.clientHeight || window.innerHeight;
    this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100);
    this.camera.position.set(0, 4, 8);
    this.camera.lookAt(0, 0, 0);

    // Create renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      antialias: true,
      alpha: true
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(width, height);

    // Create a grid of particles (wave)
    const particleCountX = 60;
    const particleCountZ = 60;
    const count = particleCountX * particleCountZ;

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    // Set initial positions and colors
    let i = 0;
    const gap = 0.25;
    const offset = (particleCountX * gap) / 2;

    const colorTeal = new THREE.Color('#0D9488');
    const colorPurple = new THREE.Color('#6366F1');

    for (let x = 0; x < particleCountX; x++) {
      for (let z = 0; z < particleCountZ; z++) {
        const posX = x * gap - offset;
        const posZ = z * gap - offset;
        positions[i] = posX;
        positions[i + 1] = 0; // Height will be animated
        positions[i + 2] = posZ;

        // Gradient color from center or based on index
        const mixRatio = (x / particleCountX + z / particleCountZ) / 2;
        const mixedColor = new THREE.Color().lerpColors(colorTeal, colorPurple, mixRatio);
        colors[i] = mixedColor.r;
        colors[i + 1] = mixedColor.g;
        colors[i + 2] = mixedColor.b;

        i += 3;
      }
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Custom circular particle texture (using Canvas API to generate a soft circle)
    const pCanvas = document.createElement('canvas');
    pCanvas.width = 16;
    pCanvas.height = 16;
    const ctx = pCanvas.getContext('2d');
    if (ctx) {
      const grad = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
      grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
      grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 16, 16);
    }
    const texture = new THREE.CanvasTexture(pCanvas);

    const material = new THREE.PointsMaterial({
      size: 0.12,
      vertexColors: true,
      map: texture,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);

    // Generate indices for connecting lines (constellation network)
    const lineIndices: number[] = [];
    for (let x = 0; x < particleCountX; x++) {
      for (let z = 0; z < particleCountZ; z++) {
        const idx = x * particleCountZ + z;
        if (x + 1 < particleCountX) {
          const rightIdx = (x + 1) * particleCountZ + z;
          lineIndices.push(idx, rightIdx);
        }
        if (z + 1 < particleCountZ) {
          const downIdx = x * particleCountZ + (z + 1);
          lineIndices.push(idx, downIdx);
        }
      }
    }
    geometry.setIndex(lineIndices);

    // Semitransparent glowing link material
    const lineMaterial = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.16,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    this.lines = new THREE.LineSegments(geometry, lineMaterial);
    this.scene.add(this.lines);

    // Track mouse move for parallax effect
    // We bind it to the left-half container
    const leftHalf = document.querySelector('.left-half');
    if (leftHalf) {
      leftHalf.addEventListener('mousemove', this.onMouseMove.bind(this));
      leftHalf.addEventListener('mouseleave', this.onMouseLeave.bind(this));
    }

    // Resize handling via ResizeObserver
    const resizeObserver = new ResizeObserver(entries => {
      if (!entries || entries.length === 0) return;
      const rect = entries[0].contentRect;
      this.onResize(rect.width, rect.height);
    });
    resizeObserver.observe(container);

    // Start animation loop
    this.animate();
  }

  private onMouseMove(e: Event) {
    const mouseEvent = e as MouseEvent;
    const leftHalf = document.querySelector('.left-half');
    if (!leftHalf) return;
    const rect = leftHalf.getBoundingClientRect();
    const x = ((mouseEvent.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((mouseEvent.clientY - rect.top) / rect.height) * 2 + 1;
    this.mouse.x = x;
    this.mouse.y = y;
  }

  private onMouseLeave() {
    this.mouse.x = 0;
    this.mouse.y = 0;
  }

  private onResize(width: number, height: number) {
    if (!this.camera || !this.renderer) return;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  private animate() {
    this.animationFrameId = requestAnimationFrame(() => this.animate());

    if (!this.scene || !this.camera || !this.renderer) return;

    const time = this.clock.getElapsedTime();
    const positions = this.particles.geometry.attributes['position'].array as Float32Array;
    const count = positions.length / 3;

    // Calculate wave heights
    if (!this.prefersReducedMotion) {
      let index = 0;
      // Calculate mouse attraction point in grid units
      const mouseTargetX = this.mouse.x * 6;
      const mouseTargetZ = -this.mouse.y * 6;

      for (let i = 0; i < count; i++) {
        const x = positions[index];
        const z = positions[index + 2];

        // Complex wave formula: sine waves based on distance and coordinates
        const dist = Math.sqrt(x * x + z * z);
        
        // Calculate distance from grid node to mouse target
        const dx = x - mouseTargetX;
        const dz = z - mouseTargetZ;
        const mouseDist = Math.sqrt(dx * dx + dz * dz);
        
        // Symmetrical swell under cursor
        const gravitySwell = Math.max(0, 2.0 - mouseDist) * 0.35;

        positions[index + 1] = Math.sin(x * 1.5 + time * 1.5) * 0.4 +
                               Math.cos(z * 1.5 + time * 1.2) * 0.3 +
                               Math.sin(dist * 2.0 - time * 2.0) * 0.2 +
                               gravitySwell;

        index += 3;
      }
      this.particles.geometry.attributes['position'].needsUpdate = true;
    }

    // Parallax effect on camera position
    this.targetCameraPos.x = this.mouse.x * 2.5;
    this.targetCameraPos.y = 4 + this.mouse.y * 1.5;
    
    // Smooth camera interpolation (lerp)
    this.camera.position.x += (this.targetCameraPos.x - this.camera.position.x) * 0.05;
    this.camera.position.y += (this.targetCameraPos.y - this.camera.position.y) * 0.05;
    this.camera.lookAt(0, 0, 0);

    // Gently rotate particle grid and lines
    if (!this.prefersReducedMotion) {
      this.particles.rotation.y = time * 0.05;
      if (this.lines) {
        this.lines.rotation.y = time * 0.05;
      }
    }

    this.renderer.render(this.scene, this.camera);
  }

  ngOnDestroy() {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    mq.removeEventListener('change', this.motionQueryListener);

    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }

    const leftHalf = document.querySelector('.left-half');
    if (leftHalf) {
      // Event listeners automatically cleaned up on DOM removal but clean them just in case
      leftHalf.removeEventListener('mousemove', this.onMouseMove.bind(this));
      leftHalf.removeEventListener('mouseleave', this.onMouseLeave.bind(this));
    }
    
    if (this.renderer) {
      this.renderer.dispose();
    }
    
    if (this.lines) {
      if (Array.isArray(this.lines.material)) {
        this.lines.material.forEach(m => m.dispose());
      } else {
        this.lines.material.dispose();
      }
    }
    
    if (this.particles) {
      this.particles.geometry.dispose();
      if (Array.isArray(this.particles.material)) {
        this.particles.material.forEach(m => m.dispose());
      } else {
        this.particles.material.dispose();
      }
    }
  }

  switchTab(tab: 'login' | 'signup') {
    this.activeTab = tab;
    this.errorMsg = '';
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  onLogin() {
    if (!this.loginData.email || !this.loginData.password) {
      this.errorMsg = 'Please fill in all fields';
      return;
    }
    
    this.loading = true;
    this.authService.login(this.loginData).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        console.error('Login error details:', err);
        this.errorMsg = err.message || err.error?.detail || 'Invalid credentials. Please try again.';
      }
    });
  }

  onSignup() {
    if (!this.signupData.name || !this.signupData.email || !this.signupData.password) {
      this.errorMsg = 'Please fill in all fields';
      return;
    }
    
    if (this.signupData.password !== this.signupData.confirmPassword) {
      this.errorMsg = 'Passwords do not match';
      return;
    }
    
    this.loading = true;
    const data = {
      name: this.signupData.name,
      email: this.signupData.email,
      password: this.signupData.password
    };
    
    this.authService.signup(data).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        console.error('Signup error details:', err);
        this.errorMsg = err.message || err.error?.detail || 'Error creating account. Please try again.';
      }
    });
  }
}
