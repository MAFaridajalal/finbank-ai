import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Agent,
  Provider,
  Customer,
  Account,
  Transaction,
  Loan,
  DashboardStats
} from '../models/types';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  // Health check
  healthCheck(): Observable<{ status: string }> {
    return this.http.get<{ status: string }>(`${this.baseUrl}/health`);
  }

  // Agents
  getAgents(): Observable<{ agents: Agent[] }> {
    return this.http.get<{ agents: Agent[] }>(`${this.baseUrl}/api/agents`);
  }

  // Providers
  getProviders(): Observable<{ providers: Provider[]; default: string }> {
    return this.http.get<{ providers: Provider[]; default: string }>(`${this.baseUrl}/api/providers`);
  }

  // Chat (non-streaming)
  sendMessage(message: string, provider?: string): Observable<{ response: string; agents_used: string[] }> {
    return this.http.post<{ response: string; agents_used: string[] }>(`${this.baseUrl}/api/chat`, {
      message,
      provider
    });
  }

  // Dashboard
  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.baseUrl}/api/dashboard/stats`);
  }

  // Data Browser
  getCustomers(limit = 50, offset = 0): Observable<{ data: Customer[]; total: number }> {
    return this.http.get<{ data: Customer[]; total: number }>(`${this.baseUrl}/api/data/customers?limit=${limit}&offset=${offset}`);
  }

  getAccounts(limit = 50, offset = 0): Observable<{ data: Account[]; total: number }> {
    return this.http.get<{ data: Account[]; total: number }>(`${this.baseUrl}/api/data/accounts?limit=${limit}&offset=${offset}`);
  }

  getTransactions(limit = 50, offset = 0): Observable<{ data: Transaction[]; total: number }> {
    return this.http.get<{ data: Transaction[]; total: number }>(`${this.baseUrl}/api/data/transactions?limit=${limit}&offset=${offset}`);
  }

  getLoans(limit = 50, offset = 0): Observable<{ data: Loan[]; total: number }> {
    return this.http.get<{ data: Loan[]; total: number }>(`${this.baseUrl}/api/data/loans?limit=${limit}&offset=${offset}`);
  }

  getBranches(): Observable<{ data: any[] }> {
    return this.http.get<{ data: any[] }>(`${this.baseUrl}/api/data/branches`);
  }

  // Customer Management
  createCustomer(customerData: {
    first_name: string;
    last_name: string;
    email: string;
    phone?: string;
    address?: string;
    city?: string;
    tier?: string;
    branch?: string;
  }): Observable<{
    success: boolean;
    customer_id?: number;
    message: string;
    errors?: { [key: string]: string };
  }> {
    return this.http.post<any>(`${this.baseUrl}/api/customers`, customerData);
  }

  updateCustomer(customerId: number, data: {
    first_name?: string;
    last_name?: string;
    email?: string;
    phone?: string;
    address?: string;
    city?: string;
    tier?: string;
    branch?: string;
  }): Observable<{
    success: boolean;
    customer_id?: number;
    message: string;
    errors?: { [key: string]: string };
  }> {
    return this.http.put<any>(`${this.baseUrl}/api/customers/${customerId}`, data);
  }

  deleteCustomer(customerId: number): Observable<{
    success: boolean;
    customer_id?: number;
    message: string;
    errors?: { [key: string]: string };
  }> {
    return this.http.delete<any>(`${this.baseUrl}/api/customers/${customerId}`);
  }

  // Settings
  updateProvider(provider: string, model: string): Observable<{ success: boolean }> {
    return this.http.post<{ success: boolean }>(`${this.baseUrl}/api/settings/provider`, {
      provider,
      model
    });
  }
}
