---
title: History Encryption
description: Protect sensitive data in browser history
---

History encryption prevents users from viewing sensitive information in their browser history after logging out. This is crucial for applications handling banking data, healthcare records, admin panels, or any sensitive information.

## The Problem

By default, browsers cache page data. When users press the back button, they see the cached version - even after logging out. This can expose:

- Bank account balances and transactions
- Healthcare records (HIPAA compliance)
- Admin panel data
- Personal identifying information
- Payment details

## How History Encryption Works

Cross-Inertia encrypts page state using the browser's Web Crypto API:

1. **Encryption**: Page data is encrypted with AES-GCM before being stored in browser history
2. **Key Storage**: Encryption keys are stored in `sessionStorage`
3. **Key Rotation**: `clear_history()` rotates keys, making old history unreadable
4. **Logout**: After logout, previous encrypted pages can't be decrypted

## Basic Usage

### Protect Sensitive Pages

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaDep

app = FastAPI()

@app.get("/account/transactions")
async def transactions(inertia: InertiaDep):
    """Bank transactions page with encryption"""
    # Enable encryption for this page
    inertia.encrypt_history()
    
    return inertia.render("Transactions", {
        "balance": user.balance,
        "transactions": user.get_transactions()
    })
```

### Clear History on Logout

```python
@app.post("/logout")
async def logout(inertia: InertiaDep):
    """Logout and clear encrypted history"""
    # Clear user session
    clear_user_session()
    
    # Rotate encryption keys (makes old history unreadable)
    inertia.clear_history()
    
    return inertia.render("Login", {})
```

## Method Chaining

You can chain `encrypt_history()` with `render()`:

```python
@app.get("/admin/users")
async def admin_users(inertia: InertiaDep):
    return inertia.encrypt_history().render("Admin/Users", {
        "users": get_all_users()
    })
```

## Complete Banking Example

Here's a complete example for a banking application:

```python
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from inertia.fastapi import InertiaDep

app = FastAPI()

