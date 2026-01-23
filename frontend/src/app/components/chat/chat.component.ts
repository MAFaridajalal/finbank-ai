import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subscription } from 'rxjs';

import { WebSocketService } from '../../services/websocket.service';
import { ChatService } from '../../services/chat.service';
import { ChatMessage, AgentStatus, WsResponse } from '../../models/types';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatChipsModule,
    MatTooltipModule,
  ],
  template: `
    <div class="chat-container">
      <div class="chat-header">
        <h2>Chat</h2>
        <button
          mat-icon-button
          (click)="clearChat()"
          matTooltip="Clear chat history"
          [disabled]="messages.length === 0">
          <mat-icon>delete_sweep</mat-icon>
        </button>
      </div>
      <div class="messages-container" #messagesContainer>
        @for (message of messages; track message.id) {
          <div class="message" [class.user]="message.role === 'user'" [class.assistant]="message.role === 'assistant'">
            <div class="message-header">
              <mat-icon>{{ message.role === 'user' ? 'person' : 'smart_toy' }}</mat-icon>
              <span class="role">{{ message.role === 'user' ? 'You' : 'FinBank AI' }}</span>
              <span class="time">{{ message.timestamp | date:'shortTime' }}</span>
            </div>

            @if (message.agentStatuses && message.agentStatuses.length > 0) {
              <div class="agent-statuses">
                @for (agent of message.agentStatuses; track agent.name) {
                  <div class="agent-status" [class]="agent.status">
                    <mat-icon>{{ getAgentIcon(agent.name) }}</mat-icon>
                    <span class="agent-name">{{ agent.name }}</span>
                    @if (agent.status === 'running') {
                      <mat-progress-bar mode="indeterminate"></mat-progress-bar>
                    }
                    @if (agent.status === 'done') {
                      <mat-icon class="status-icon">check_circle</mat-icon>
                    }
                    @if (agent.status === 'error') {
                      <mat-icon class="status-icon error">error</mat-icon>
                    }
                  </div>
                }
              </div>
            }

            <div class="message-content" [innerHTML]="formatContent(message.content)"></div>

            @if (message.agentsUsed && message.agentsUsed.length > 0) {
              <div class="agents-used">
                <mat-chip-set>
                  @for (agent of message.agentsUsed; track agent) {
                    <mat-chip>{{ agent }}</mat-chip>
                  }
                </mat-chip-set>
              </div>
            }
          </div>
        }

        @if (isProcessing) {
          <div class="message assistant processing">
            <div class="message-header">
              <mat-icon>smart_toy</mat-icon>
              <span class="role">FinBank AI</span>
            </div>
            <div class="processing-status">{{ processingStatus }}</div>
            @if (currentAgents.length > 0) {
              <div class="agent-statuses">
                @for (agent of currentAgents; track agent.name) {
                  <div class="agent-status" [class]="agent.status">
                    <mat-icon>{{ getAgentIcon(agent.name) }}</mat-icon>
                    <span class="agent-name">{{ agent.name }}</span>
                    @if (agent.status === 'running') {
                      <mat-progress-bar mode="indeterminate"></mat-progress-bar>
                    }
                    @if (agent.status === 'done') {
                      <mat-icon class="status-icon">check_circle</mat-icon>
                    }
                  </div>
                }
              </div>
            }
          </div>
        }
      </div>

      <div class="input-container">
        <mat-form-field class="message-input" appearance="outline">
          <input
            matInput
            [(ngModel)]="newMessage"
            placeholder="Ask about customers, accounts, transactions..."
            (keyup.enter)="sendMessage()"
            [disabled]="isProcessing"
          />
        </mat-form-field>
        <button
          mat-fab
          color="primary"
          (click)="sendMessage()"
          [disabled]="isProcessing || !newMessage.trim()"
        >
          <mat-icon>send</mat-icon>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .chat-container {
      display: flex;
      flex-direction: column;
      height: calc(100vh - 120px);
      max-width: 900px;
      margin: 0 auto;
    }

    .chat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px;
      border-bottom: 1px solid #e0e0e0;
      background: white;
    }

    .chat-header h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 500;
    }

    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .message {
      padding: 16px;
      border-radius: 12px;
      max-width: 85%;
    }

    .message.user {
      background: #e3f2fd;
      align-self: flex-end;
    }

    .message.assistant {
      background: white;
      align-self: flex-start;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .message-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      font-size: 12px;
      color: #666;
    }

    .message-header mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    .role {
      font-weight: 500;
    }

    .time {
      margin-left: auto;
    }

    .message-content {
      line-height: 1.6;
      white-space: pre-wrap;
    }

    .agent-statuses {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin: 12px 0;
      padding: 12px;
      background: #f5f5f5;
      border-radius: 8px;
    }

    .agent-status {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
    }

    .agent-status mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    .agent-status mat-progress-bar {
      flex: 1;
      max-width: 100px;
    }

    .agent-status .status-icon {
      color: #4caf50;
    }

    .agent-status .status-icon.error {
      color: #f44336;
    }

    .agents-used {
      margin-top: 12px;
    }

    .processing-status {
      color: #666;
      font-style: italic;
      margin-bottom: 8px;
    }

    .input-container {
      display: flex;
      gap: 16px;
      padding: 16px;
      background: white;
      border-top: 1px solid #e0e0e0;
    }

    .message-input {
      flex: 1;
    }
  `]
})
export class ChatComponent implements OnInit, OnDestroy {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;

