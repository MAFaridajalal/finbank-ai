import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { ApiService } from '../../services/api.service';

interface DashboardStats {
  totalDeposits: number;
  totalCustomers: number;
  activeLoans: number;
  loanValue: number;
  transactionsByBranch: { branch: string; count: number; percentage: number }[];
  recentAlerts: { message: string; type: 'warning' | 'success' | 'info' }[];
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatProgressBarModule],
  template: `
    <div class="dashboard-container">
      <h2>Dashboard</h2>

      <div class="metrics-row">
        <mat-card class="metric-card">
          <mat-card-content>
            <div class="metric-icon deposits">
              <mat-icon>account_balance</mat-icon>
            </div>
            <div class="metric-info">
              <span class="metric-label">Total Deposits</span>
              <span class="metric-value">{{ stats.totalDeposits | currency }}</span>
              <span class="metric-change positive">↑ 12% MTD</span>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="metric-card">
          <mat-card-content>
            <div class="metric-icon customers">
              <mat-icon>people</mat-icon>
            </div>
            <div class="metric-info">
              <span class="metric-label">Total Customers</span>
              <span class="metric-value">{{ stats.totalCustomers | number }}</span>
              <span class="metric-change positive">↑ 5% MTD</span>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="metric-card">
          <mat-card-content>
            <div class="metric-icon loans">
              <mat-icon>request_quote</mat-icon>
            </div>
            <div class="metric-info">
              <span class="metric-label">Active Loans</span>
              <span class="metric-value">{{ stats.activeLoans | number }}</span>
              <span class="metric-change neutral">{{ stats.loanValue | currency }} value</span>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <div class="charts-row">
        <mat-card class="chart-card">
          <mat-card-header>
            <mat-card-title>Transactions by Branch</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="branch-chart">
              @for (branch of stats.transactionsByBranch; track branch.branch) {
                <div class="branch-item">
                  <span class="branch-name">{{ branch.branch }}</span>
                  <div class="branch-bar-container">
                    <mat-progress-bar
                      mode="determinate"
                      [value]="branch.percentage">
                    </mat-progress-bar>
                  </div>
                  <span class="branch-percentage">{{ branch.percentage }}%</span>
                </div>
              }
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="chart-card alerts-card">
          <mat-card-header>
            <mat-card-title>Recent Alerts</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="alerts-list">
              @for (alert of stats.recentAlerts; track alert.message) {
                <div class="alert-item" [class]="alert.type">
                  <mat-icon>
                    {{ alert.type === 'warning' ? 'warning' : alert.type === 'success' ? 'check_circle' : 'info' }}
                  </mat-icon>
                  <span>{{ alert.message }}</span>
                </div>
              }
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    h2 {
      margin-bottom: 24px;
      color: #333;
    }

    .metrics-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
      margin-bottom: 24px;
    }

    .metric-card {
      mat-card-content {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 24px;
      }
    }

    .metric-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;

      mat-icon {
        font-size: 28px;
        width: 28px;
        height: 28px;
        color: white;
      }

      &.deposits { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
      &.customers { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
      &.loans { background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); }
    }

    .metric-info {
      display: flex;
      flex-direction: column;
    }

    .metric-label {
      font-size: 14px;
      color: #666;
    }

    .metric-value {
      font-size: 28px;
      font-weight: 500;
      color: #333;
    }

    .metric-change {
      font-size: 12px;
      &.positive { color: #4caf50; }
      &.negative { color: #f44336; }
      &.neutral { color: #666; }
    }

    .charts-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 24px;
    }

    .chart-card {
      mat-card-header {
        padding: 16px 16px 0;
      }

      mat-card-content {
        padding: 16px;
      }
    }

    .branch-chart {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .branch-item {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .branch-name {
      width: 100px;
      font-size: 14px;
    }

    .branch-bar-container {
      flex: 1;
      mat-progress-bar {
        height: 8px;
        border-radius: 4px;
      }
    }

    .branch-percentage {
      width: 40px;
      text-align: right;
      font-size: 14px;
      color: #666;
    }

    .alerts-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .alert-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 8px;
      font-size: 14px;

      mat-icon {
        font-size: 20px;
        width: 20px;
        height: 20px;
      }

      &.warning {
        background: #fff3e0;
        color: #e65100;
        mat-icon { color: #ff9800; }
      }

      &.success {
        background: #e8f5e9;
        color: #2e7d32;
        mat-icon { color: #4caf50; }
      }

      &.info {
        background: #e3f2fd;
        color: #1565c0;
        mat-icon { color: #2196f3; }
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  stats: DashboardStats = {
    totalDeposits: 2500000,
    totalCustomers: 1234,
    activeLoans: 456,
    loanValue: 12500000,
    transactionsByBranch: [
      { branch: 'Downtown', count: 1234, percentage: 45 },
      { branch: 'Westside', count: 823, percentage: 30 },
      { branch: 'Airport', count: 686, percentage: 25 },
    ],
    recentAlerts: [
      { message: '$15K withdrawal flagged for review', type: 'warning' },
      { message: 'New large transfer detected', type: 'warning' },
      { message: 'All systems operational', type: 'success' },
    ]
  };

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadStats();
  }

  loadStats(): void {
    this.apiService.getDashboardStats().subscribe({
      next: (response) => {
        if (response) {
          this.stats = { ...this.stats, ...response };
        }
      },
      error: (err) => {
        console.error('Failed to load dashboard stats:', err);
      }
    });
  }
}
