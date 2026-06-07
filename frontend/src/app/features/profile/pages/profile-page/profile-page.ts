import { Component, inject, OnInit, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../../core/services/auth';
import { ReviewService } from '../../../../core/services/review';
import { DatePipe } from '@angular/common';
import { forkJoin } from 'rxjs';
import { Review } from '../../../../core/models/review.model';

interface UserInfo {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  role_display: string;
  course: number;
  date_joined: string;
}

interface ProfessorItem {
  prof_id: number;
  name: string;
}

interface SubjectItem {
  subj_id: number;
  name: string;
}

@Component({
  selector: 'app-profile-page',
  imports: [RouterLink, DatePipe, FormsModule],
  templateUrl: './profile-page.html',
  styleUrl: './profile-page.css',
})
export class ProfilePage implements OnInit {
  private http = inject(HttpClient);
  private router = inject(Router);
  private authService = inject(AuthService);
  private reviewService = inject(ReviewService);

  user = signal<UserInfo | null>(null);
  reviews = signal<Review[]>([]);
  loading = signal(true);
  reviewsError = signal('');

  professorMap = signal<Record<number, string>>({});
  subjectMap = signal<Record<number, string>>({});

  editingId = signal<number | null>(null);
  editForm = { rating: 5, difficulty: 3, text: '' };
  editSaving = signal(false);
  editError = signal('');

  deletingId = signal<number | null>(null);

  ngOnInit(): void {
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login']);
      return;
    }

    this.loadData();
  }

  private loadData(): void {
    forkJoin({
      me: this.http.get<UserInfo>('http://localhost:8000/me/'),
      reviews: this.http.get<Review[]>('http://localhost:8000/reviews/'),
      professors: this.http.get<ProfessorItem[]>('http://localhost:8000/professors/'),
      subjects: this.http.get<SubjectItem[]>('http://localhost:8000/subjects/'),
    }).subscribe({
      next: ({ me, reviews, professors, subjects }) => {
        this.user.set(me);

        const profMap: Record<number, string> = {};
        professors.forEach(p => profMap[p.prof_id] = p.name);
        this.professorMap.set(profMap);

        const subjMap: Record<number, string> = {};
        subjects.forEach(s => subjMap[s.subj_id] = s.name);
        this.subjectMap.set(subjMap);

        const myReviews = reviews.filter(r => r.user === me.id);
        this.reviews.set(myReviews);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load data:', err);
        this.reviewsError.set(
          err.status === 401
            ? 'Сессия истекла. Войдите снова.'
            : 'Не удалось загрузить данные профиля.'
        );
        this.loading.set(false);
      }
    });
  }

  getProfessorName(id: number): string {
    return this.professorMap()[id] ?? `Преподаватель #${id}`;
  }

  getSubjectName(id: number): string {
    return this.subjectMap()[id] ?? `Предмет #${id}`;
  }

  logout(): void {
    this.authService.logout();
  }

  getStars(rating: number): string {
    const full = Math.round(Math.max(0, Math.min(5, rating)));
    return '★'.repeat(full) + '☆'.repeat(5 - full);
  }

  startEdit(review: Review): void {
    this.editingId.set(review.rev_id);
    this.editForm = {
      rating: review.rating,
      difficulty: review.difficulty,
      text: review.text
    };
    this.editError.set('');
  }

  cancelEdit(): void {
    this.editingId.set(null);
    this.editError.set('');
  }

  saveEdit(): void {
    const revId = this.editingId();
    if (!revId) return;
    if (!this.editForm.text.trim()) {
      this.editError.set('Текст отзыва не может быть пустым');
      return;
    }

    this.editSaving.set(true);
    this.reviewService.update(revId, this.editForm).subscribe({
      next: () => {
        const updated = this.reviews().map(
          r => r.rev_id === revId
            ? { ...r, rating: this.editForm.rating, difficulty: this.editForm.difficulty, text: this.editForm.text }
            : r
        );
        this.reviews.set(updated);
        this.editingId.set(null);
        this.editSaving.set(false);
      },
      error: () => {
        this.editError.set('Не удалось сохранить. Попробуйте ещё раз.');
        this.editSaving.set(false);
      }
    });
  }

  confirmDelete(revId: number): void {
    this.deletingId.set(revId);
  }

  cancelDelete(): void {
    this.deletingId.set(null);
  }

  deleteReview(): void {
    const revId = this.deletingId();
    if (!revId) return;

    this.reviewService.delete(revId).subscribe({
      next: () => {
        this.reviews.set(this.reviews().filter(r => r.rev_id !== revId));
        this.deletingId.set(null);
      },
      error: () => {
        this.deletingId.set(null);
      }
    });
  }
}
