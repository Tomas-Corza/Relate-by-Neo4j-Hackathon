import {defineConfig,devices} from '@playwright/test';

export default defineConfig({
  testDir:'./e2e',
  fullyParallel:false,
  workers:1,
  retries:0,
  timeout:45000,
  expect:{timeout:15000},
  reporter:[['list'],['html',{open:'never'}]],
  use:{baseURL:'http://127.0.0.1:8765',trace:'retain-on-failure',screenshot:'only-on-failure'},
  projects:[{name:'chromium',use:{...devices['Desktop Chrome']}}],
  webServer:{
    command:'python -m uvicorn preview_api:app --host 127.0.0.1 --port 8765',
    cwd:'..',
    url:'http://127.0.0.1:8765/_stcore/health',
    timeout:60000,
    reuseExistingServer:false,
    env:{OPENAI_API_KEY:'',PYTHONUNBUFFERED:'1'}
  }
});