# Middleware to check authentication
def require_auth(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login")
    return None

@app.get("/login")
async def login_form(inertia: InertiaDep):
    """Public login page - no encryption needed"""
    return inertia.render("Login", {})

@app.post("/login")
async def login(inertia: InertiaDep):
    """Process login"""
    form_data = await inertia.request.json()
    
    # Authenticate user
    user = authenticate(form_data["email"], form_data["password"])
    
    if not user:
        return inertia.render("Login", {}, errors={
            "email": "Invalid credentials"
        })
    
    # Set session
    set_user_session(user)
    
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/dashboard", dependencies=[Depends(require_auth)])
async def dashboard(inertia: InertiaDep):
    """Dashboard - encrypt sensitive financial data"""
    inertia.encrypt_history()
    
    user = get_current_user()
    
    return inertia.render("Dashboard", {
        "user": user,
        "accounts": user.get_accounts(),
        "recent_transactions": user.get_recent_transactions(limit=5)
    })

@app.get("/account/{account_id}/transactions", dependencies=[Depends(require_auth)])
async def account_transactions(account_id: int, inertia: InertiaDep):
    """Transaction history - highly sensitive"""
    inertia.encrypt_history()
    
    user = get_current_user()
    account = user.get_account(account_id)
    
    return inertia.render("Transactions", {
        "account": account,
        "transactions": account.get_transactions(),
        "balance": account.balance
    })

@app.get("/settings", dependencies=[Depends(require_auth)])
async def settings(inertia: InertiaDep):
    """Settings page - less sensitive, no encryption"""
    user = get_current_user()
    
    return inertia.render("Settings", {
        "user": user,
        "preferences": user.preferences
    })

@app.post("/logout", dependencies=[Depends(require_auth)])
async def logout(inertia: InertiaDep):
    """Logout and clear all encrypted history"""
    clear_user_session()
    
    # Critical: Clear encryption keys to prevent back button access
    inertia.clear_history()
    
    return inertia.render("Login", {
        "message": "You have been logged out"
    })
```

## Healthcare (HIPAA) Example

```python
@app.get("/patient/{patient_id}/records")
async def patient_records(patient_id: int, inertia: InertiaDep):
    """Protected health information (PHI)"""
    # HIPAA compliance: encrypt patient data
    inertia.encrypt_history()
    
    patient = get_patient(patient_id)
    
    return inertia.render("PatientRecords", {
        "patient": patient,
        "medical_history": patient.get_medical_history(),
        "prescriptions": patient.get_prescriptions(),
        "test_results": patient.get_test_results()
    })

@app.get("/patient/{patient_id}/billing")
async def patient_billing(patient_id: int, inertia: InertiaDep):
    """Billing information - also sensitive"""
    inertia.encrypt_history()
    
    patient = get_patient(patient_id)
    
    return inertia.render("Billing", {
        "patient": patient,
        "invoices": patient.get_invoices(),
        "insurance": patient.insurance_info
    })
```

## Admin Panel Example

```python
@app.get("/admin/users")
async def admin_users(inertia: InertiaDep):
    """Admin panel - encrypt user data"""
    inertia.encrypt_history()
    
    return inertia.render("Admin/Users", {
        "users": get_all_users(),
        "stats": get_user_stats()
    })

@app.get("/admin/audit-log")
async def audit_log(inertia: InertiaDep):
    """Audit log - sensitive security information"""
    inertia.encrypt_history()
    
    return inertia.render("Admin/AuditLog", {
        "logs": get_audit_logs()
    })
```

## Security Features

### AES-GCM Encryption

- **Algorithm**: AES-GCM (256-bit keys)
- **Randomization**: Each encryption uses a unique IV (initialization vector)
- **Authentication**: GCM mode provides authenticated encryption
- **Key Storage**: Keys stored in `sessionStorage` (cleared on tab close)

### Key Rotation

When you call `clear_history()`:

1. Old encryption keys are deleted
2. New keys are generated
3. Previous encrypted pages become unreadable
4. User must re-authenticate to view sensitive data

### HTTPS Requirement

History encryption only works over HTTPS (except localhost for development):

- Production: Requires HTTPS
- Development: Works on `localhost` or `127.0.0.1`
- Mixed content: Falls back to unencrypted if HTTPS unavailable

## When to Use History Encryption

### ✅ Use for:

- Banking and financial data
- Healthcare records (HIPAA)
- Admin panels with user data
- Payment information
- Personal identifying information (PII)
- Social Security Numbers, tax records
- Internal company data

### ❌ Don't use for:

- Public pages
- Marketing content
- Blog posts
- Product listings
- Search results
- About/contact pages

## Best Practices

1. **Encrypt All Sensitive Pages**: Don't forget any page with sensitive data
2. **Always Clear on Logout**: Call `clear_history()` in your logout handler
3. **Use HTTPS in Production**: Encryption requires secure context
4. **Test the Back Button**: Verify encrypted pages can't be read after logout
5. **Combine with Session Management**: Clear both server sessions and history

## Testing History Encryption

### Manual Testing

1. Login to your application
2. Visit sensitive pages (they should be encrypted)
3. Logout
4. Press the back button
5. Verify encrypted pages are unreadable or redirect to login

### Automated Testing

```python
from playwright.sync_api import sync_playwright

def test_history_encryption():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Login
        page.goto("http://localhost:8000/login")
        page.fill("#email", "user@example.com")
        page.fill("#password", "password")
        page.click("button[type=submit]")
        
        # Visit encrypted page
        page.goto("http://localhost:8000/account/transactions")
        assert "transactions" in page.content().lower()
        
        # Logout
        page.click("#logout-button")
        
        # Try to go back
        page.go_back()
        
        # Should be redirected or unable to decrypt
        assert page.url == "http://localhost:8000/login"
        
        browser.close()
```

## Browser Support

History encryption uses modern web APIs:

- ✅ Chrome 37+
- ✅ Firefox 34+
- ✅ Safari 11+
- ✅ Edge 79+
- ❌ IE 11 (not supported)

For unsupported browsers, the feature gracefully degrades (pages stored unencrypted).

## How It Compares

### vs. Cache-Control Headers

```python
# Cache-Control prevents caching but doesn't encrypt
response.headers["Cache-Control"] = "no-store, private"
```

**Problem**: Users can still press back button and see cached data in browser memory.

**Solution**: History encryption encrypts the data, making it unreadable without the key.

### vs. Server-Side Session Validation

```python
# Checking session on every request
if not is_authenticated():
    return RedirectResponse("/login")
```

**Problem**: This doesn't prevent browser from showing cached data when pressing back.

**Solution**: History encryption ensures even cached data is encrypted.

## Limitations

1. **JavaScript Required**: Encryption happens client-side
2. **HTTPS Required**: (except localhost)
3. **sessionStorage**: Keys cleared when tab closes
4. **Performance**: Minimal overhead (encryption is fast)

## Next Steps

- [Shared Data](/guides/shared-data/) - Flash messages for login/logout
- [External Redirects](/guides/external-redirects/) - OAuth with encryption
- [Configuration](/guides/configuration/) - Set up HTTPS for production
