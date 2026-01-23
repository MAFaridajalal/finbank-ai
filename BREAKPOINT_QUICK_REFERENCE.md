# 🔴 Breakpoint Quick Reference

## Complete Flow: User → Response

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│                    (TypeScript/Angular)                          │
└─────────────────────────────────────────────────────────────────┘
      │
      │ 🔴 Breakpoint 1: chat.component.ts:303
      │    → this.chatService.addUserMessage(this.newMessage)
      │    ✓ Inspect: this.newMessage
      │
      │ 🔴 Breakpoint 2: chat.component.ts:306
      │    → this.wsService.sendMessage(this.newMessage)
      │    ✓ Inspect: Message being sent over WebSocket
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WEBSOCKET LAYER                               │
└─────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│                     (Python/FastAPI)                             │
└─────────────────────────────────────────────────────────────────┘
      │
      │ 🔴 Breakpoint 3: orchestrator.py:36
      │    → print(f"PLAN: {plan}")
      │    ✓ Inspect: user_message, plan
      │    ✓ Check: plan[0]['agent'] == 'crud' ✅
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CRUD AGENT                                  │
│                 (agents/crud_agent.py)                           │
└─────────────────────────────────────────────────────────────────┘
      │
      │ 🔴 Breakpoint 4: crud_agent.py:22
      │    → operation = self.detect_operation(task)
      │    ✓ Inspect: task, operation ("CREATE"/"DELETE")
      │
      ├─── IF CREATE ───────────────────────────┐
      │                                          │
      │ 🔴 Breakpoint 5a: crud_agent.py:113     │
      │    → data = json.loads(content)         │
      │    ✓ Inspect: content, data             │
      │                                          │
      │ 🔴 Breakpoint 6a: crud_agent.py:175     │
      │    → result = self.db.execute(INSERT)   │
      │    ✓ Inspect: insert_data               │
      │    ✓ Check: result.lastrowid            │
      │                                          │
      └──────────────────────────────────────────┘
      │
      ├─── IF DELETE ───────────────────────────┐
      │                                          │
      │ 🔴 Breakpoint 5b: crud_agent.py:354     │
      │    → data = json.loads(content)         │
      │    ✓ Inspect: data (ID or name?)        │
      │                                          │
      │ 🔴 Breakpoint 6b: crud_agent.py:362     │
      │    → (if name search)                   │
      │    ✓ Inspect: first_name, last_name     │
      │                                          │
      │ 🔴 Breakpoint 7b: crud_agent.py:394     │
      │    → self.db.execute(DELETE)            │
      │    ✓ Inspect: customer_id, existing     │
      │                                          │
      └──────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATABASE                                   │
│                     (SQLite)                                     │
└─────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE SYNTHESIS                            │
│                   (orchestrator.py)                              │
└─────────────────────────────────────────────────────────────────┘
      │
      │ 🔴 Breakpoint 8: orchestrator.py:64
      │    → response = await self.llm.synthesize(...)
      │    ✓ Inspect: results, response
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│                   (Response Handling)                            │
└─────────────────────────────────────────────────────────────────┘
      │
      │ 🔴 Breakpoint 9: chat.component.ts:323
      │    → this.completeMessage(response.content)
      │    ✓ Inspect: response.content
      │
      │ 🔴 Breakpoint 10: chat.component.ts:367
      │    → this.chatService.addAssistantMessage(...)
      │    ✓ Inspect: content, currentAgentsUsed
      │
      ▼
    [User sees response in chat]
```

---

## 🎯 Essential 5 Breakpoints (Minimum)

For quick debugging, set these 5:

```
1. 🔴 chat.component.ts:303      → User sends message
2. 🔴 orchestrator.py:36          → Check routing
3. 🔴 crud_agent.py:22            → Operation type
4. 🔴 crud_agent.py:113 or :354   → Data extraction
5. 🔴 crud_agent.py:175 or :394   → Database operation
```

---

## 📍 File → Line Number Map

### Frontend (TypeScript)
```
frontend/src/app/components/chat/chat.component.ts
  ├─ Line 303: Send message (user action)
  ├─ Line 306: WebSocket send
  ├─ Line 323: Handle response
  └─ Line 367: Save to localStorage

frontend/src/app/components/register/register.component.ts
  └─ Line 92: Form submit (onSubmit)

frontend/src/app/services/chat.service.ts
  ├─ Line 54: addUserMessage
  └─ Line 63: addAssistantMessage
```

### Backend (Python)
```
backend/app/orchestrator.py
  ├─ Line 36: Print plan (routing decision)
  ├─ Line 53: Get agent & execute
  └─ Line 64: Final response

backend/app/agents/crud_agent.py
  ├─ Line 22: detect_operation()
  ├─ Line 113: CREATE - Parse JSON
  ├─ Line 175: CREATE - INSERT query
  ├─ Line 354: DELETE - Parse JSON
  ├─ Line 362: DELETE - Name lookup
  └─ Line 394: DELETE - DELETE query

