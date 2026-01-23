import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';

import { ApiService } from '../../services/api.service';

interface LLMProvider {
  id: string;
  name: string;
  models: string[];
  description: string;
  icon: string;
}

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatIconModule,
    MatSnackBarModule,
    MatDividerModule
  ],
  template: `
    <div class="settings-container">
      <h2>Settings</h2>

      <mat-card class="settings-card">
        <mat-card-header>
          <mat-icon mat-card-avatar>psychology</mat-icon>
          <mat-card-title>LLM Provider</mat-card-title>
          <mat-card-subtitle>Configure your AI model provider</mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <div class="provider-grid">
            @for (provider of providers; track provider.id) {
              <div
                class="provider-card"
                [class.selected]="selectedProvider === provider.id"
                (click)="selectProvider(provider.id)">
                <mat-icon>{{ provider.icon }}</mat-icon>
                <span class="provider-name">{{ provider.name }}</span>
                <span class="provider-desc">{{ provider.description }}</span>
              </div>
            }
          </div>

          <mat-divider></mat-divider>

          <div class="model-selection">
            <mat-form-field appearance="outline">
              <mat-label>Model</mat-label>
              <mat-select [(ngModel)]="selectedModel">
                @for (model of getModelsForProvider(); track model) {
                  <mat-option [value]="model">{{ model }}</mat-option>
                }
              </mat-select>
            </mat-form-field>
          </div>
        </mat-card-content>

        <mat-card-actions>
          <button mat-raised-button color="primary" (click)="saveProviderSettings()">
            <mat-icon>save</mat-icon>
            Save Provider Settings
          </button>
        </mat-card-actions>
      </mat-card>

      <mat-card class="settings-card">
        <mat-card-header>
          <mat-icon mat-card-avatar>tune</mat-icon>
          <mat-card-title>Generation Settings</mat-card-title>
          <mat-card-subtitle>Fine-tune AI response generation</mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <div class="settings-form">
            <mat-form-field appearance="outline">
              <mat-label>Temperature</mat-label>
              <input matInput type="number" [(ngModel)]="temperature" min="0" max="2" step="0.1">
              <mat-hint>0 = deterministic, 2 = creative</mat-hint>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Max Tokens</mat-label>
              <input matInput type="number" [(ngModel)]="maxTokens" min="100" max="8000" step="100">
              <mat-hint>Maximum response length</mat-hint>
            </mat-form-field>
          </div>
        </mat-card-content>
      </mat-card>

      <mat-card class="settings-card">
        <mat-card-header>
          <mat-icon mat-card-avatar>smart_toy</mat-icon>
          <mat-card-title>Agent Settings</mat-card-title>
          <mat-card-subtitle>Enable or disable specific agents</mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <div class="agent-toggles">
            <div class="agent-toggle">
              <mat-slide-toggle [(ngModel)]="agents.query" color="primary">
                <mat-icon>search</mat-icon>
                Query Agent
              </mat-slide-toggle>
              <span class="agent-desc">Customer and account lookups</span>
            </div>

            <div class="agent-toggle">
              <mat-slide-toggle [(ngModel)]="agents.transaction" color="primary">
                <mat-icon>swap_horiz</mat-icon>
                Transaction Agent
              </mat-slide-toggle>
              <span class="agent-desc">Deposits, withdrawals, transfers</span>
            </div>

            <div class="agent-toggle">
              <mat-slide-toggle [(ngModel)]="agents.analytics" color="primary">
                <mat-icon>analytics</mat-icon>
                Analytics Agent
              </mat-slide-toggle>
              <span class="agent-desc">Financial reports and statistics</span>
            </div>

            <div class="agent-toggle">
              <mat-slide-toggle [(ngModel)]="agents.search" color="primary">
                <mat-icon>person_search</mat-icon>
                Search Agent
              </mat-slide-toggle>
              <span class="agent-desc">Find customers and accounts</span>
            </div>

            <div class="agent-toggle">
              <mat-slide-toggle [(ngModel)]="agents.risk" color="primary">
                <mat-icon>security</mat-icon>
                Risk Agent
              </mat-slide-toggle>
              <span class="agent-desc">Fraud detection and alerts</span>
            </div>

            <div class="agent-toggle">
              <mat-slide-toggle [(ngModel)]="agents.export" color="primary">
                <mat-icon>download</mat-icon>
                Export Agent
              </mat-slide-toggle>
              <span class="agent-desc">Statements and CSV exports</span>
            </div>
          </div>
        </mat-card-content>

        <mat-card-actions>
          <button mat-raised-button color="primary" (click)="saveAgentSettings()">
            <mat-icon>save</mat-icon>
            Save Agent Settings
          </button>
        </mat-card-actions>
      </mat-card>

      <mat-card class="settings-card">
        <mat-card-header>
          <mat-icon mat-card-avatar>info</mat-icon>
          <mat-card-title>System Information</mat-card-title>
        </mat-card-header>

        <mat-card-content>
          <div class="system-info">
            <div class="info-row">
              <span class="info-label">API Version</span>
              <span class="info-value">1.0.0</span>
            </div>
            <div class="info-row">
              <span class="info-label">Database</span>
              <span class="info-value">{{ dbStatus }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Active Agents</span>
              <span class="info-value">{{ activeAgentCount }} / 6</span>
            </div>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .settings-container {
      padding: 24px;
      max-width: 800px;
      margin: 0 auto;
    }

    h2 {
      margin-bottom: 24px;
      color: #333;
    }

    .settings-card {
      margin-bottom: 24px;

      mat-card-header {
        margin-bottom: 16px;

        mat-icon[mat-card-avatar] {
          background: #3f51b5;
          color: white;
          padding: 8px;
          border-radius: 50%;
          font-size: 24px;
          width: 40px;
          height: 40px;
        }
      }

      mat-card-actions {
        padding: 16px;
        display: flex;
        justify-content: flex-end;
      }
    }

    .provider-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .provider-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      border: 2px solid #e0e0e0;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        border-color: #3f51b5;
        background: #f5f5f5;
      }

      &.selected {
        border-color: #3f51b5;
        background: #e8eaf6;
      }

      mat-icon {
        font-size: 32px;
        width: 32px;
        height: 32px;
        margin-bottom: 8px;
        color: #3f51b5;
      }

      .provider-name {
        font-weight: 500;
        margin-bottom: 4px;
      }

      .provider-desc {
        font-size: 11px;
        color: #666;
        text-align: center;
      }
    }

    mat-divider {
      margin: 24px 0;
    }

    .model-selection {
      mat-form-field {
        width: 100%;
      }
    }

    .settings-form {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;

      mat-form-field {
        width: 100%;
      }
    }

    .agent-toggles {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .agent-toggle {
      display: flex;
      flex-direction: column;
      gap: 4px;

      mat-slide-toggle {
        mat-icon {
          margin-right: 8px;
          vertical-align: middle;
        }
      }

      .agent-desc {
        font-size: 12px;
        color: #666;
        margin-left: 44px;
      }
    }

    .system-info {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }
    }

    .info-label {
      color: #666;
    }

    .info-value {
      font-weight: 500;
    }
  `]
})
export class SettingsComponent implements OnInit {
  providers: LLMProvider[] = [
    {
      id: 'openai',
      name: 'OpenAI',
      models: ['gpt-4-turbo-preview', 'gpt-4', 'gpt-3.5-turbo'],
      description: 'GPT-4 & GPT-3.5',
      icon: 'auto_awesome'
    },
    {
      id: 'claude',
      name: 'Claude',
      models: ['claude-3-sonnet-20240229', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
      description: 'Anthropic Claude 3',
      icon: 'psychology'
    },
    {
      id: 'azure',
      name: 'Azure OpenAI',
      models: ['gpt-4', 'gpt-35-turbo'],
      description: 'Enterprise Azure',
      icon: 'cloud'
    },
    {
      id: 'ollama',
      name: 'Ollama',
      models: ['llama2', 'mistral', 'codellama'],
      description: 'Local Models',
      icon: 'computer'
    }
  ];

  selectedProvider = 'openai';
  selectedModel = 'gpt-4-turbo-preview';
  temperature = 0.7;
  maxTokens = 2000;

  agents = {
    query: true,
    transaction: true,
    analytics: true,
    search: true,
    risk: true,
    export: true
  };

  dbStatus = 'Connected';

  constructor(
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadSettings();
  }

  get activeAgentCount(): number {
    return Object.values(this.agents).filter(v => v).length;
  }

  loadSettings(): void {
    this.apiService.getProviders().subscribe({
      next: (response) => {
        if (response.default) {
          this.selectedProvider = response.default;
        }
      }
    });
  }

  selectProvider(providerId: string): void {
    this.selectedProvider = providerId;
    const provider = this.providers.find(p => p.id === providerId);
    if (provider && provider.models.length > 0) {
      this.selectedModel = provider.models[0];
    }
  }

  getModelsForProvider(): string[] {
    const provider = this.providers.find(p => p.id === this.selectedProvider);
    return provider ? provider.models : [];
  }

  saveProviderSettings(): void {
    this.apiService.updateProvider(this.selectedProvider, this.selectedModel).subscribe({
      next: () => {
        this.snackBar.open('Provider settings saved!', 'Close', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('Failed to save settings', 'Close', { duration: 3000 });
      }
    });
  }

  saveAgentSettings(): void {
    this.snackBar.open('Agent settings saved!', 'Close', { duration: 3000 });
  }
}
