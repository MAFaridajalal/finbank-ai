# VS Code Debugging Guide - FinBank AI

## 🎯 **Complete Code Flow Debugging**

This guide shows you how to debug the **entire flow** from frontend → backend → database using VS Code breakpoints.

---

## 🚀 **Quick Start**

### **1. Stop Any Running Servers**

First, stop manually running servers:
```bash
# Stop backend (Ctrl+C in terminal)
# Stop frontend (Ctrl+C in terminal)
```

### **2. Start Debugging**

**Option A: Debug Both (Recommended)**
1. Press `F5` or click **Run and Debug** (▶️) in sidebar
2. Select **"Full Stack: Backend + Frontend"**
3. Both backend and frontend will start in debug mode
4. Browser will open automatically

**Option B: Debug Backend Only**
1. Press `F5`
2. Select **"Python: FastAPI Backend"**
3. Backend starts, set breakpoints, test with Postman/curl

**Option C: Debug Frontend Only**
1. Start backend manually: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
2. Press `F5`
3. Select **"Angular: Chrome"**
4. Frontend opens in Chrome with debugging enabled

---

## 📍 **Where to Place Breakpoints**

### **Complete Flow: Add Customer via Chat**

Here's the exact flow with breakpoint locations:

#### **1️⃣ FRONTEND: User Sends Message**

**File**: `frontend/src/app/components/chat/chat.component.ts`

**Breakpoint Line 303**: When user clicks send
```typescript
// LINE 303
this.chatService.addUserMessage(this.newMessage); // 🔴 BREAKPOINT HERE
```

**What to inspect**:
- `this.newMessage` → See what user typed
- Step into to see how message is saved to localStorage

---

**Breakpoint Line 306**: WebSocket send
```typescript
// LINE 306
this.wsService.sendMessage(this.newMessage); // 🔴 BREAKPOINT HERE
```

**What to inspect**:
- Message being sent over WebSocket
- Step into to see WebSocket communication

---

#### **2️⃣ BACKEND: WebSocket Receives Message**

**File**: `backend/app/websocket_handler.py`

Find the WebSocket message handler (check your file), add breakpoint at:
```python
async def handle_chat_websocket(websocket: WebSocket, db: Session):
    # ... connection setup ...

    while True:
        data = await websocket.receive_text()  # 🔴 BREAKPOINT HERE
        # See the incoming message from frontend
```

---

#### **3️⃣ BACKEND: Orchestrator Routes Message**

**File**: `backend/app/orchestrator.py`

**Breakpoint Line 35**: See the plan
```python
# LINE 35
print(f"USER MESSAGE: {user_message}")  # Already has print
print(f"PLAN: {plan}")  # 🔴 BREAKPOINT HERE
```

**What to inspect**:
- `user_message` → User's request
- `plan` → Which agents will be used
- Look for `{'agent': 'crud', 'task': '...'}`

---

**Breakpoint Line 53**: Before executing agent
```python
# LINE 53
agent = get_agent(agent_name, self.db, self.llm)  # 🔴 BREAKPOINT HERE
result = await agent.execute(task_desc)
```

**What to inspect**:
- `agent_name` → Should be "crud" for add/delete operations
- `task_desc` → The specific task
- Step into `execute()` to follow agent logic

---

#### **4️⃣ BACKEND: CRUD Agent Processes Request**

**File**: `backend/app/agents/crud_agent.py`

**Breakpoint Line 22**: Operation detection
```python
# LINE 22
operation = self.detect_operation(task)
print(f"CRUD AGENT: Detected operation: {operation}")  # 🔴 BREAKPOINT HERE
```

**What to inspect**:
- `task` → The task description
- `operation` → "CREATE", "UPDATE", or "DELETE"

---

**For CREATE operations, Breakpoint Line 113**:
```python
# LINE 113
data = json.loads(content)
print(f"CRUD AGENT: Parsed data: {data}")  # 🔴 BREAKPOINT HERE
```

**What to inspect**:
- `content` → LLM's raw JSON response
- `data` → Parsed customer information
- Check if all required fields present

---

**Breakpoint Line 175**: Before database insert
```python
# LINE 175
print(f"CRUD AGENT: Inserting customer with data: {insert_data}")  # 🔴 BREAKPOINT HERE
result = self.db.execute(text("""
    INSERT INTO customers ...
```

**What to inspect**:
- `insert_data` → Exact data being inserted
- Step over to see if INSERT succeeds
- Check `result.lastrowid` for new customer ID

---

**For DELETE operations, Breakpoint Line 354**:
```python
# LINE 354
data = json.loads(content)
print(f"CRUD AGENT DELETE: Parsed data: {data}")  # 🔴 BREAKPOINT HERE
```

**What to inspect**:
- `data` → Should have `customer_id` or `first_name`/`last_name`
- Step through name lookup logic if no ID

---

**Breakpoint Line 394**: Before DELETE execution
```python
# LINE 394
self.db.execute(text("DELETE FROM customers WHERE id = :id"), {"id": customer_id})  # 🔴 BREAKPOINT HERE
self.db.commit()
```

