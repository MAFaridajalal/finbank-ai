import { Injectable } from '@angular/core';
import { Subject, Observable, BehaviorSubject } from 'rxjs';
import { WsMessage, WsResponse } from '../models/types';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private messagesSubject = new Subject<WsResponse>();
  private connectionStatus = new BehaviorSubject<boolean>(false);

  private wsUrl = 'ws://localhost:8000/ws/chat';
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  messages$: Observable<WsResponse> = this.messagesSubject.asObservable();
  connected$: Observable<boolean> = this.connectionStatus.asObservable();

  connect(): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.socket = new WebSocket(this.wsUrl);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.connectionStatus.next(true);
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      try {
        const data: WsResponse = JSON.parse(event.data);
        this.messagesSubject.next(data);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.connectionStatus.next(false);
      this.attemptReconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
    }
  }

  send(message: WsMessage): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
      this.connect();
    }
  }

  sendMessage(content: string, provider?: string): void {
    this.send({
      type: 'message',
      content,
      provider
    });
  }

  ping(): void {
    this.send({ type: 'ping' });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
