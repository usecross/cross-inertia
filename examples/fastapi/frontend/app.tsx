import { createInertiaApp } from '@inertiajs/react'
import { createRoot } from 'react-dom/client'
import React from 'react'
import './globals.css'

// Import all page components
import Home from './pages/Home'
import About from './pages/About'
import UsersIndex from './pages/Users/Index'
import UsersShow from './pages/Users/Show'
import Form from './pages/Form'
import Error from './pages/Error'

const pages: Record<string, React.ComponentType<any>> = {
  Home,
  About,
  'Users/Index': UsersIndex,
  'Users/Show': UsersShow,
  Form,
  Error,
}

createInertiaApp({
  resolve: (name) => {
    const page = pages[name]
    if (!page) {
      throw new Error(`Page component "${name}" not found`)
    }
    return page
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
})
