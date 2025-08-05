<script lang="ts">
  import Button from '$lib/components/shared/Button.svelte';
  import { Settings, Database, User, Bell, Palette } from 'lucide-svelte';
</script>

<svelte:head>
  <title>Settings - Bright Ideas</title>
  <meta name="description" content="Configure your Bright Ideas application settings" />
</svelte:head>

<div class="min-h-screen bg-secondary-50 py-8">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center space-x-3 mb-2">
        <Settings size={32} class="text-primary-600" />
        <h1 class="text-3xl font-bold text-secondary-900">Settings</h1>
      </div>
      <p class="text-secondary-600">Configure your Bright Ideas application preferences</p>
    </div>

    <!-- Settings Sections -->
    <div class="space-y-6">
      
      <!-- Account Settings -->
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
        <div class="p-6">
          <div class="flex items-center space-x-3 mb-4">
            <User size={20} class="text-secondary-600" />
            <h2 class="text-xl font-semibold text-secondary-900">Account</h2>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-secondary-700 mb-1">
                Display Name
              </label>
              <input
                type="text"
                class="w-full max-w-md px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Your name"
                disabled
              />
              <p class="text-sm text-secondary-500 mt-1">Account management coming soon</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Application Settings -->
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
        <div class="p-6">
          <div class="flex items-center space-x-3 mb-4">
            <Palette size={20} class="text-secondary-600" />
            <h2 class="text-xl font-semibold text-secondary-900">Appearance</h2>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-secondary-700 mb-1">
                Theme
              </label>
              <select
                class="w-full max-w-md px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled
              >
                <option>Light</option>
                <option>Dark</option>
                <option>System</option>
              </select>
              <p class="text-sm text-secondary-500 mt-1">Theme customization coming soon</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Notifications -->
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
        <div class="p-6">
          <div class="flex items-center space-x-3 mb-4">
            <Bell size={20} class="text-secondary-600" />
            <h2 class="text-xl font-semibold text-secondary-900">Notifications</h2>
          </div>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <label class="text-sm font-medium text-secondary-700">
                  Email Notifications
                </label>
                <p class="text-sm text-secondary-500">Get notified about important updates</p>
              </div>
              <input
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-secondary-300 rounded"
                disabled
              />
            </div>
            <div class="flex items-center justify-between">
              <div>
                <label class="text-sm font-medium text-secondary-700">
                  Plan Generation Alerts
                </label>
                <p class="text-sm text-secondary-500">Notify when AI finishes generating plans</p>
              </div>
              <input
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-secondary-300 rounded"
                disabled
              />
            </div>
            <p class="text-sm text-secondary-500">Notification preferences coming soon</p>
          </div>
        </div>
      </div>

      <!-- Data Management -->
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
        <div class="p-6">
          <div class="flex items-center space-x-3 mb-4">
            <Database size={20} class="text-secondary-600" />
            <h2 class="text-xl font-semibold text-secondary-900">Data Management</h2>
          </div>
          <div class="space-y-4">
            <div>
              <h3 class="text-sm font-medium text-secondary-700 mb-2">Export Data</h3>
              <p class="text-sm text-secondary-600 mb-3">
                Download all your ideas, refinement sessions, and plans
              </p>
              <Button variant="outline" disabled>
                Export All Data
              </Button>
            </div>
            <div class="pt-4 border-t border-secondary-200">
              <h3 class="text-sm font-medium text-red-700 mb-2">Danger Zone</h3>
              <p class="text-sm text-secondary-600 mb-3">
                Permanently delete all your data. This action cannot be undone.
              </p>
              <Button variant="outline" disabled>
                Delete All Data
              </Button>
            </div>
            <p class="text-sm text-secondary-500">Data management features coming soon</p>
          </div>
        </div>
      </div>

      <!-- Application Info -->
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
        <div class="p-6">
          <h2 class="text-xl font-semibold text-secondary-900 mb-4">About Bright Ideas</h2>
          <div class="space-y-2 text-sm text-secondary-600">
            <p><strong>Version:</strong> 2.0.0 (Structured Refinement Architecture)</p>
            <p><strong>Architecture:</strong> AI-powered brainstorming and planning</p>
            <p><strong>Features:</strong> Idea capture, AI refinement, plan generation, export</p>
          </div>
        </div>
      </div>

    </div>

    <!-- Back Navigation -->
    <div class="mt-8">
      <Button variant="ghost" href="/">
        ← Back to Dashboard
      </Button>
    </div>
  </div>
</div>