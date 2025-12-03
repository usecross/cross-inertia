import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface DeferredPropsProps {
  content: {
    title: string
    description: string
  }
}

export default function DeferredProps({ content }: DeferredPropsProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>What are deferred props?</h2>
      <p>
        Deferred props allow you to load slow or expensive data asynchronously, after the initial
        page load. This improves perceived performance by showing the page immediately while
        loading additional data in the background.
      </p>

      <h2>Using defer()</h2>
      <p>
        Wrap slow operations with <code>defer()</code> to load them asynchronously:
      </p>
      <CodeBlock
        code={`from inertia import defer
from inertia.fastapi import InertiaDep

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        # Immediate data
        "user": get_user(),

        # Deferred data - loaded after initial render
        "analytics": defer(lambda: fetch_analytics()),
        "notifications": defer(lambda: get_notifications()),
    })`}
        language="python"
      />

      <h2>Handling deferred data on the frontend</h2>
      <p>
        Use the <code>Deferred</code> component to handle loading states:
      </p>
      <CodeBlock
        code={`import { Deferred } from '@inertiajs/react'

export default function Dashboard({ user, analytics, notifications }) {
  return (
    <div>
      <h1>Welcome, {user.name}</h1>

      <Deferred data="analytics" fallback={<Spinner />}>
        <AnalyticsChart data={analytics} />
      </Deferred>

      <Deferred data="notifications" fallback={<div>Loading...</div>}>
        <NotificationList items={notifications} />
      </Deferred>
    </div>
  )
}`}
        language="tsx"
      />

      <h2>Deferred groups</h2>
      <p>Group related deferred props to load them together:</p>
      <CodeBlock
        code={`@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        # Group 1: Analytics data
        "visitors": defer(lambda: get_visitors(), group="analytics"),
        "pageviews": defer(lambda: get_pageviews(), group="analytics"),

        # Group 2: User data
        "notifications": defer(lambda: get_notifications(), group="user"),
        "messages": defer(lambda: get_messages(), group="user"),
    })`}
        language="python"
      />
      <CodeBlock
        code={`<Deferred data={["visitors", "pageviews"]} fallback={<Spinner />}>
  <AnalyticsSection visitors={visitors} pageviews={pageviews} />
</Deferred>`}
        language="tsx"
      />

      <h2>Optional props</h2>
      <p>
        Use <code>optional()</code> for props that should only be evaluated when explicitly
        requested:
      </p>
      <CodeBlock
        code={`from inertia import optional

@app.get("/users")
async def users(inertia: InertiaDep):
    return inertia.render("Users/Index", {
        "users": get_users(),
        # Only evaluated during partial reloads that request it
        "detailed_stats": optional(lambda: compute_expensive_stats()),
    })`}
        language="python"
      />
    </DocsLayout>
  )
}
