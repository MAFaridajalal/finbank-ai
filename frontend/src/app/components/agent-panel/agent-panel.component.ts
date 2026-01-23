import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subscription } from 'rxjs';

import { AgentTrackerService, AgentInfo, AgentActivity } from '../../services/agent-tracker.service';

@Component({
  selector: 'app-agent-panel',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressBarModule,
    MatChipsModule,
    MatTooltipModule,
  ],
  template: `
    <div class="agent-panel-container">
      <div class="panel-header">
        <h2>AI Agents</h2>
        <div class="stats-summary">
          <span class="stat">
            <mat-icon>hub</mat-icon>
            {{ stats.total }} agents
          </span>
          <span class="stat running" *ngIf="stats.running > 0">
            <mat-icon>sync</mat-icon>
            {{ stats.running }} running
          </span>
          <span class="stat success">
            <mat-icon>check_circle</mat-icon>
            {{ stats.success }}
          </span>
          <span class="stat error" *ngIf="stats.errors > 0">
            <mat-icon>error</mat-icon>
            {{ stats.errors }}
          </span>
          <button mat-icon-button (click)="resetStats()" matTooltip="Reset stats">
            <mat-icon>refresh</mat-icon>
          </button>
        </div>
      </div>

      <div class="agents-grid">
        @for (agent of agents; track agent.name) {
          <div class="agent-card" [class]="'status-' + agent.status">
            <div class="agent-header">
              <mat-icon class="agent-icon">{{ agent.icon }}</mat-icon>
              <div class="agent-info">
                <span class="agent-name">{{ agent.name }}</span>
                <span class="agent-desc">{{ agent.description }}</span>
              </div>
              <div class="status-indicator" [class]="agent.status">
                @if (agent.status === 'running') {
                  <mat-icon class="spinning">sync</mat-icon>
                } @else if (agent.status === 'error') {
                  <mat-icon>error</mat-icon>
                } @else {
                  <mat-icon>check_circle</mat-icon>
                }
              </div>
            </div>

            @if (agent.status === 'running') {
              <mat-progress-bar mode="indeterminate" class="running-bar"></mat-progress-bar>
              <div class="current-task">{{ agent.currentTask }}</div>
            }

            <div class="agent-stats">
              <span matTooltip="Total runs">
                <mat-icon>play_arrow</mat-icon>
                {{ agent.runCount }}
              </span>
              <span matTooltip="Successful" class="success">
                <mat-icon>check</mat-icon>
                {{ agent.successCount }}
              </span>
              <span matTooltip="Errors" class="error" *ngIf="agent.errorCount > 0">
                <mat-icon>close</mat-icon>
                {{ agent.errorCount }}
              </span>
              <span matTooltip="Avg duration" *ngIf="agent.runCount > 0">
                <mat-icon>timer</mat-icon>
                {{ getAvgDuration(agent) }}ms
              </span>
            </div>

            @if (agent.lastRun) {
              <div class="last-run">
                Last: {{ agent.lastRun | date:'shortTime' }}
              </div>
            }
          </div>
        }
      </div>

      <div class="activity-section">
        <h3>Activity Timeline</h3>
        <div class="activity-list">
          @for (activity of activities; track activity.id) {
            <div class="activity-item" [class]="activity.status">
              <span class="activity-time">{{ activity.timestamp | date:'HH:mm:ss' }}</span>
              <mat-icon class="activity-status">
                @if (activity.status === 'running') {
                  sync
                } @else if (activity.status === 'done') {
                  check_circle
                } @else {
                  error
                }
              </mat-icon>
              <span class="activity-agent">{{ activity.agent }}</span>
              <span class="activity-task">{{ activity.task | slice:0:50 }}{{ activity.task.length > 50 ? '...' : '' }}</span>
              @if (activity.duration) {
                <span class="activity-duration">{{ activity.duration }}ms</span>
              }
            </div>
          } @empty {
            <div class="no-activity">No activity yet. Send a message in Chat to see agents in action.</div>
          }
        </div>
      </div>
    </div>
  `,
  styles: [`
    .agent-panel-container {
      padding: 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .panel-header h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 500;
    }

    .stats-summary {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .stat {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 14px;
      color: #666;
    }

    .stat mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    .stat.running { color: #1976d2; }
    .stat.success { color: #388e3c; }
    .stat.error { color: #d32f2f; }

    .agents-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }

    .agent-card {
      background: white;
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      transition: all 0.3s ease;
    }

    .agent-card.status-running {
      border-left: 4px solid #1976d2;
      box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
    }

    .agent-card.status-error {
      border-left: 4px solid #d32f2f;
    }

    .agent-card.status-idle {
      border-left: 4px solid #e0e0e0;
    }

    .agent-header {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;
    }

    .agent-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
      color: #1976d2;
    }

    .agent-info {
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    .agent-name {
      font-size: 16px;
      font-weight: 500;
      text-transform: capitalize;
    }

    .agent-desc {
      font-size: 12px;
      color: #666;
    }

    .status-indicator mat-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .status-indicator.running mat-icon {
      color: #1976d2;
    }

    .status-indicator.idle mat-icon {
      color: #9e9e9e;
    }

    .status-indicator.error mat-icon {
      color: #d32f2f;
    }

    .spinning {
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    .running-bar {
      margin: 8px 0;
    }

    .current-task {
      font-size: 12px;
      color: #1976d2;
      font-style: italic;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 8px;
    }

    .agent-stats {
      display: flex;
      gap: 12px;
      font-size: 12px;
      color: #666;
      margin-top: 8px;
    }

    .agent-stats span {
      display: flex;
      align-items: center;
      gap: 2px;
    }

    .agent-stats mat-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
    }

    .agent-stats .success { color: #388e3c; }
    .agent-stats .error { color: #d32f2f; }

    .last-run {
      font-size: 11px;
      color: #999;
      margin-top: 8px;
    }

    .activity-section h3 {
      font-size: 18px;
      font-weight: 500;
      margin-bottom: 16px;
    }

    .activity-list {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      max-height: 300px;
      overflow-y: auto;
    }

    .activity-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      border-bottom: 1px solid #f0f0f0;
      font-size: 13px;
    }

    .activity-item:last-child {
      border-bottom: none;
    }

    .activity-item.running {
      background: #e3f2fd;
    }

    .activity-item.error {
      background: #ffebee;
    }

    .activity-time {
      color: #999;
      font-family: monospace;
      min-width: 70px;
    }

    .activity-status mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    .activity-item.running .activity-status mat-icon { color: #1976d2; }
    .activity-item.done .activity-status mat-icon { color: #388e3c; }
    .activity-item.error .activity-status mat-icon { color: #d32f2f; }

    .activity-agent {
      font-weight: 500;
      text-transform: capitalize;
      min-width: 80px;
    }

    .activity-task {
      flex: 1;
      color: #666;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .activity-duration {
      color: #999;
      font-family: monospace;
      min-width: 60px;
      text-align: right;
    }

    .no-activity {
      padding: 32px;
      text-align: center;
      color: #999;
    }
  `]
})
export class AgentPanelComponent implements OnInit, OnDestroy {
  agents: AgentInfo[] = [];
  activities: AgentActivity[] = [];
  stats = { total: 0, running: 0, success: 0, errors: 0 };

  private agentsSub?: Subscription;
  private activitiesSub?: Subscription;

  constructor(private tracker: AgentTrackerService) {}

  ngOnInit(): void {
    this.agentsSub = this.tracker.agents$.subscribe(agents => {
      this.agents = agents;
      this.stats = this.tracker.getAgentStats();
    });

    this.activitiesSub = this.tracker.activities$.subscribe(activities => {
      this.activities = activities;
    });
  }

  ngOnDestroy(): void {
    this.agentsSub?.unsubscribe();
    this.activitiesSub?.unsubscribe();
  }

  getAvgDuration(agent: AgentInfo): number {
    if (agent.runCount === 0) return 0;
    return Math.round(agent.totalDuration / agent.runCount);
  }

  resetStats(): void {
    this.tracker.resetStats();
  }
}
