export interface User {
    id: number;
    username: string;
}
export interface AuthResponse {
    access: string;
    refresh: string;
}
export interface RegisterRequest {
    username: string;
    password: string;
    first_name: string;
    last_name: string;
    email?: string;
    course?: number;
}
export interface LoginRequest {
  username: string;
  password: string;
}