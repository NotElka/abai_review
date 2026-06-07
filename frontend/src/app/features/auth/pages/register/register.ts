import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { AuthService } from '../../../../core/services/auth';
import { Router, RouterLink } from '@angular/router';
import { RegisterRequest } from '../../../../core/models/user.model';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class Register {
  private authService = inject(AuthService);
  private router = inject(Router);


  firstName = '';
  lastName = '';
  username = '';
  password = '';
  confirmPassword = '';
  email = '';
  course = 1;

  error = '';
  loading = false;
  success = '';

  onSubmit() {
    if (!this.firstName.trim() || !this.lastName.trim()) {
      this.error = 'Введите имя и фамилию';
      return;
    }

    if (!this.username.trim() || !this.password.trim()) {
      this.error = 'Введите имя пользователя и пароль';
      return;
    }

    if (this.password !== this.confirmPassword) {
      this.error = 'Пароли не совпадают';
      return;
    }

    if (this.password.length < 8) {
      this.error = 'Пароль должен содержать не менее 8 символов';
      return;
    }

    if (!this.email.trim()) {
      this.error = 'Введите электронную почту';
      return;
    }
    this.loading = true;
    this.error = '';
    this.success = '';
    const payload: RegisterRequest = {
      username: this.username,
      password: this.password,
      first_name: this.firstName.trim(),
      last_name: this.lastName.trim(),
      email: this.email.trim(),
      course: Number(this.course)
    };

    this.authService.register(payload).subscribe({
      next: (res) => {
        this.authService.saveTokens(res);
        this.authService.isAuthenticated.set(true);
        this.success = 'Регистрация успешна! Перенаправление на главную...';
        console.log('Tokens received:', res);
        setTimeout(() => {
          this.router.navigate(['/']);
        }, 0);
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Ошибка регистрации';
        console.error(err);
        if (err.status === 400) {
          if (err.error?.first_name) {
            this.error = err.error.first_name[0];
          } else if (err.error?.last_name) {
            this.error = err.error.last_name[0];
          } else if (err.error?.username) {
            this.error = err.error.username[0];
          } else if (err.error?.password) {
            this.error = err.error.password[0];
          } else if (err.error?.email) {
            this.error = err.error.email[0];
          } else if (err.error?.course) {
            this.error = err.error.course[0];
          } else {
            this.error = 'Неверные данные. Проверьте введённую информацию';
          }
        } else if (err.status === 0) {
          this.error = 'Не удаётся подключиться к серверу. Django запущен?';
        } else {
          this.error = 'Произошла непредвиденная ошибка сервера';
        }
      },
      complete: () => {
        this.loading = false;
      }
    });
  }
}
