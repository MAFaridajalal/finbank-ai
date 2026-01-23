import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { AgentStatusComponent } from './components/agent-status/agent-status.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    AgentStatusComponent,
  ],
  template: `
    <mat-sidenav-container class="app-container">
      <mat-sidenav #sidenav mode="side" opened class="sidenav">
        <div class="sidenav-header">
          <mat-icon class="logo-icon">account_balance</mat-icon>
          <span class="logo-text">FinBank AI</span>
        </div>

        <mat-nav-list>
          <a mat-list-item routerLink="/chat" routerLinkActive="active">
            <mat-icon matListItemIcon>chat</mat-icon>
            <span matListItemTitle>Chat</span>
          </a>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active">
            <mat-icon matListItemIcon>dashboard</mat-icon>
            <span matListItemTitle>Dashboard</span>
          </a>
          <a mat-list-item routerLink="/data" routerLinkActive="active">
            <mat-icon matListItemIcon>table_chart</mat-icon>
            <span matListItemTitle>Data Browser</span>
          </a>
          <a mat-list-item routerLink="/agents" routerLinkActive="active">
            <mat-icon matListItemIcon>hub</mat-icon>
            <span matListItemTitle>AI Agents</span>
          </a>
          <a mat-list-item routerLink="/register" routerLinkActive="active">
            <mat-icon matListItemIcon>person_add</mat-icon>
            <span matListItemTitle>Register Customer</span>
          </a>
          <a mat-list-item routerLink="/settings" routerLinkActive="active">
            <mat-icon matListItemIcon>settings</mat-icon>
            <span matListItemTitle>Settings</span>
          </a>
        </mat-nav-list>

        <div class="sidenav-footer">
          <app-agent-status></app-agent-status>
        </div>
      </mat-sidenav>

      <mat-sidenav-content class="main-content">
        <mat-toolbar color="primary" class="toolbar">
          <button mat-icon-button (click)="sidenav.toggle()">
            <mat-icon>menu</mat-icon>
          </button>
          <span class="toolbar-title">Multi-Agent Banking Assistant</span>
          <span class="spacer"></span>
          <button mat-icon-button>
            <mat-icon>notifications</mat-icon>
          </button>
          <button mat-icon-button>
            <mat-icon>account_circle</mat-icon>
          </button>
        </mat-toolbar>

        <div class="content">
          <router-outlet></router-outlet>
        </div>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [`
    .app-container {
      height: 100vh;
    }

    .sidenav {
      width: 250px;
      background: #1a237e;
      color: white;
      display: flex;
      flex-direction: column;
    }

    .sidenav-header {
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    .logo-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
    }

    .logo-text {
      font-size: 20px;
      font-weight: 500;
    }

    .sidenav mat-nav-list {
      flex: 1;
    }

    .sidenav mat-nav-list a {
      color: rgba(255,255,255,0.8);
    }

    .sidenav mat-nav-list a.active {
      background: rgba(255,255,255,0.1);
      color: white;
    }

    .sidenav mat-nav-list a:hover {
      background: rgba(255,255,255,0.05);
    }

    .sidenav-footer {
      padding: 16px;
      border-top: 1px solid rgba(255,255,255,0.1);
    }

    .main-content {
      display: flex;
      flex-direction: column;
    }

    .toolbar {
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .toolbar-title {
      margin-left: 16px;
    }

    .spacer {
      flex: 1;
    }

    .content {
      flex: 1;
      padding: 24px;
      background: #f5f5f5;
      overflow-y: auto;
    }
  `]
})
export class AppComponent {
  title = 'FinBank AI';
}
