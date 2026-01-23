# How to Clear Chat History

## 🆕 **Option 1: Clear Button in UI (EASIEST)**

I just added a clear chat button to your chat interface!

**Location**: Top-right corner of the Chat page

**How to use**:
1. Go to Chat tab
2. Click the **trash/broom icon** (🗑️) in the top-right
3. Confirm the dialog
4. ✅ All chat history cleared!

**Features**:
- Button is disabled when there's no chat history
- Shows confirmation dialog before clearing
- Immediately clears localStorage
- Chat resets to welcome message

---

## **Option 2: Browser Developer Console**

If you want to manually clear without the UI button:

**Steps**:
1. Open your browser (Chrome/Firefox/Safari)
2. Press `F12` or `Cmd+Option+I` (Mac) to open Developer Tools
3. Go to **Console** tab
4. Paste this command:
   ```javascript
   localStorage.removeItem('finbank_chat_history')
   ```
5. Press `Enter`
6. Refresh the page (`Cmd+R` or `F5`)

---

## **Option 3: Browser Settings**

Clear all localStorage for the site:

### **Chrome/Edge**:
1. Open http://localhost:4200
2. Click the 🔒 lock icon in address bar
3. Click "Site settings"
4. Scroll down to "Storage"
5. Click "Clear data"
6. Refresh page

### **Firefox**:
1. Press `Shift+F9` to open Storage Inspector
2. Expand "Local Storage"
3. Click `http://localhost:4200`
4. Right-click `finbank_chat_history`
5. Select "Delete Item"
6. Refresh page

### **Safari**:
1. Safari → Preferences → Privacy
2. Click "Manage Website Data"
3. Search for "localhost"
4. Click "Remove"
5. Refresh page

---

## **Option 4: Clear via API/Code**

If you want to programmatically clear chat:

### **TypeScript (Angular)**:
```typescript
// In any component with ChatService injected
constructor(private chatService: ChatService) {}

clearAllHistory() {
  this.chatService.clearHistory();
}
```

### **JavaScript Console**:
```javascript
// Access Angular component
const chatComponent = ng.getComponent(document.querySelector('app-chat'));
chatComponent.clearChat();
```

---

## **Understanding Chat Persistence**

### **Where is chat stored?**
- **Location**: Browser's `localStorage`
- **Key**: `finbank_chat_history`
- **Format**: JSON array of messages

### **What persists?**
```json
[
  {
    "id": "1737599123456",
    "role": "user",
    "content": "show all users",
    "timestamp": "2026-01-22T23:12:03.456Z"
  },
  {
    "id": "1737599128789",
    "role": "assistant",
    "content": "Here are all users...",
    "timestamp": "2026-01-22T23:12:08.789Z",
    "agentsUsed": ["query"]
  }
]
```

### **When does it persist?**
- ✅ After every message sent
- ✅ After every response received
- ✅ Survives tab close
- ✅ Survives browser close
- ✅ Survives page refresh
- ❌ Does NOT sync across devices
- ❌ Does NOT sync across different browsers

### **When is it cleared?**
- ✅ When you click the clear button
- ✅ When you call `chatService.clearHistory()`
- ✅ When you clear browser data
- ❌ Does NOT clear on logout (no auth implemented)
- ❌ Does NOT auto-expire

---

## **Testing the Clear Button**

### **Test Steps**:
1. **Send some messages**:
   ```
   show all users
   delete user Farida MD
   list premium tier users
   ```

2. **Verify persistence**:
   - Close the Chat tab
   - Open Chat tab again
   - ✅ Messages should still be there

3. **Clear chat**:
   - Click the 🗑️ icon in top-right
   - Click "OK" in confirmation dialog
   - ✅ All messages cleared
   - ✅ Welcome message appears

4. **Verify cleared**:
   - Refresh the page
   - ✅ Chat is still empty (except welcome message)

---

## **Keyboard Shortcuts (Future Enhancement)**

Could add:
```typescript
// In chat.component.ts
@HostListener('document:keydown', ['$event'])
handleKeyboard(event: KeyboardEvent) {
  // Ctrl+Shift+Delete to clear chat
  if (event.ctrlKey && event.shiftKey && event.key === 'Delete') {
    this.clearChat();
  }
}
```

---

## **File Modified**

**[frontend/src/app/components/chat/chat.component.ts](frontend/src/app/components/chat/chat.component.ts)**

**Changes**:
1. Added chat header with title and clear button
2. Added `MatTooltipModule` import
3. Added `clearChat()` method with confirmation
4. Added CSS for header styling

**Lines Changed**:
- Line 8: Added `MatTooltipModule` import
- Line 28: Added `MatTooltipModule` to imports array
- Line 31-38: Added chat header with clear button
- Line 135-153: Added header CSS
- Line 414-418: Added `clearChat()` method

---

## **Current Clear Button Features**

```typescript
clearChat(): void {
  // Shows confirmation dialog
  if (confirm('Are you sure you want to clear all chat history?')) {
    // Clears localStorage
    this.chatService.clearHistory();

    // Result:
    // - messages array becomes []
    // - localStorage.removeItem('finbank_chat_history')
    // - Chat resets to welcome message
  }
}
```

---

## **Troubleshooting**

### **Clear button not appearing?**
- Refresh the page (`Cmd+R`)
- Check browser console for errors
- Verify frontend is running: http://localhost:4200

### **Clear button disabled/grayed out?**
- This is normal when there are no messages
- Send a message first, then the button becomes active

### **Chat still shows old messages after clearing?**
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Check if multiple tabs are open
- Verify localStorage is actually cleared (F12 → Application → Local Storage)

### **Chat doesn't persist after clearing and refreshing?**
- This is expected! Clear = delete forever
- Send new messages to start a new history

---

## **Summary**

**Easiest way**: Just click the 🗑️ button in the top-right of the Chat page!

The button will appear after the frontend rebuilds (should auto-reload in a few seconds).

Enjoy your clean chat! 🎉
