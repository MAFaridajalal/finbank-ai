import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subscription } from 'rxjs';

import { WebSocketService } from '../../services/websocket.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-agent-status',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatProgressSpinnerModule],
  template: `
    <div class="status-panel">
      <div class="status-item">
        <mat-icon [class.connected]="isConnected" [class.disconnected]="!isConnected">
          {{ isConnected ? 'wifi' : 'wifi_off' }}
        </mat-icon>
        <span>{{ isConnected ? 'Connected' : 'Disconnected' }}</span>
      </div>

      <div class="status-item">
        <mat-icon>memory</mat-icon>
        <span>LLM: {{ currentProvider }}</span>
      </div>

      <div class="status-item">
        <mat-icon>hub</mat-icon>
        <span>Agents: {{ agentCount }}</span>
      </div>

      @if (!isConnected) {
        <button class="reconnect-btn" (click)="reconnect()">
          Reconnect
        </button>
      }
    </div>
  `,
  styles: [`
    .status-panel {
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 12px;
      color: rgba(255,255,255,0.7);
    }

    .status-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-item mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }

    .status-item mat-icon.connected {
      color: #4caf50;
    }

    .status-item mat-icon.disconnected {
      color: #f44336;
    }

    .reconnect-btn {
      margin-top: 8px;
      padding: 4px 12px;
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      border-radius: 4px;
      color: white;
      cursor: pointer;
    }

    .reconnect-btn:hover {
      background: rgba(255,255,255,0.2);
    }
  `]
})
export class AgentStatusComponent implements OnInit, OnDestroy {
  isConnected = false;
  currentProvider = 'OpenAI';
  agentCount = 6;

  private subscription?: Subscription;

  constructor(
    private wsService: WebSocketService,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.subscription = this.wsService.connected$.subscribe(connected => {
      this.isConnected = connected;
    });

    // Get provider info
    this.apiService.getProviders().subscribe(response => {
      this.currentProvider = response.default;
    });

    // Get agent count
    this.apiService.getAgents().subscribe(response => {
      this.agentCount = response.agents.length;
    });
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }

  reconnect(): void {
    this.wsService.connect();
  }
}