**What to inspect**:
- `customer_id` → ID being deleted
- `existing` → Customer data before deletion
- Step over to verify deletion

---

#### **5️⃣ BACKEND: Response Sent Back**

**File**: `backend/app/orchestrator.py`

**Breakpoint Line 64**: Final response
```python
# LINE 64
response = await self.llm.synthesize(user_message, results)
yield f"[RESPONSE]{response}"  # 🔴 BREAKPOINT HERE
```

**What to inspect**:
- `results` → All agent results
- `response` → Final message sent to user

---

#### **6️⃣ FRONTEND: Response Received**

**File**: `frontend/src/app/components/chat/chat.component.ts`

**Breakpoint Line 323**: Response handling
```typescript
// LINE 323 (in handleResponse method)
case 'response':
  this.completeMessage(response.content || '');  // 🔴 BREAKPOINT HERE
  break;
```

**What to inspect**:
- `response.content` → AI's response
- Step into to see message being saved

---

**Breakpoint Line 367**: Message persistence
```typescript
// LINE 367
this.chatService.addAssistantMessage(content, [...this.currentAgentsUsed]);  // 🔴 BREAKPOINT HERE
```

**What to inspect**:
- `content` → Message content
- `this.currentAgentsUsed` → Which agents were used
- Step into to see localStorage save

---

## 🔍 **Debugging Scenarios**

### **Scenario 1: Debug "Add Customer via Registration Form"**

**Breakpoints to set**:
1. `frontend/src/app/components/register/register.component.ts:92` → Form submit
2. `backend/app/orchestrator.py:36` → Check routing to CRUD agent
3. `backend/app/agents/crud_agent.py:113` → Check parsed data
4. `backend/app/agents/crud_agent.py:175` → Before INSERT

**Test**:
1. Fill registration form
2. Click "Create Customer"
3. Hit breakpoint 1 → Inspect `formData`
4. Hit breakpoint 2 → Verify `plan[0]['agent'] === 'crud'`
5. Hit breakpoint 3 → Check extracted customer info
6. Hit breakpoint 4 → See INSERT data

---

### **Scenario 2: Debug "Delete Customer by Name"**

**Breakpoints to set**:
1. `frontend/src/app/components/chat/chat.component.ts:303` → Message send
2. `backend/app/orchestrator.py:36` → Check plan
3. `backend/app/agents/crud_agent.py:354` → Check parsed delete data
4. `backend/app/agents/crud_agent.py:362` → Name lookup (if no ID)
5. `backend/app/agents/crud_agent.py:394` → Before DELETE

**Test**:
1. Type in chat: "delete customer Farida MD"
2. Hit breakpoint 1 → See message
3. Hit breakpoint 2 → Verify CRUD agent selected
4. Hit breakpoint 3 → Check if name was extracted
5. Hit breakpoint 4 → See customer lookup by name
6. Hit breakpoint 5 → Verify correct customer_id

---

### **Scenario 3: Debug "List All Users"**

**Breakpoints to set**:
1. `backend/app/orchestrator.py:36` → Check agent routing
2. `backend/app/agents/query_agent.py` → (find the execute method)

**Expected**:
- Plan should show `{'agent': 'query', ...}`
- NOT `{'agent': 'crud', ...}`

---

## 🛠️ **VS Code Debugging Features**

### **Debug Console**

While paused at a breakpoint, use the Debug Console (bottom panel):

**Python (Backend)**:
```python
# Inspect variables
print(user_message)
print(plan)
print(type(data))

# Check database state
self.db.execute(text("SELECT COUNT(*) FROM customers")).scalar()

# Call functions
self.detect_operation("delete customer")
```

**TypeScript (Frontend)**:
```typescript
// In Debug Console
this.messages.length
this.chatService.getMessages()
localStorage.getItem('finbank_chat_history')
```

---

### **Call Stack**

Click on the **Call Stack** panel to see:
- Where you are in the code
- How you got there
- Navigate up/down the stack

Example stack trace for CREATE:
```
chat.component.ts:303 - sendMessage()
  ↓
websocket_handler.py:45 - handle_chat_websocket()
  ↓
orchestrator.py:53 - process()
  ↓
crud_agent.py:22 - execute()
  ↓
crud_agent.py:79 - create_customer()
  ↓
crud_agent.py:175 - (database INSERT)
```

---

### **Variables Panel**

See all variables in current scope:
- **Locals** → Current function variables
- **Globals** → Module-level variables
- **Closure** → Variables from outer scopes

---

### **Watch Expressions**

Add expressions to watch continuously:
1. Click **+** in Watch panel
2. Add expressions like:
   - `plan[0]['agent']` (backend)
   - `this.messages.length` (frontend)
   - `customer_id`

---

## ⌨️ **Keyboard Shortcuts**

| Action | Shortcut |
|--------|----------|
| Start Debugging | `F5` |
| Stop Debugging | `Shift+F5` |
| Step Over | `F10` |
| Step Into | `F11` |
| Step Out | `Shift+F11` |
| Continue | `F5` |
| Toggle Breakpoint | `F9` |
| Conditional Breakpoint | Right-click line number |

---

## 🎨 **Conditional Breakpoints**

