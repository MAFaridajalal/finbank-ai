import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-data-browser',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatTabsModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatSnackBarModule
  ],
  template: `
    <div class="data-browser-container">
      <h2>Data Browser</h2>

      <mat-tab-group (selectedTabChange)="onTabChange($event)" animationDuration="200ms">
        <mat-tab label="Customers">
          <ng-template matTabContent>
            <div class="table-container">
              @if (loading) {
                <div class="loading-spinner">
                  <mat-spinner diameter="40"></mat-spinner>
                </div>
              } @else {
                <table mat-table [dataSource]="customers" class="data-table">
                  <ng-container matColumnDef="id">
                    <th mat-header-cell *matHeaderCellDef>ID</th>
                    <td mat-cell *matCellDef="let row">{{ row.id }}</td>
                  </ng-container>
                  <ng-container matColumnDef="name">
                    <th mat-header-cell *matHeaderCellDef>Name</th>
                    <td mat-cell *matCellDef="let row">{{ row.first_name }} {{ row.last_name }}</td>
                  </ng-container>
                  <ng-container matColumnDef="email">
                    <th mat-header-cell *matHeaderCellDef>Email</th>
                    <td mat-cell *matCellDef="let row">{{ row.email }}</td>
                  </ng-container>
                  <ng-container matColumnDef="tier">
                    <th mat-header-cell *matHeaderCellDef>Tier</th>
                    <td mat-cell *matCellDef="let row">
                      <mat-chip [class]="'tier-' + row.tier_name?.toLowerCase()">{{ row.tier_name }}</mat-chip>
                    </td>
                  </ng-container>
                  <ng-container matColumnDef="branch">
                    <th mat-header-cell *matHeaderCellDef>Branch</th>
                    <td mat-cell *matCellDef="let row">{{ row.branch_name }}</td>
                  </ng-container>
                  <ng-container matColumnDef="actions">
                    <th mat-header-cell *matHeaderCellDef>Actions</th>
                    <td mat-cell *matCellDef="let row">
                      <button mat-icon-button color="primary" (click)="editCustomer(row)" matTooltip="Edit">
                        <mat-icon>edit</mat-icon>
                      </button>
                      <button mat-icon-button color="warn" (click)="deleteCustomer(row)" matTooltip="Delete">
                        <mat-icon>delete</mat-icon>
                      </button>
                    </td>
                  </ng-container>

                  <tr mat-header-row *matHeaderRowDef="customerColumns"></tr>
                  <tr mat-row *matRowDef="let row; columns: customerColumns;"></tr>
                </table>
                <mat-paginator
                  [length]="totalCustomers"
                  [pageSize]="pageSize"
                  [pageSizeOptions]="[5, 10, 25]"
                  (page)="onPageChange($event, 'customers')">
                </mat-paginator>
              }
            </div>
          </ng-template>
        </mat-tab>

        <mat-tab label="Accounts">
          <ng-template matTabContent>
            <div class="table-container">
              @if (loading) {
                <div class="loading-spinner">
                  <mat-spinner diameter="40"></mat-spinner>
                </div>
              } @else {
                <table mat-table [dataSource]="accounts" class="data-table">
                  <ng-container matColumnDef="account_number">
                    <th mat-header-cell *matHeaderCellDef>Account #</th>
                    <td mat-cell *matCellDef="let row">{{ row.account_number }}</td>
                  </ng-container>
                  <ng-container matColumnDef="customer">
                    <th mat-header-cell *matHeaderCellDef>Customer</th>
                    <td mat-cell *matCellDef="let row">{{ row.customer_name }}</td>
                  </ng-container>
                  <ng-container matColumnDef="type">
                    <th mat-header-cell *matHeaderCellDef>Type</th>
                    <td mat-cell *matCellDef="let row">
                      <mat-icon class="account-icon">{{ getAccountIcon(row.type_name) }}</mat-icon>
                      {{ row.type_name }}
                    </td>
                  </ng-container>
                  <ng-container matColumnDef="balance">
                    <th mat-header-cell *matHeaderCellDef>Balance</th>
                    <td mat-cell *matCellDef="let row" class="currency">{{ row.balance | currency }}</td>
                  </ng-container>
                  <ng-container matColumnDef="status">
                    <th mat-header-cell *matHeaderCellDef>Status</th>
                    <td mat-cell *matCellDef="let row">
                      <mat-chip [class]="'status-' + row.status">{{ row.status }}</mat-chip>
                    </td>
                  </ng-container>

                  <tr mat-header-row *matHeaderRowDef="accountColumns"></tr>
                  <tr mat-row *matRowDef="let row; columns: accountColumns;"></tr>
                </table>
                <mat-paginator
                  [length]="totalAccounts"
                  [pageSize]="pageSize"
                  [pageSizeOptions]="[5, 10, 25]"
                  (page)="onPageChange($event, 'accounts')">
                </mat-paginator>
              }
            </div>
          </ng-template>
        </mat-tab>

        <mat-tab label="Transactions">
          <ng-template matTabContent>
            <div class="table-container">
              @if (loading) {
                <div class="loading-spinner">
                  <mat-spinner diameter="40"></mat-spinner>
                </div>
              } @else {
                <table mat-table [dataSource]="transactions" class="data-table">
                  <ng-container matColumnDef="transaction_id">
                    <th mat-header-cell *matHeaderCellDef>Transaction ID</th>
                    <td mat-cell *matCellDef="let row">{{ row.transaction_id }}</td>
                  </ng-container>
                  <ng-container matColumnDef="type">
                    <th mat-header-cell *matHeaderCellDef>Type</th>
                    <td mat-cell *matCellDef="let row">
                      <mat-chip [class]="'txn-' + row.type">{{ row.type }}</mat-chip>
                    </td>
                  </ng-container>
                  <ng-container matColumnDef="amount">
                    <th mat-header-cell *matHeaderCellDef>Amount</th>
                    <td mat-cell *matCellDef="let row" class="currency">{{ row.amount | currency }}</td>
                  </ng-container>
                  <ng-container matColumnDef="description">
                    <th mat-header-cell *matHeaderCellDef>Description</th>
                    <td mat-cell *matCellDef="let row">{{ row.description }}</td>
                  </ng-container>
                  <ng-container matColumnDef="created_at">
                    <th mat-header-cell *matHeaderCellDef>Date</th>
                    <td mat-cell *matCellDef="let row">{{ row.created_at | date:'short' }}</td>
                  </ng-container>

                  <tr mat-header-row *matHeaderRowDef="transactionColumns"></tr>
                  <tr mat-row *matRowDef="let row; columns: transactionColumns;"></tr>
                </table>
                <mat-paginator
                  [length]="totalTransactions"
                  [pageSize]="pageSize"
                  [pageSizeOptions]="[5, 10, 25]"
                  (page)="onPageChange($event, 'transactions')">
                </mat-paginator>
              }
            </div>
          </ng-template>
        </mat-tab>

        <mat-tab label="Loans">
          <ng-template matTabContent>
            <div class="table-container">
              @if (loading) {
                <div class="loading-spinner">
                  <mat-spinner diameter="40"></mat-spinner>
                </div>
              } @else {
                <table mat-table [dataSource]="loans" class="data-table">
                  <ng-container matColumnDef="loan_number">
                    <th mat-header-cell *matHeaderCellDef>Loan #</th>
                    <td mat-cell *matCellDef="let row">{{ row.loan_number }}</td>
                  </ng-container>
                  <ng-container matColumnDef="customer">
                    <th mat-header-cell *matHeaderCellDef>Customer</th>
                    <td mat-cell *matCellDef="let row">{{ row.customer_name }}</td>
                  </ng-container>
                  <ng-container matColumnDef="type">
                    <th mat-header-cell *matHeaderCellDef>Type</th>
                    <td mat-cell *matCellDef="let row">{{ row.type }}</td>
                  </ng-container>
                  <ng-container matColumnDef="principal">
                    <th mat-header-cell *matHeaderCellDef>Principal</th>
                    <td mat-cell *matCellDef="let row" class="currency">{{ row.principal | currency }}</td>
                  </ng-container>
                  <ng-container matColumnDef="remaining">
                    <th mat-header-cell *matHeaderCellDef>Remaining</th>
                    <td mat-cell *matCellDef="let row" class="currency">{{ row.remaining_balance | currency }}</td>
                  </ng-container>
                  <ng-container matColumnDef="status">
                    <th mat-header-cell *matHeaderCellDef>Status</th>
                    <td mat-cell *matCellDef="let row">
                      <mat-chip [class]="'status-' + row.status">{{ row.status }}</mat-chip>
                    </td>
                  </ng-container>

                  <tr mat-header-row *matHeaderRowDef="loanColumns"></tr>
                  <tr mat-row *matRowDef="let row; columns: loanColumns;"></tr>
                </table>
                <mat-paginator
                  [length]="totalLoans"
                  [pageSize]="pageSize"
                  [pageSizeOptions]="[5, 10, 25]"
                  (page)="onPageChange($event, 'loans')">
                </mat-paginator>
              }
            </div>
          </ng-template>
        </mat-tab>
      </mat-tab-group>

      <!-- Edit Customer Dialog -->
      @if (editingCustomer) {
        <div class="edit-overlay" (click)="cancelEdit()">
          <div class="edit-dialog" (click)="$event.stopPropagation()">
            <h3>Edit Customer</h3>
            <div class="edit-form">
              <mat-form-field>
                <mat-label>First Name</mat-label>
                <input matInput [(ngModel)]="editingCustomer.first_name">
              </mat-form-field>
              <mat-form-field>
                <mat-label>Last Name</mat-label>
                <input matInput [(ngModel)]="editingCustomer.last_name">
              </mat-form-field>
              <mat-form-field>
                <mat-label>Email</mat-label>
                <input matInput [(ngModel)]="editingCustomer.email">
              </mat-form-field>
              <mat-form-field>
                <mat-label>Phone</mat-label>
                <input matInput [(ngModel)]="editingCustomer.phone">
              </mat-form-field>
              <mat-form-field>
                <mat-label>City</mat-label>
                <input matInput [(ngModel)]="editingCustomer.city">
              </mat-form-field>
              <mat-form-field>
                <mat-label>Tier</mat-label>
                <mat-select [(ngModel)]="editingCustomer.tier_name">
                  <mat-option value="Basic">Basic</mat-option>
                  <mat-option value="Premium">Premium</mat-option>
                  <mat-option value="VIP">VIP</mat-option>
                </mat-select>
              </mat-form-field>
            </div>
            <div class="edit-actions">
              <button mat-button (click)="cancelEdit()">Cancel</button>
              <button mat-raised-button color="primary" (click)="saveCustomer()" [disabled]="saving">
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .data-browser-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    h2 {
      margin-bottom: 24px;
      color: #333;
    }

    .table-container {
      margin-top: 16px;
      background: white;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .loading-spinner {
      display: flex;
      justify-content: center;
      padding: 48px;
    }

    .data-table {
      width: 100%;
    }

    .data-table th {
      background: #f5f5f5;
      font-weight: 500;
      color: #333;
    }

    .data-table td, .data-table th {
      padding: 16px;
    }

    .data-table tr:hover {
      background: #fafafa;
    }

    .currency {
      font-family: 'Roboto Mono', monospace;
      font-weight: 500;
    }

    .account-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      vertical-align: middle;
      margin-right: 4px;
      color: #666;
    }

    mat-chip {
      font-size: 12px;
    }

    .tier-basic { background: #e0e0e0 !important; }
    .tier-premium { background: #e3f2fd !important; color: #1565c0 !important; }
    .tier-vip { background: #fce4ec !important; color: #c2185b !important; }

    .status-active { background: #e8f5e9 !important; color: #2e7d32 !important; }
    .status-inactive { background: #ffebee !important; color: #c62828 !important; }
    .status-pending { background: #fff3e0 !important; color: #ef6c00 !important; }

    .txn-deposit { background: #e8f5e9 !important; color: #2e7d32 !important; }
    .txn-withdrawal { background: #ffebee !important; color: #c62828 !important; }
    .txn-transfer { background: #e3f2fd !important; color: #1565c0 !important; }

    mat-paginator {
      border-top: 1px solid #e0e0e0;
    }

    .actions-cell {
      white-space: nowrap;
    }

    .edit-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .edit-dialog {
      background: white;
      padding: 24px;
      border-radius: 8px;
      min-width: 400px;
      max-width: 500px;
    }

    .edit-dialog h3 {
      margin: 0 0 16px 0;
    }

    .edit-form {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .edit-form mat-form-field {
      width: 100%;
    }

    .edit-actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      margin-top: 16px;
    }
  `]
})
export class DataBrowserComponent implements OnInit {
  loading = false;
  saving = false;
  pageSize = 10;

