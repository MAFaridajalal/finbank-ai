# FinBank AI - Chat Commands Reference Guide

Complete list of commands you can use for testing and demo purposes.

---

## 📊 QUERY AGENT COMMANDS

### Customer Queries
```
✅ List all customers
✅ Show me all customers
✅ Get all customer records
✅ How many customers do we have?
✅ Show customers from Downtown branch
✅ List all Premium tier customers
✅ Show all VIP customers
✅ Find customers in Westside branch
✅ List Basic tier customers
```

### Account Queries
```
✅ Show all accounts
✅ List all accounts
✅ How many accounts are there?
✅ Show accounts for customer 1
✅ List accounts belonging to John Smith
✅ Show checking accounts
✅ List savings accounts
```

### Transaction Queries
```
✅ Show all transactions
✅ List recent transactions
✅ Show transactions for account 1
✅ Get transactions for customer John Smith
✅ Show deposits
✅ List withdrawals
✅ Show transfers
```

### Specific Customer Lookups
```
✅ Show customer 1
✅ Get details for customer ID 5
✅ Find customer John Smith
✅ Show customer with email john.smith@email.com
✅ Get customer information for ID 12
```

---

## ✏️ CRUD AGENT COMMANDS

### CREATE Operations
```
✅ Add a new customer named John Doe with email john.doe@bank.com, phone 555-1234
✅ Create customer Jane Smith, email jane@bank.com, phone 555-5678, tier Premium
✅ Register new customer Robert Brown with email robert@bank.com
```

### UPDATE Operations (Use Customer ID for best results)
```
✅ Update customer 14, change email to newemail@bank.com
✅ Update customer 1, change phone to 555-9999
✅ Update customer 5, change tier to VIP
✅ Update customer 3, change branch to Airport
✅ Update customer 12, change last name to Johnson

// By name (may have issues based on orchestrator rephrasing)
⚠️ Update John Smith, change email to new@email.com
```

### DELETE Operations (Use Customer ID for best results)
```
✅ Delete customer 14
✅ Remove customer 20

// By name (may have issues)
⚠️ Delete customer John Smith
⚠️ Remove customer Jane Doe
```

---

## 📈 ANALYTICS AGENT COMMANDS

### Balance Analytics
```
✅ Calculate total balance across all accounts
✅ What's the total balance?
✅ Show average account balance
✅ Calculate average balance for Premium customers
✅ What's the total balance for VIP tier?
```

### Customer Analytics
```
✅ Show customer distribution by tier
✅ How many customers are in each tier?
✅ Show customer count by branch
✅ Analyze customer distribution
✅ Show tier breakdown
```

### Account Analytics
```
✅ Show account type distribution
✅ How many accounts of each type?
✅ Calculate total deposits
✅ Calculate total withdrawals
✅ Show transaction volume
```

### Advanced Analytics
```
✅ Show top 5 customers by balance
✅ Find customers with balance over $10,000
✅ Show accounts with low balance
✅ Calculate average transaction amount
✅ Show most active accounts
```

---

## 🔍 SEARCH AGENT COMMANDS

### Fuzzy/Partial Name Search
```
✅ Find customer John
✅ Search for customers named Smith
✅ Find anyone named Maria
✅ Search for Erik
✅ Find customers with name containing "son"
```

### Email Search
```
✅ Find customer with email john@email.com
✅ Search for email containing "@gmail.com"
✅ Find customer by email erik@gmail.com
```

### Phone Search
```
✅ Find customer with phone 555-0101
✅ Search for phone number 555-1234
```

### Combined Search
```
✅ Find John Smith in Downtown branch
✅ Search for Premium customers named John
✅ Find VIP tier customer Smith
```

---

## 💰 TRANSACTION AGENT COMMANDS

### Transaction History
```
✅ Show transaction history for account 1
✅ Get transactions for customer 1
✅ Show last 10 transactions
✅ List recent activity for account 5
```

### Transaction Analysis
```
✅ Show largest transactions
✅ Find transactions over $1000
✅ Show deposits to account 1
✅ List withdrawals from account 2
```

### Account Activity
```
✅ Show activity for John Smith's accounts
✅ Get transaction summary for customer 1
✅ Show all transfers
```

---

## ⚠️ RISK AGENT COMMANDS

### Risk Assessment
```
✅ Assess risk for customer 1
✅ Check risk score for John Smith
✅ Evaluate customer 5 risk profile
✅ Calculate risk for Premium tier customers
```

