import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface AgentInfo {
  name: string;
  description: string;
  icon: string;
  status: 'idle' | 'running' | 'done' | 'error';
  currentTask?: string;
  lastRun?: Date;
  runCount: number;
  successCount: number;
  errorCount: number;
  totalDuration: number;
}

export interface AgentActivity {
  id: string;
  timestamp: Date;
  agent: string;
  task: string;
  status: 'running' | 'done' | 'error';
  duration?: number;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AgentTrackerService {
  private agents: Map<string, AgentInfo> = new Map();
  private activities: AgentActivity[] = [];
  private runningTasks: Map<string, { startTime: Date; task: string }> = new Map();

  private agentsSubject = new BehaviorSubject<AgentInfo[]>([]);
  private activitiesSubject = new BehaviorSubject<AgentActivity[]>([]);

  agents$: Observable<AgentInfo[]> = this.agentsSubject.asObservable();
  activities$: Observable<AgentActivity[]> = this.activitiesSubject.asObservable();

  constructor() {
    this.initializeAgents();
  }

  private initializeAgents(): void {
    const agentConfigs = [
      { name: 'query', description: 'Database queries (SELECT)', icon: 'search' },
      { name: 'crud', description: 'Create, Update, Delete', icon: 'edit_note' },
      { name: 'transaction', description: 'Deposits, Withdrawals, Transfers', icon: 'payments' },
      { name: 'analytics', description: 'Reports & Statistics', icon: 'analytics' },
      { name: 'search', description: 'Fuzzy Search', icon: 'manage_search' },
      { name: 'risk', description: 'Fraud Detection', icon: 'warning' },
      { name: 'export', description: 'Statements & CSV', icon: 'download' },
    ];

    agentConfigs.forEach(config => {
      this.agents.set(config.name, {
        ...config,
        status: 'idle',
        runCount: 0,
        successCount: 0,
        errorCount: 0,
        totalDuration: 0,
      });
    });

    this.emitAgents();
  }

  updateAgentStatus(agentName: string, status: 'running' | 'done' | 'error', task?: string): void {
    const agent = this.agents.get(agentName);
    if (!agent) return;

    const now = new Date();

    if (status === 'running') {
      agent.status = 'running';
      agent.currentTask = task;
      this.runningTasks.set(agentName, { startTime: now, task: task || '' });

      this.addActivity({
        id: `${agentName}-${now.getTime()}`,
        timestamp: now,
        agent: agentName,
        task: task || '',
        status: 'running',
      });
    } else {
      const runningTask = this.runningTasks.get(agentName);
      const duration = runningTask ? now.getTime() - runningTask.startTime.getTime() : 0;

      agent.status = status === 'done' ? 'idle' : 'error';
      agent.lastRun = now;
      agent.runCount++;
      agent.totalDuration += duration;

      if (status === 'done') {
        agent.successCount++;
      } else {
        agent.errorCount++;
      }

      agent.currentTask = undefined;
      this.runningTasks.delete(agentName);

      // Update the activity with completion status
      const activityIndex = this.activities.findIndex(
        a => a.agent === agentName && a.status === 'running'
      );
      if (activityIndex >= 0) {
        this.activities[activityIndex] = {
          ...this.activities[activityIndex],
          status,
          duration,
          error: status === 'error' ? task : undefined,
        };
      }

      this.emitActivities();
    }

    this.emitAgents();
  }

  private addActivity(activity: AgentActivity): void {
    this.activities.unshift(activity);
    if (this.activities.length > 50) {
      this.activities = this.activities.slice(0, 50);
    }
    this.emitActivities();
  }

  private emitAgents(): void {
    this.agentsSubject.next(Array.from(this.agents.values()));
  }

  private emitActivities(): void {
    this.activitiesSubject.next([...this.activities]);
  }

  resetStats(): void {
    this.agents.forEach(agent => {
      agent.runCount = 0;
      agent.successCount = 0;
      agent.errorCount = 0;
      agent.totalDuration = 0;
      agent.status = 'idle';
      agent.currentTask = undefined;
      agent.lastRun = undefined;
    });
    this.activities = [];
    this.emitAgents();
    this.emitActivities();
  }

  getAgentStats(): { total: number; running: number; success: number; errors: number } {
    let running = 0, success = 0, errors = 0;
    this.agents.forEach(agent => {
      if (agent.status === 'running') running++;
      success += agent.successCount;
      errors += agent.errorCount;
    });
    return { total: this.agents.size, running, success, errors };
  }
}
