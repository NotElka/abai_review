import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { forkJoin } from 'rxjs';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-home-page',
  imports: [RouterLink],
  templateUrl: './home-page.html',
  styleUrl: './home-page.css'
})
export class HomePage implements OnInit {
  private http = inject(HttpClient);

  professorsCount = signal(0);
  subjectsCount = signal(0);

  ngOnInit(): void {
    forkJoin({
      professors: this.http.get<any[]>(`${environment.apiUrl}/professors/`),
      subjects: this.http.get<any[]>(`${environment.apiUrl}/subjects/`),
    }).subscribe({
      next: (data) => {
        this.professorsCount.set(data.professors.length);
        this.subjectsCount.set(data.subjects.length);
      },
      error: (err) => {
        console.error('Failed to load stats:', err);
      }
    });
  }
}
