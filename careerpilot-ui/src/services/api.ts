import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface UserRegistrationPayload {
  username: string;
  email: string;
  password: string;
}

export interface UserLoginPayload {
  usernameOrEmail: string;
  password: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  role: string;
  createdAt: string;
}

export const authService = {
  register: async (payload: UserRegistrationPayload): Promise<UserResponse> => {
    const res = await api.post<UserResponse>('/auth/register', payload);
    return res.data;
  },
  login: async (payload: UserLoginPayload): Promise<UserResponse> => {
    const res = await api.post<UserResponse>('/auth/login', payload);
    return res.data;
  },
  getUser: async (id: number): Promise<UserResponse> => {
    const res = await api.get<UserResponse>(`/auth/users/${id}`);
    return res.data;
  },
  getAllUsers: async (): Promise<UserResponse[]> => {
    const res = await api.get<UserResponse[]>('/auth/users');
    return res.data;
  },
};

export default api;
