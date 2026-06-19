import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.scss'
})
export class AuthComponent {
  activeTab: 'login' | 'signup' = 'login';
  showPassword = false;
  
  loginData = { email: '', password: '' };
  signupData = { name: '', email: '', password: '', confirmPassword: '' };
  
  errorMsg = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

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
        this.errorMsg = err.error?.detail || 'Invalid credentials. Please try again.';
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
        this.errorMsg = err.error?.detail || 'Error creating account. Please try again.';
      }
    });
  }
}
