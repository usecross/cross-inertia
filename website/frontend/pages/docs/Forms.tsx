import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface FormsProps {
  content: {
    title: string
    description: string
  }
}

export default function Forms({ content }: FormsProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>Using the useForm hook</h2>
      <p>
        The <code>useForm</code> hook provides a convenient way to handle form submissions:
      </p>
      <CodeBlock
        code={`import { useForm } from '@inertiajs/react'

export default function CreateUser() {
  const { data, setData, post, processing, errors } = useForm({
    name: '',
    email: '',
  })

  function submit(e: React.FormEvent) {
    e.preventDefault()
    post('/users')
  }

  return (
    <form onSubmit={submit}>
      <input
        value={data.name}
        onChange={(e) => setData('name', e.target.value)}
      />
      {errors.name && <span>{errors.name}</span>}

      <input
        value={data.email}
        onChange={(e) => setData('email', e.target.value)}
      />
      {errors.email && <span>{errors.email}</span>}

      <button disabled={processing}>Create User</button>
    </form>
  )
}`}
        language="tsx"
      />

      <h2>Server-side validation</h2>
      <p>
        Return validation errors using the <code>errors</code> parameter or <code>inertia.back()</code>:
      </p>
      <CodeBlock
        code={`from pydantic import BaseModel, EmailStr, ValidationError

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

@app.post("/users")
async def create_user(request: Request, inertia: InertiaDep):
    form = await request.form()

    try:
        data = CreateUserRequest(**form)
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return inertia.back(errors=errors)

    # Create user...
    return RedirectResponse("/users", status_code=303)`}
        language="python"
      />

      <h2>File uploads</h2>
      <p>
        Use <code>forceFormData</code> for file uploads:
      </p>
      <CodeBlock
        code={`const { data, setData, post } = useForm({
  name: '',
  avatar: null as File | null,
})

function submit(e: React.FormEvent) {
  e.preventDefault()
  post('/users', { forceFormData: true })
}

return (
  <form onSubmit={submit}>
    <input
      type="file"
      onChange={(e) => setData('avatar', e.target.files?.[0] || null)}
    />
    <button type="submit">Upload</button>
  </form>
)`}
        language="tsx"
      />

      <h2>Form progress</h2>
      <p>Track upload progress for large files:</p>
      <CodeBlock
        code={`const { progress, post } = useForm({ file: null })

post('/upload', {
  onProgress: (progress) => {
    console.log(\`\${progress.percentage}% uploaded\`)
  }
})`}
        language="tsx"
      />
    </DocsLayout>
  )
}