  customers: any[] = [];
  accounts: any[] = [];
  transactions: any[] = [];
  loans: any[] = [];

  totalCustomers = 0;
  totalAccounts = 0;
  totalTransactions = 0;
  totalLoans = 0;

  customerColumns = ['id', 'name', 'email', 'tier', 'branch', 'actions'];
  accountColumns = ['account_number', 'customer', 'type', 'balance', 'status'];
  transactionColumns = ['transaction_id', 'type', 'amount', 'description', 'created_at'];
  loanColumns = ['loan_number', 'customer', 'type', 'principal', 'remaining', 'status'];

  editingCustomer: any = null;
  originalCustomer: any = null;

  constructor(private apiService: ApiService, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.loadCustomers(0, this.pageSize);
  }

  onTabChange(event: any): void {
    const tabIndex = event.index;
    switch (tabIndex) {
      case 0:
        if (this.customers.length === 0) this.loadCustomers(0, this.pageSize);
        break;
      case 1:
        if (this.accounts.length === 0) this.loadAccounts(0, this.pageSize);
        break;
      case 2:
        if (this.transactions.length === 0) this.loadTransactions(0, this.pageSize);
        break;
      case 3:
        if (this.loans.length === 0) this.loadLoans(0, this.pageSize);
        break;
    }
  }

