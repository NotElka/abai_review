import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Professor } from '../models/professor.model';
import { environment } from '../../../environments/environment';

@Injectable({ 
  providedIn: 'root' 
})
export class ProfessorService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getAll(): Observable<Professor[]> {
    return this.http.get<Professor[]>(`${this.apiUrl}/professors/`);
  }
  getById(id: number): Observable<Professor> {
  return this.http.get<Professor>(`${this.apiUrl}/professors/${id}/`);
}
}