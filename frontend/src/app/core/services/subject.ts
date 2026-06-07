import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Subject } from '../models/subject.model';
import { environment } from '../../../environments/environment';

@Injectable({ 
  providedIn: 'root' 
})
export class SubjectService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getAll(): Observable<Subject[]> {
    return this.http.get<Subject[]>(`${this.apiUrl}/subjects/`);
  }

  getById(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/subjects/${id}/`);
  }
}