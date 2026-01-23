# FinBank AI - Complete Debugging Guide

## 🐛 **BUG FIXED**

**Root Cause Found**: The orchestrator's task planner was NOT including the `crud` agent in available agents list.

**Files Fixed**:
1. ✅ [backend/app/llm/base.py:48-85](backend/app/llm/base.py#L48-L85) - Added `crud` agent to available agents
2. ✅ [backend/app/orchestrator.py:22-35](backend/app/orchestrator.py#L22-L35) - Added debug logging
3. ✅ [backend/app/agents/crud_agent.py:16-24](backend/app/agents/crud_agent.py#L16-L24) - Added debug logging

---

## 🚀 **START THE SERVERS**

### **Terminal 1: Backend with Logs**
```bash
cd /Users/farida/finbank-ai/backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Terminal 2: Frontend**
```bash
cd /Users/farida/finbank-ai/frontend
npm start
```

**Access:**
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000/docs

---

## 🔍 **DATABASE ACCESS**

Your database: `/Users/farida/finbank-ai/finbank.db`

### **Method 1: Command Line (Quick)**

```bash
cd /Users/farida/finbank-ai

# Connect
sqlite3 finbank.db

# List all customers
SELECT id, first_name, last_name, email FROM customers;

# Check specific email
SELECT * FROM customers WHERE email LIKE '%farida%';

# Count customers
SELECT COUNT(*) FROM customers;

# View with tier names
SELECT c.id, c.first_name, c.last_name, c.email, ct.name as tier
FROM customers c
LEFT JOIN customer_tiers ct ON c.tier_id = ct.id;

# Exit
.quit
```

### **Method 2: GUI (Recommended)**

```bash
# Install DB Browser for SQLite
brew install --cask db-browser-for-sqlite

# Open database
open -a "DB Browser for SQLite" /Users/farida/finbank-ai/finbank.db
```

**In DB Browser:**
- Click "Browse Data" tab
- Select "customers" table
- See all records in real-time
- Can edit, add, delete manually for testing

---

## 📋 **READING BACKEND LOGS**

### **Real-Time Logs in Terminal**

When you run the backend with `--reload`, all logs appear in Terminal 1.

You'll now see **DEBUG OUTPUT** like this:

```
============================================================
USER MESSAGE: Add a new customer named Farida Md with email farida@test.com
PLAN: [{'agent': 'crud', 'task': 'Create a new customer named Farida Md with email farida@test.com'}]
============================================================

============================================================
CRUD AGENT EXECUTE: Received task: Create a new customer named Farida Md with email farida@test.com
CRUD AGENT: Detected operation: CREATE
============================================================

CRUD AGENT: LLM extraction response: {
  "first_name": "Farida",
  "last_name": "Md",
  "email": "farida@test.com",
  ...
}

CRUD AGENT: Parsed data: {'first_name': 'Farida', 'last_name': 'Md', ...}

CRUD AGENT: Inserting customer with data: {'first_name': 'Farida', 'last_name': 'Md', ...}

CRUD AGENT: Customer inserted successfully, ID: 11
```

### **Save Logs to File**

```bash
# Run with log file
cd /Users/farida/finbank-ai/backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee backend.log
```

**In another terminal:**
```bash
# Watch logs live
tail -f backend.log

# Search for errors
grep -i "error" backend.log

# Search for CRUD operations
grep "CRUD AGENT" backend.log

# See all agent routing
grep "PLAN:" backend.log
```

---

## 🧪 **TESTING WORKFLOW**

### **Test 1: Add Customer via Registration Form** (3 min)

1. **Open App**: http://localhost:4200
2. **Click**: "Register Customer" in sidebar
3. **Fill Form**:
   ```
   First Name: Farida
   Last Name: Md
   Email: farida@test.com
   Phone: 3471984011
   Address: 101 Crossing
   City: NYC
   Tier: Premium
   Branch: Downtown
   ```
4. **Click**: "Create Customer"

**Expected Backend Logs**:
```
============================================================
PLAN: [{'agent': 'crud', 'task': 'Create a new customer named Farida...'}]
============================================================
CRUD AGENT: Detected operation: CREATE
CRUD AGENT: Inserting customer with data: {...}
CRUD AGENT: Customer inserted successfully, ID: 11
```

**Expected Frontend**:
- ✅ Success notification appears
- ✅ Auto-redirect to Data Browser
- ✅ New customer appears in list

**Verify in Database**:
```bash
sqlite3 finbank.db "SELECT * FROM customers WHERE email='farida@test.com'"
```

---

### **Test 2: Add Customer via Chat** (2 min)

1. **Go to Chat Tab**
2. **Type**: "Add a new customer named Test User with email test@example.com tier Basic branch Downtown"
3. **Press Enter**

**Expected Backend Logs**:
```
USER MESSAGE: Add a new customer named Test User...
PLAN: [{'agent': 'crud', 'task': '...'}]
CRUD AGENT: Detected operation: CREATE
CRUD AGENT: Customer inserted successfully, ID: 12
```

**Expected Chat Response**:
```
Successfully created customer: Test User (ID: 12)
Email: test@example.com
Tier: Basic
Branch: Downtown
```

---

### **Test 3: Update Customer** (2 min)

1. **Check customer ID**: `sqlite3 finbank.db "SELECT id, first_name FROM customers WHERE email='test@example.com'"`
   - Note the ID (e.g., 12)

2. **In Chat**: "Update customer 12 set tier to VIP"

**Expected Backend Logs**:
```
PLAN: [{'agent': 'crud', 'task': 'Update customer 12 set tier to VIP'}]
CRUD AGENT: Detected operation: UPDATE
```

**Expected Response**:
```
Successfully updated customer Test User
Updated fields: tier
```

**Verify**:
```bash
sqlite3 finbank.db "SELECT c.first_name, ct.name FROM customers c JOIN customer_tiers ct ON c.tier_id = ct.id WHERE c.id = 12"
# Should show: Test User|VIP
```

---

### **Test 4: Delete Customer** (2 min)

1. **In Chat**: "Delete customer 12"

**Expected Backend Logs**:
```
PLAN: [{'agent': 'crud', 'task': 'Delete customer 12'}]
CRUD AGENT: Detected operation: DELETE
```

**Expected Response**:
```
Successfully deleted customer: Test User
```

**Verify**:
```bash
sqlite3 finbank.db "SELECT COUNT(*) FROM customers WHERE id = 12"
# Should return: 0
```

---

## 🐞 **COMMON ISSUES & FIXES**

### **Issue 1: Agent not routing to CRUD**

**Symptom**: Chat shows "query" or "search" agent instead of "crud"

**Check logs for**:
```
PLAN: [{'agent': 'query', ...}]  # WRONG - should be 'crud'
```

**Fix**: Verify [backend/app/llm/base.py:48](backend/app/llm/base.py#L48) includes `crud` agent

---

### **Issue 2: Customer not added to database**

**Symptom**: Success message but no record in database

**Debug steps**:
1. Check backend logs for:
   ```
   CRUD AGENT: Customer inserted successfully, ID: X
   ```

2. Check database:
   ```bash
   sqlite3 finbank.db "SELECT COUNT(*) FROM customers"
   ```

3. Check for errors:
   ```bash
   grep -i "error" backend_terminal_output
   ```

**Common causes**:
- ❌ Missing required fields (first_name, last_name, email)
- ❌ Email already exists
- ❌ Database not committed (check `self.db.commit()` is called)

---

### **Issue 3: Registration form shows weird popup**

**Symptom**: Popup shows "query failed" or "no column named 'name'"

**Root cause**: Orchestrator routing to wrong agent

**Check**: Backend logs should show:
```
PLAN: [{'agent': 'crud', ...}]  # CORRECT
```

**If it shows**:
```
PLAN: [{'agent': 'query', ...}]  # WRONG
```

**Fix**: Restart backend after updating [backend/app/llm/base.py](backend/app/llm/base.py)

---

### **Issue 4: DELETE not working**

**Symptom**: Error or "Expecting value: line 1 column 1"

**Check logs for**:
```
CRUD AGENT: Detected operation: DELETE
```

**Common causes**:
- ❌ Customer has active accounts (safety check prevents deletion)
- ❌ JSON parsing error in response

**Test with customer that has no accounts**:
```bash
# Check if customer has accounts
sqlite3 finbank.db "SELECT COUNT(*) FROM accounts WHERE customer_id = X"
```

---

## 📊 **DEBUG CHECKLIST**

Before reporting an issue, check:

- [ ] Backend is running (`ps aux | grep uvicorn`)
- [ ] Frontend is running (`ps aux | grep ng`)
- [ ] Check backend logs for errors
- [ ] Check database file exists: `ls -lh /Users/farida/finbank-ai/finbank.db`
- [ ] Check database has tables: `sqlite3 finbank.db ".tables"`
- [ ] Check PLAN routing: `grep "PLAN:" backend_logs`
- [ ] Check customer count: `sqlite3 finbank.db "SELECT COUNT(*) FROM customers"`

---

## 🔧 **ADVANCED DEBUGGING**

### **Enable SQL Query Logging**

Edit `/Users/farida/finbank-ai/backend/app/database.py`:

```python
engine = create_engine(
    settings.database_url,
    echo=True,  # ADD THIS - shows all SQL queries
    connect_args={"check_same_thread": False}
)
```

Restart backend → see all SQL queries in logs

---

### **Test with Python REPL**

```bash
cd /Users/farida/finbank-ai/backend
source venv/bin/activate
python
```

```python
from app.database import get_db
from sqlalchemy import text

# Get database session
db = next(get_db())

# Check customers
result = db.execute(text("SELECT * FROM customers")).fetchall()
print(f"Total customers: {len(result)}")
for row in result:
    print(dict(row))

# Insert test customer
db.execute(text("""
    INSERT INTO customers (first_name, last_name, email, tier_id, branch_id)
    VALUES ('Test', 'User', 'test@test.com', 1, 1)
"""))
db.commit()

# Verify
result = db.execute(text("SELECT * FROM customers WHERE email='test@test.com'")).first()
print(dict(result))
```

---

## 📝 **WHAT TO EXPECT AFTER FIX**

### **Before (Broken)**
```
User: "Add customer Farida..."
PLAN: [{'agent': 'search', 'task': '...'}, {'agent': 'query', 'task': '...'}]
Response: "Database Error: no column named 'name'"
Database: No new customer
```

### **After (Fixed)**
```
User: "Add customer Farida..."
PLAN: [{'agent': 'crud', 'task': 'Create a new customer named Farida...'}]
CRUD AGENT: Detected operation: CREATE
CRUD AGENT: Customer inserted successfully, ID: 11
Response: "Successfully created customer: Farida Md (ID: 11)"
Database: ✅ Customer added
Data Browser: ✅ Shows new customer
```

---

## 🎯 **QUICK TESTS**

After starting servers, run these quick tests:

```bash
# 1. Check backend is up
curl http://localhost:8000/health

# 2. Check database
sqlite3 /Users/farida/finbank-ai/finbank.db "SELECT COUNT(*) FROM customers"

# 3. Test via API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "list all customers"}'

# 4. Test CRUD via API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add customer Test with email test@test.com tier Basic branch Downtown"}'
```

---

## ✅ **SUCCESS INDICATORS**

You know it's working when:

1. **Backend logs show**:
   ```
   PLAN: [{'agent': 'crud', ...}]  ✅
   CRUD AGENT: Customer inserted successfully  ✅
   ```

2. **Database has record**:
   ```bash
   sqlite3 finbank.db "SELECT * FROM customers WHERE email='your-test-email'"
   # Returns a row ✅
   ```

3. **Data Browser updates immediately** after adding customer ✅

4. **Chat shows success message** with customer ID ✅

---

## 🆘 **STILL NOT WORKING?**

If after following this guide it still doesn't work:

1. **Restart both servers** (Ctrl+C, then start again)
2. **Clear browser cache** (Shift+Cmd+R on Mac)
3. **Check logs** for exact error message
4. **Test database directly** with sqlite3 commands
5. **Verify all files were saved** (check git status)

Provide:
- [ ] Full backend log output
- [ ] Screenshot of error
- [ ] Database query result: `SELECT COUNT(*) FROM customers`
- [ ] Output of: `grep "PLAN:" backend_logs`

Good luck! The fix is in place - CRUD agent is now properly configured. 🚀
