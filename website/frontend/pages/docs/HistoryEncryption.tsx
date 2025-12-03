import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface HistoryEncryptionProps {
  content: {
    title: string
    description: string
  }
}

export default function HistoryEncryption({ content }: HistoryEncryptionProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>Why encrypt history?</h2>
      <p>
        Browser history stores page state, which may include sensitive data. History encryption
        protects this data by encrypting the history state using the Web Crypto API.
      </p>
      <p>Use cases include:</p>
      <ul>
        <li>Banking and financial applications</li>
        <li>Healthcare portals with patient data</li>
        <li>Admin panels with sensitive information</li>
        <li>Any page displaying personal data</li>
      </ul>

      <h2>Enabling history encryption</h2>
      <p>
        Call <code>encrypt_history()</code> before rendering sensitive pages:
      </p>
      <CodeBlock
        code={`@app.get("/account/transactions")
async def transactions(inertia: InertiaDep):
    inertia.encrypt_history()
    return inertia.render("Transactions", {
        "balance": user.balance,
        "transactions": user.get_transactions()
    })`}
        language="python"
      />
      <p>Method chaining is also supported:</p>
      <CodeBlock
        code={`return inertia.encrypt_history().render("Transactions", {...})`}
        language="python"
      />

      <h2>How it works</h2>
      <ul>
        <li>Uses the browser's Web Crypto API (AES-GCM encryption)</li>
        <li>Encryption keys are stored in sessionStorage</li>
        <li>Only works over HTTPS (except localhost for development)</li>
        <li>Each browser tab has its own encryption key</li>
      </ul>

      <h2>Clearing encrypted history</h2>
      <p>
        Use <code>clear_history()</code> to rotate encryption keys, making previously encrypted
        pages unreadable. This is typically done on logout:
      </p>
      <CodeBlock
        code={`@app.post("/logout")
async def logout(inertia: InertiaDep):
    clear_user_session()
    inertia.clear_history()  # Rotate encryption keys
    return inertia.render("Login", {})`}
        language="python"
      />

      <h2>Frontend configuration</h2>
      <p>
        History encryption requires Inertia.js v2.0+. Enable it in your app setup:
      </p>
      <CodeBlock
        code={`createInertiaApp({
  // ... other options
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
})`}
        language="tsx"
      />
      <p>
        The encryption is handled automatically by Inertia.js when the server sends the appropriate
        headers.
      </p>

      <h2>Security considerations</h2>
      <ul>
        <li>History encryption is a defense-in-depth measure, not a primary security control</li>
        <li>Always use HTTPS in production</li>
        <li>Clear history on logout for shared computers</li>
        <li>Combine with proper session management and authentication</li>
      </ul>
    </DocsLayout>
  )
}