### Fraud Detection
```
✅ Check for suspicious activity on account 1
✅ Detect unusual transactions
✅ Flag high-risk customers
✅ Show accounts with risk indicators
```

### Compliance Checks
```
✅ Check compliance status for customer 1
✅ Verify KYC status for John Smith
✅ Show customers requiring verification
```

---

## 📄 EXPORT AGENT COMMANDS

### Report Generation
```
✅ Generate customer report
✅ Export customer list to CSV
✅ Create account summary report
✅ Generate transaction report
✅ Export Premium tier customers
```

### Specific Exports
```
✅ Export customer 1 details
✅ Generate report for John Smith
✅ Create transaction report for account 5
✅ Export all accounts to CSV
```

### Formatted Exports
```
✅ Create PDF report for customer 1
✅ Generate Excel spreadsheet of customers
✅ Export transaction history as CSV
```

---

## 🎯 MULTI-AGENT COMMANDS (Complex Queries)

These commands trigger multiple agents working together:

```
✅ Show me full details of all Premium tier users
   → Query Agent + Analytics Agent

✅ Find high-value customers and calculate their total balance
   → Search Agent + Query Agent + Analytics Agent

✅ Show customers with balance over $10,000 and assess their risk
   → Query Agent + Analytics Agent + Risk Agent

✅ Find John Smith and generate a full report
   → Search Agent + Query Agent + Export Agent

✅ List all VIP customers and calculate average balance
   → Query Agent + Analytics Agent

✅ Show transaction history for customer 1 and check for fraud
   → Transaction Agent + Risk Agent

✅ Find customers in Downtown branch and export to CSV
   → Query Agent + Export Agent
```

---

## 🧪 TESTING COMMANDS

### Edge Cases
```
✅ Delete customer John Smith
   → Should ask for confirmation, shows customer with accounts

✅ Find customer ERIK MOL
   → Tests case-insensitive search

✅ Update customer 999, change email to test@test.com
   → Tests non-existent customer handling

✅ Create customer without email
   → Tests validation

✅ Show customer -1
   → Tests invalid ID handling
```

### Performance Testing
```
✅ List all customers
   → Simple query, fast response

✅ Calculate total balance across all accounts with risk assessment
   → Complex multi-agent query

✅ Show top 10 customers by balance with full transaction history
   → Heavy data processing
```

---

## 💡 DEMO SCRIPT SUGGESTIONS

### Demo Flow 1: Basic Query → CRUD
```
1. "List all customers"
2. "Show customer 1 details"
3. "Update customer 1, change email to demo@bank.com"
4. "Show customer 1 details" (verify update)
```

### Demo Flow 2: Search → Analytics
```
1. "Find customers named Smith"
2. "Show all Premium tier customers"
3. "Calculate total balance for Premium customers"
4. "Show customer distribution by tier"
```

### Demo Flow 3: Complex Multi-Agent
```
1. "Show me full details of all Premium tier users"
2. "Find high-value customers and assess their risk"
3. "Generate report for top 5 customers by balance"
```

### Demo Flow 4: Banking Operations
```
1. "Show accounts for customer John Smith"
2. "Show transaction history for account 1"
3. "Calculate average transaction amount"
4. "Check for suspicious activity"
```

### Demo Flow 5: Error Handling
```
1. "Delete customer 1" (has accounts - should fail safely)
2. "Update customer 999" (doesn't exist - should handle gracefully)
3. "Create customer without required fields" (validation test)
```

---

## 🎨 FORMATTING TIPS

### For Best Results:
1. **Use customer IDs** for UPDATE/DELETE operations
2. **Be specific** with names (First + Last)
3. **Use exact tier names**: Basic, Premium, VIP
4. **Use exact branch names**: Downtown, Westside, Airport, Bellevue
5. **Include context** for better orchestrator routing

### Examples:
```
❌ "Update John" → Ambiguous
✅ "Update customer 5, change email to new@email.com"

❌ "Show gold tier" → Invalid tier
✅ "Show Premium tier customers"

❌ "Delete Smith" → Missing first name
✅ "Delete customer 12"
```

---

## 🔧 DEBUG COMMANDS

### Check System Status
```
✅ What agents are available?
✅ Show available LLM providers
✅ What can you help me with?
```

### Test Agent Routing
```
✅ This should go to the query agent: list customers
✅ Test CRUD agent: create customer
✅ Test analytics: calculate balance
```

---

## 📋 QUICK REFERENCE TABLE

