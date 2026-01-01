# QA Testing Example

## E2E Test with Playwright

```typescript
import { test, expect } from '@playwright/test'

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', 'user@example.com')
    await page.fill('input[name="password"]', 'password')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('http://localhost:3000/dashboard')
  })

  test('should create a new task', async ({ page }) => {
    await page.click('text=New Task')
    await page.fill('input[name="title"]', 'Test Task')
    await page.click('button:has-text("Create")')

    // Verify task appears in list
    await expect(page.locator('text=Test Task')).toBeVisible()
  })

  test('should mark task as complete', async ({ page }) => {
    await page.click('input[type="checkbox"]')

    // Verify task shows completed state
    const task = page.locator('.task-item').first()
    await expect(task).toHaveClass(/completed/)
  })

  test('should delete task', async ({ page }) => {
    const taskCount = await page.locator('.task-item').count()
    await page.locator('.task-item').first().hover()
    await page.click('button:has-text("Delete")')

    // Verify task removed
    await expect(page.locator('.task-item')).toHaveCount(taskCount - 1)
  })
})
```

## API Integration Tests

```typescript
import { test, expect } from '@playwright/test'

test.describe('API Tests', () => {
  const baseURL = 'http://localhost:8000'
  let authToken: string

  test.beforeAll(async ({ request }) => {
    const response = await request.post(`${baseURL}/api/auth/login`, {
      data: {
        email: 'user@example.com',
        password: 'password'
      }
    })
    authToken = response.data().access_token
  })

  test('should fetch tasks', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/tasks`, {
      headers: {
        Authorization: `Bearer ${authToken}`
      }
    })

    expect(response.status()).toBe(200)
    expect(response.data()).toBeInstanceOf(Array)
  })

  test('should create task via API', async ({ request }) => {
    const response = await request.post(`${baseURL}/api/tasks`, {
      headers: {
        Authorization: `Bearer ${authToken}`
      },
      data: {
        title: 'API Test Task',
        description: 'Created via API'
      }
    })

    expect(response.status()).toBe(200)
    expect(response.data()).toHaveProperty('id')
  })
})
```