backend/app/llm/base.py
  └─ Line 79: Task planning (generate)
```

---

## 🔍 What to Inspect at Each Breakpoint

### 🔴 Breakpoint 1: chat.component.ts:303
```typescript
Variables to check:
  ✓ this.newMessage → "add customer Farida..."
  ✓ this.messages.length → How many messages exist
```

### 🔴 Breakpoint 2: orchestrator.py:36
```python
Variables to check:
  ✓ user_message → Full message text
  ✓ plan → [{'agent': 'crud', 'task': '...'}]
  ✓ plan[0]['agent'] → Should be 'crud' for add/delete
```

### 🔴 Breakpoint 3: crud_agent.py:22
```python
Variables to check:
  ✓ task → Task description
  ✓ operation → "CREATE", "UPDATE", or "DELETE"
```

### 🔴 Breakpoint 4: crud_agent.py:113 (CREATE)
```python
Variables to check:
  ✓ content → LLM's raw JSON response
  ✓ data → Parsed dict with customer info
  ✓ data['first_name'], data['email'] → Required fields
```

### 🔴 Breakpoint 5: crud_agent.py:175 (CREATE)
```python
Variables to check:
  ✓ insert_data → Dict with all INSERT values
  ✓ tier_id, branch_id → Mapped from names to IDs

After stepping over:
  ✓ result.lastrowid → New customer ID (should be > 0)
```

### 🔴 Breakpoint 6: crud_agent.py:354 (DELETE)
```python
Variables to check:
  ✓ content → LLM extraction result
  ✓ data → Should have 'customer_id' or 'first_name'+'last_name'
  ✓ "missing" in data → Should be False
```

### 🔴 Breakpoint 7: crud_agent.py:394 (DELETE)
```python
Variables to check:
  ✓ customer_id → ID being deleted
  ✓ existing → Tuple with (id, first_name, last_name, email)
  ✓ account_count → Should be 0 (else delete fails)

After stepping over:
  ✓ Execute in Debug Console:
    self.db.execute(text("SELECT * FROM customers WHERE id = {customer_id}")).first()
    Should return None (deleted)
```

---

## ⚡ Debug Console Commands

While paused at breakpoint, try these in Debug Console:

### Python (Backend)
```python
# Check variable types
type(data)
type(plan)

# Database queries
self.db.execute(text("SELECT COUNT(*) FROM customers")).scalar()
self.db.execute(text("SELECT * FROM customers WHERE id = 11")).first()

# Function calls
self.detect_operation("delete customer Farida")
json.loads('{"first_name": "Test"}')

# Pretty print
import json
print(json.dumps(data, indent=2))
```

### TypeScript (Frontend)
```typescript
// Check localStorage
localStorage.getItem('finbank_chat_history')

// Check service state
this.chatService.getMessages()
this.messages.length

// Check form data (in register component)
this.registerForm.value
this.registerForm.valid
```

---

## 🎯 Quick Debugging Scenarios

### Test 1: Add Customer
```
Set breakpoints: 1, 2, 3, 4, 5
Action: Fill registration form, click submit
Expected flow:
  1 → Message created
  2 → Plan shows 'crud'
  3 → Operation is 'CREATE'
  4 → Data has first_name, email
  5 → INSERT executes, lastrowid > 0
```

### Test 2: Delete Customer
```
Set breakpoints: 1, 2, 3, 6, 7
Action: Type "delete customer Farida MD"
Expected flow:
  1 → Message sent
  2 → Plan shows 'crud'
  3 → Operation is 'DELETE'
  6 → Data has first_name='Farida', last_name='MD'
  7 → customer_id found, DELETE executes
```

### Test 3: Check Routing
```
Set breakpoint: 2 only (orchestrator.py:36)
Actions to test:
  - "show all users" → plan[0]['agent'] should be 'query'
  - "add customer" → plan[0]['agent'] should be 'crud'
  - "delete user" → plan[0]['agent'] should be 'crud'
```

---

## 💡 Pro Tips

1. **Use Step Over (F10)** for most debugging
2. **Use Step Into (F11)** when you want to see function internals
3. **Use Step Out (Shift+F11)** to exit current function
4. **Watch expressions** for variables you check repeatedly
5. **Conditional breakpoints** to skip unwanted hits
6. **Logpoints** instead of print statements

---

## 🚀 Getting Started

**Right now:**

1. Stop any running servers (Ctrl+C)
2. In VS Code, press `F5`
3. Select **"Full Stack: Backend + Frontend"**
4. Set breakpoint at `orchestrator.py:36`
5. In browser, send a chat message
6. Breakpoint should hit! 🎉

**See**: [VSCODE_DEBUGGING_GUIDE.md](VSCODE_DEBUGGING_GUIDE.md) for full details.