| Operation | Agent | Command Example |
|-----------|-------|-----------------|
| List data | Query | `List all customers` |
| Search | Search | `Find customer John Smith` |
| Create | CRUD | `Add customer John Doe with email john@email.com` |
| Update | CRUD | `Update customer 5, change email to new@email.com` |
| Delete | CRUD | `Delete customer 14` |
| Calculate | Analytics | `Calculate total balance` |
| Report | Export | `Generate customer report` |
| Transactions | Transaction | `Show transactions for account 1` |
| Risk Check | Risk | `Assess risk for customer 1` |

---

## 🎬 READY-TO-USE DEMO SCRIPT

Copy-paste these commands in sequence for a complete demo:

```bash
# 1. Show current state
List all customers

# 2. Search functionality
Find customer John Smith

# 3. Show analytics
Calculate total balance across all accounts

# 4. Show tier distribution
Show customer distribution by tier

# 5. Create new customer
Add a new customer named Demo User with email demo@test.com, phone 555-DEMO

# 6. Update customer
Update customer 14, change email to updated@test.com

# 7. Complex query
Show me full details of all Premium tier users

# 8. Edge case - try to delete customer with accounts
Delete customer John Smith

# 9. Case-insensitive search
Find customer ERIK MOL

# 10. Generate report
Generate customer report for Premium tier
```

---

## 🏗️ ARCHITECTURE DEMONSTRATION COMMANDS

### Single Agent Execution
```
List all customers
→ Shows: Simple routing to Query Agent only
```

### Parallel Agent Execution
```
Show me full details of all Premium tier users
→ Shows: Query Agent + Analytics Agent working in parallel
```

### Sequential Agent Chain
```
Find John Smith and generate a full report
→ Shows: Search Agent → Query Agent → Export Agent (sequential)
```

### Error Recovery
```
Delete customer 1
→ Shows: CRUD Agent detects accounts, prevents deletion, safe failure
```

### Multi-Agent Collaboration
```
Calculate total balance for Premium customers and assess risk
→ Shows: Query → Analytics → Risk (complex coordination)
```

---

## 📊 AGENT ROUTING EXAMPLES

These examples show which agent(s) handle each type of request:

| Command | Primary Agent | Secondary Agents | Complexity |
|---------|---------------|------------------|------------|
| `List all customers` | Query | None | Simple |
| `Find customer John` | Search | Query | Medium |
| `Calculate total balance` | Analytics | Query | Medium |
| `Update customer 5` | CRUD | Query (validation) | Medium |
| `Show Premium users with analytics` | Query | Analytics | Complex |
| `Find high-value customers and assess risk` | Search, Query | Analytics, Risk | Complex |

---

## 🎯 TESTING CHECKLIST

Use this checklist to verify all agents are working:

- [ ] Query Agent: `List all customers`
- [ ] Search Agent: `Find customer John Smith`
- [ ] CRUD Agent (Create): `Add customer Test User with email test@test.com`
- [ ] CRUD Agent (Update): `Update customer 14, change email to new@test.com`
- [ ] CRUD Agent (Delete): `Delete customer 14`
- [ ] Analytics Agent: `Calculate total balance across all accounts`
- [ ] Transaction Agent: `Show transactions for account 1`
- [ ] Risk Agent: `Assess risk for customer 1`
- [ ] Export Agent: `Generate customer report`
- [ ] Multi-Agent: `Show Premium tier users with full details`
- [ ] Edge Case: `Delete customer 1` (should fail safely)
- [ ] Case-Insensitive: `Find customer ERIK MOL`

---

## 📝 NOTES

### Known Limitations
1. **UPDATE by name** may have issues due to orchestrator rephrasing - use customer ID instead
2. **DELETE by name** may lose last name in orchestrator - use customer ID instead
3. **Complex queries** may take 2-5 seconds due to LLM processing

### Best Practices
1. Always use customer IDs for UPDATE/DELETE operations
2. Include full names (first + last) for search operations
3. Use exact tier and branch names (case-sensitive)
4. Test with valid data first before testing edge cases
5. Check backend logs at `/tmp/backend.log` for debugging

---

**Last Updated:** 2026-01-23
**Version:** 1.0
**Tested With:** Ollama llama3.2, SQLite Database

---

For detailed testing results and architecture documentation, see:
- [TESTING_REPORT.md](TESTING_REPORT.md) - Comprehensive test results
- [README.md](README.md) - Project overview and setup
