// WebSocket message types
export interface WsMessage {
  type: 'message' | 'ping';
  content?: string;
  provider?: string;
}

export interface WsResponse {
  type: 'status' | 'agent' | 'response' | 'error' | 'pong';
  content?: string;
  agent?: string;
  status?: 'running' | 'done' | 'error';
}

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agentsUsed?: string[];
  agentStatuses?: AgentStatus[];
}

export interface AgentStatus {
  name: string;
  status: 'running' | 'done' | 'error';
  task?: string;
  result?: string;
}

// API types
export interface Agent {
  name: string;
  description: string;
}

export interface Provider {
  name: string;
  description: string;
}

// Data types
export interface Customer {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  tier_name: string;
  branch_name: string;
  created_at: string;
}

export interface Account {
  id: number;
  account_number: string;
  customer_name: string;
  type_name: string;
  balance: number;
  status: string;
  opened_at: string;
}

export interface Transaction {
  id: number;
  transaction_id: string;
  account_number: string;
  customer_name: string;
  type: string;
  amount: number;
  description: string;
  created_at: string;
}

export interface Loan {
  id: number;
  loan_number: string;
  customer_name: string;
  type: string;
  principal: number;
  interest_rate: number;
  term_months: number;
  monthly_payment: number;
  remaining_balance: number;
  status: string;
  created_at: string;
}

// Dashboard types
export interface DashboardStats {
  total_customers: number;
  total_accounts: number;
  total_balance: number;
  deposits_this_month: number;
  active_loans: number;
  loan_balance: number;
}
