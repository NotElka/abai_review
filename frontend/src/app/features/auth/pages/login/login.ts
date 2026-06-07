import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { LoginRequest } from '../../../../core/models/user.model';
import { AuthService } from '../../../../core/services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  username = '';
  password = '';
  
  loading = false;
  error = '';
  success = '';

  onSubmit(): void {
    this.error = '';
    this.success = '';

    if (!this.username.trim()) {
      this.error = 'Введите имя пользователя.';
      return;
    }

    if (!this.password.trim()) {
      this.error = 'Введите пароль.';
      return;
    }

    this.loading = true;

    const payload: LoginRequest = {
      username: this.username,
      password: this.password
    };

    this.authService.login(payload).subscribe({
      next: (res) => {
        this.authService.saveTokens(res);
        // Save username so profile can display it without JWT decoding
        localStorage.setItem('username', this.username.trim());
        this.authService.isAuthenticated.set(true);
        this.success = 'Вход выполнен! Перенаправление...';
        
        setTimeout(() => {
          this.router.navigate(['/']);
        }, 0);
      },
      error: (err) => {
        this.loading = false;
        
        if (err.status === 401) {
          this.error = 'Неверное имя пользователя или пароль.';
        } else if (err.status === 0) {
          this.error = 'Не удаётся подключиться к серверу.';
        } else {
          this.error = 'Ошибка входа. Попробуйте ещё раз.';
        }
        
        console.error('Login error:', err);
      },
      complete: () => {
        this.loading = false;
      }
    });
  }
}