  messages: ChatMessage[] = [];
  newMessage = '';
  isProcessing = false;
  processingStatus = '';
  currentAgents: AgentStatus[] = [];

  private subscription?: Subscription;
  private chatSubscription?: Subscription;
  private currentResponse = '';
  private currentAgentsUsed: string[] = [];

  constructor(
    private wsService: WebSocketService,
    private chatService: ChatService
  ) {}

  ngOnInit(): void {
    this.wsService.connect();

    this.subscription = this.wsService.messages$.subscribe((response: WsResponse) => {
      this.handleResponse(response);
    });

    // Subscribe to chat history from service
    this.chatSubscription = this.chatService.messages$.subscribe((messages) => {
      this.messages = messages;
      this.scrollToBottom();
    });

    // Add welcome message if history is empty
    if (this.messages.length === 0) {
      this.chatService.addAssistantMessage(
        `Hello! I'm your FinBank AI assistant. I can help you with:

• **Query data** - Find customers, accounts, transactions
• **Process transactions** - Deposits, withdrawals, transfers
• **Generate analytics** - Financial reports, statistics
• **Search** - Find records by name or account number
• **Risk analysis** - Detect suspicious transactions
• **Export** - Generate statements and CSV reports

What would you like to know?`,
        []
      );
    }
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
    this.chatSubscription?.unsubscribe();
    this.wsService.disconnect();
  }

  sendMessage(): void {
    if (!this.newMessage.trim() || this.isProcessing) return;

    // Add user message via service (persists to localStorage)
    this.chatService.addUserMessage(this.newMessage);

    // Send via WebSocket
    this.wsService.sendMessage(this.newMessage);

    // Reset state
    this.newMessage = '';
    this.isProcessing = true;
    this.processingStatus = 'Processing...';
    this.currentAgents = [];
    this.currentResponse = '';
    this.currentAgentsUsed = [];

    this.scrollToBottom();
  }

  private handleResponse(response: WsResponse): void {
    switch (response.type) {
      case 'status':
        this.processingStatus = response.content || '';
        break;

      case 'agent':
        this.updateAgentStatus(response);
        break;

      case 'response':
        this.completeMessage(response.content || '');
        break;

      case 'error':
        this.completeMessage(`Error: ${response.content}`);
        break;

      case 'pong':
        // Handle pong if needed
        break;
    }

    this.scrollToBottom();
  }

  private updateAgentStatus(response: WsResponse): void {
    const agentName = response.agent || '';
    const status = response.status || 'running';

    // Track agent used
    if (!this.currentAgentsUsed.includes(agentName)) {
      this.currentAgentsUsed.push(agentName);
    }

    // Update or add agent status
    const existingIndex = this.currentAgents.findIndex(a => a.name === agentName);
    if (existingIndex >= 0) {
      this.currentAgents[existingIndex] = {
        name: agentName,
        status: status as 'running' | 'done' | 'error',
        task: response.content,
      };
    } else {
      this.currentAgents.push({
        name: agentName,
        status: status as 'running' | 'done' | 'error',
        task: response.content,
      });
    }
  }

  private completeMessage(content: string): void {
    // Add assistant message via service (persists to localStorage)
    this.chatService.addAssistantMessage(content, [...this.currentAgentsUsed]);

    this.isProcessing = false;
    this.processingStatus = '';
    this.currentAgents = [];
    this.currentAgentsUsed = [];
  }

  getAgentIcon(agentName: string): string {
    const icons: Record<string, string> = {
      query: 'search',
      transaction: 'payment',
      analytics: 'analytics',
      search: 'manage_search',
      risk: 'warning',
      export: 'download',
    };
    return icons[agentName] || 'smart_toy';
  }

  formatContent(content: string): string {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  clearChat(): void {
    if (confirm('Are you sure you want to clear all chat history?')) {
      this.chatService.clearHistory();
    }
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      if (this.messagesContainer) {
        const el = this.messagesContainer.nativeElement;
        el.scrollTop = el.scrollHeight;
      }
    }, 100);
  }
}