**When to use**: Only break when specific conditions are met

**Example 1**: Only break for "Farida"
```python
# Right-click line number → Add Conditional Breakpoint
# Condition: data.get('first_name') == 'Farida'
```

**Example 2**: Only break for DELETE operations
```python
# Condition: operation == 'DELETE'
```

**Example 3**: Only break for errors
```python
# Condition: 'error' in result
```

---

## 📊 **Logpoints** (Alternative to print statements)

Don't want to modify code? Use logpoints!

**How to add**:
1. Right-click line number
2. Select **Add Logpoint**
3. Enter message: `User message: {user_message}, Plan: {plan}`

**Benefits**:
- No code changes needed
- Logs appear in Debug Console
- Easy to toggle on/off

---

## 🐛 **Common Debugging Scenarios**

### **Problem: CRUD agent not being called**

**Debug steps**:
1. Set breakpoint at `orchestrator.py:36`
2. Send message: "add customer Test"
3. Inspect `plan` variable
4. If `plan[0]['agent'] != 'crud'`:
   - Check `backend/app/llm/base.py:60-65` (routing rules)
   - Verify CRUD agent is in available agents list

---

### **Problem: Customer not saved to database**

**Debug steps**:
1. Set breakpoint at `crud_agent.py:175` (before INSERT)
2. Check `insert_data` has all required fields
3. Step over INSERT line (`F10`)
4. Check `result.lastrowid` (should be > 0)
5. Step over `self.db.commit()` (`F10`)
6. In Debug Console: `self.db.execute(text("SELECT * FROM customers WHERE id = {result.lastrowid}")).first()`

---

### **Problem: DELETE not working**

**Debug steps**:
1. Set breakpoint at `crud_agent.py:354`
2. Inspect `data` → Check if name or ID extracted
3. If name search (line 362), check:
   - `first_name` and `last_name` variables
   - Step through SQL query
   - Verify `existing` is not None
4. Set breakpoint at line 394 (DELETE)
5. Verify `customer_id` is correct
6. In Debug Console: `self.db.execute(text("SELECT * FROM customers WHERE id = {customer_id}")).first()` before DELETE

---

## 🔥 **Advanced: Multi-threaded Debugging**

When debugging both frontend and backend simultaneously:

1. Set breakpoints in both
2. Send a message from frontend
3. Execution will pause at frontend breakpoint first
4. Press `F5` to continue
5. Execution pauses at backend breakpoint
6. Switch between them using the **Call Stack** dropdown

---

## 📝 **Debugging Checklist**

Before starting a debug session:

- [ ] `.vscode/launch.json` exists
- [ ] No servers running manually
- [ ] Breakpoints set in key locations
- [ ] Watch expressions added (optional)
- [ ] Debug Console open
- [ ] Variables panel visible

---

## 🎯 **Recommended Breakpoint Set**

For complete flow understanding, set these **5 essential breakpoints**:

1. **Frontend send**: `chat.component.ts:303`
2. **Backend routing**: `orchestrator.py:36`
3. **CRUD detection**: `crud_agent.py:22`
4. **Data extraction**: `crud_agent.py:113` (CREATE) or `crud_agent.py:354` (DELETE)
5. **Database operation**: `crud_agent.py:175` (INSERT) or `crud_agent.py:394` (DELETE)

---

## 🚨 **Troubleshooting**

### **Breakpoints show gray dot (not red)**
- File not loaded yet
- Start debugging first, then breakpoints turn red
- Or: sourcemaps issue (frontend) → check `angular.json` has `"sourceMap": true`

### **"Module not found" error (Python)**
- Check `"cwd"` in launch.json points to `backend` folder
- Verify `PYTHONPATH` includes backend folder

### **Frontend breakpoints not working**
- Ensure `"sourceMap": true` in `angular.json`
- Use Chrome DevTools as fallback
- Check `webRoot` path in launch.json

### **Variables show as "optimized out"**
- Backend: set `justMyCode: false` in launch.json
- Frontend: build in development mode (default for `ng serve`)

---

## 📚 **Learn More**

**VS Code Docs**:
- [Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [JavaScript Debugging](https://code.visualstudio.com/docs/nodejs/angular-tutorial)

**Your Config File**:
- `.vscode/launch.json` → All debug configurations

---

## ✅ **Quick Test**

**Test the setup**:

1. **Stop all running servers**
2. Press `F5` → Select **"Full Stack: Backend + Frontend"**
3. Set breakpoint at `backend/app/orchestrator.py:36`
4. In browser (auto-opens), go to Chat
5. Type: "show all users"
6. Send
7. ✅ **Breakpoint should hit!** → You should see user_message and plan
8. Press `F5` to continue
9. Response should appear in chat

**If breakpoint hits**: 🎉 You're ready to debug!
**If not**: Check troubleshooting section above

---

## 🎓 **Next Steps**

1. **Start with "Add Customer" flow** (simplest)
2. **Then "Delete Customer" flow** (slightly complex)
3. **Finally "Update Customer" flow** (most complex)

Each time, step through the **entire flow** from frontend → backend → database → response → frontend to understand the system completely.

Happy debugging! 🐛🔍