  onPageChange(event: PageEvent, table: string): void {
    const offset = event.pageIndex * event.pageSize;
    switch (table) {
      case 'customers':
        this.loadCustomers(offset, event.pageSize);
        break;
      case 'accounts':
        this.loadAccounts(offset, event.pageSize);
        break;
      case 'transactions':
        this.loadTransactions(offset, event.pageSize);
        break;
      case 'loans':
        this.loadLoans(offset, event.pageSize);
        break;
    }
  }

  loadCustomers(offset: number, limit: number): void {
    this.loading = true;
    this.apiService.getCustomers(limit, offset).subscribe({
      next: (response) => {
        this.customers = response.data || [];
        this.totalCustomers = response.total || 0;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  loadAccounts(offset: number, limit: number): void {
    this.loading = true;
    this.apiService.getAccounts(limit, offset).subscribe({
      next: (response) => {
        this.accounts = response.data || [];
        this.totalAccounts = response.total || 0;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  loadTransactions(offset: number, limit: number): void {
    this.loading = true;
    this.apiService.getTransactions(limit, offset).subscribe({
      next: (response) => {
        this.transactions = response.data || [];
        this.totalTransactions = response.total || 0;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  loadLoans(offset: number, limit: number): void {
    this.loading = true;
    this.apiService.getLoans(limit, offset).subscribe({
      next: (response) => {
        this.loans = response.data || [];
        this.totalLoans = response.total || 0;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  getAccountIcon(type: string): string {
    switch (type?.toLowerCase()) {
      case 'checking': return 'account_balance_wallet';
      case 'savings': return 'savings';
      case 'investment': return 'trending_up';
      default: return 'account_balance';
    }
  }

  editCustomer(customer: any): void {
    this.originalCustomer = customer;
    this.editingCustomer = { ...customer };
  }

  cancelEdit(): void {
    this.editingCustomer = null;
    this.originalCustomer = null;
  }

  saveCustomer(): void {
    if (!this.editingCustomer) return;

    this.saving = true;
    const updates: any = {};

    if (this.editingCustomer.first_name !== this.originalCustomer.first_name) {
      updates.first_name = this.editingCustomer.first_name;
    }
    if (this.editingCustomer.last_name !== this.originalCustomer.last_name) {
      updates.last_name = this.editingCustomer.last_name;
    }
    if (this.editingCustomer.email !== this.originalCustomer.email) {
      updates.email = this.editingCustomer.email;
    }
    if (this.editingCustomer.phone !== this.originalCustomer.phone) {
      updates.phone = this.editingCustomer.phone;
    }
    if (this.editingCustomer.city !== this.originalCustomer.city) {
      updates.city = this.editingCustomer.city;
    }
    if (this.editingCustomer.tier_name !== this.originalCustomer.tier_name) {
      updates.tier = this.editingCustomer.tier_name;
    }

    this.apiService.updateCustomer(this.editingCustomer.id, updates).subscribe({
      next: (response) => {
        this.saving = false;
        if (response.success) {
          this.snackBar.open(response.message, 'Close', { duration: 3000 });
          this.loadCustomers(0, this.pageSize);
          this.cancelEdit();
        } else {
          const errorMsg = response.errors ? Object.values(response.errors).join(', ') : response.message;
          this.snackBar.open(errorMsg, 'Close', { duration: 5000 });
        }
      },
      error: (err) => {
        this.saving = false;
        this.snackBar.open('Update failed: ' + err.message, 'Close', { duration: 5000 });
      }
    });
  }

  deleteCustomer(customer: any): void {
    if (!confirm(`Are you sure you want to delete ${customer.first_name} ${customer.last_name}?`)) {
      return;
    }

    this.apiService.deleteCustomer(customer.id).subscribe({
      next: (response) => {
        if (response.success) {
          this.snackBar.open(response.message, 'Close', { duration: 3000 });
          this.loadCustomers(0, this.pageSize);
        } else {
          this.snackBar.open(response.message, 'Close', { duration: 5000 });
        }
      },
      error: (err) => {
        this.snackBar.open('Delete failed: ' + err.message, 'Close', { duration: 5000 });
      }
    });
  }
}
