import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ChatMessage } from '../models/types';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private readonly STORAGE_KEY = 'finbank_chat_history';
  private messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  public messages$: Observable<ChatMessage[]> = this.messagesSubject.asObservable();

  constructor() {
    this.loadHistory();
  }

  private loadHistory(): void {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const messages = JSON.parse(stored);
        // Convert timestamp strings back to Date objects
        messages.forEach((msg: any) => {
          msg.timestamp = new Date(msg.timestamp);
        });
        this.messagesSubject.next(messages);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  }

  private saveHistory(): void {
    try {
      const messages = this.messagesSubject.value;
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(messages));
    } catch (error) {
      console.error('Failed to save chat history:', error);
    }
  }

  addMessage(message: ChatMessage): void {
    const messages = this.messagesSubject.value;
    this.messagesSubject.next([...messages, message]);
    this.saveHistory();
  }

  addUserMessage(content: string): void {
    this.addMessage({
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    });
  }

  addAssistantMessage(content: string, agents_used?: string[]): void {
    this.addMessage({
      id: Date.now().toString(),
      role: 'assistant',
      content,
      timestamp: new Date(),
      agentsUsed: agents_used
    });
  }

  clearHistory(): void {
    this.messagesSubject.next([]);
    localStorage.removeItem(this.STORAGE_KEY);
  }

  getMessages(): ChatMessage[] {
    return this.messagesSubject.value;
  }
}
