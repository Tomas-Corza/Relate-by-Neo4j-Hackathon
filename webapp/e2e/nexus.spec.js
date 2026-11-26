import {test,expect} from '@playwright/test';
import {readFile} from 'node:fs/promises';

const pages=['Overview','Advertising','Revenue sources','Profit analysis','Product inventory','Customer journeys','Business connections','Budget planning','AI assistant','Reports'];
async function visit(page,name){
  const nav=page.locator('.sidebar').getByRole('button',{name,exact:true});
  if(!(await nav.isVisible())) await page.getByRole('button',{name:'Menu',exact:true}).click();
  await nav.click();
  await expect(page.getByRole('heading',{level:1})).toHaveText(name+'.');
}
async function start(page){
  await page.goto('/');
  await expect(page.locator('.hero-value')).toHaveText('$6,970.00');
}
async function download(page,locator,name){
  const [file]=await Promise.all([page.waitForEvent('download'),locator.click()]);
  expect(file.suggestedFilename()).toBe(name);
  expect(await file.failure()).toBeNull();
  return readFile(await file.path());
}
test('all ten workspaces render with real backend evidence',async({page})=>{
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await start(page);
  for(const name of pages){
    await visit(page,name);
    if(name!=='Overview') await expect(page.locator('.canvas .surface').first()).toBeVisible();
    await expect(page.getByRole('alert')).toHaveCount(0);
  }
  expect(errors).toEqual([]);
});
test('model switch preserves recorded revenue and changes campaign credit',async({page})=>{
  await start(page);
  const baseline=await (await page.request.get('/api/overview?model=linear')).json();
  const response=page.waitForResponse(r=>r.url().includes('/api/overview?model=first_touch')&&r.ok());
  await page.getByLabel('Revenue credit model').selectOption('first_touch');
  const changed=await (await response).json();
  await expect(page.locator('.hero-value')).toHaveText('$6,970.00');
  expect(changed.financials).toEqual(baseline.financials);
  expect(changed.campaigns.map(c=>c.revenue)).not.toEqual(baseline.campaigns.map(c=>c.revenue));
  await page.getByRole('button',{name:/See supporting details/}).first().click();
  await expect(page.locator('.inspector')).toContainText('Limited edition');
});
test('guided demo navigates all six steps and exits',async({page})=>{
  await start(page);
  await page.getByRole('button',{name:/Start guided demo/}).click();
  const guide=page.getByLabel('Guided demo',{exact:true});
  for(const [i,name] of ['Overview','Business connections','Revenue sources','AI assistant','Budget planning','Reports'].entries()){
    await expect(page.getByRole('heading',{level:1})).toHaveText(name+'.');
    await expect(guide).toContainText('STEP '+(i+1)+' OF 6');
    await guide.getByRole('button',{name:i===5?'Finish demo':/Next step/}).click();
  }
  await expect(page.getByRole('heading',{level:1})).toHaveText('Overview.');
  await expect(page.getByRole('button',{name:/Start guided demo/})).toBeVisible();
});
test('canonical ZIP and persistent Relate store download',async({page})=>{
  await start(page);
  await visit(page,'Business connections');
  await page.getByText('Developer audit and reproducibility',{exact:true}).click();
  const zip=await download(page,page.getByRole('link',{name:/Download original Nexus CSV dataset/}),'nexus-original-csv.zip');
  expect(zip.subarray(0,4).toString('hex')).toBe('504b0304');
  const store=await download(page,page.getByRole('link',{name:/Download persistent Relate store/}),'nexus-demo.rl');
  expect(store.length).toBeGreaterThan(0);
});
test('budget simulation conserves total spend and produces modeled delta',async({page})=>{
  await start(page);
  await visit(page,'Budget planning');
  await page.getByLabel('Reduce spend from').selectOption('C2');
  await page.getByLabel('Transfer to').selectOption('C3');
  await page.getByLabel('Transfer amount ($)').fill('300');
  const response=page.waitForResponse(r=>r.url().endsWith('/api/budget')&&r.ok());
  await page.getByRole('button',{name:'Calculate scenario'}).click();
  const result=await (await response).json();
  expect(result.records.reduce((s,r)=>s+r.baseline_spend,0)).toBe(3150);
  expect(result.records.reduce((s,r)=>s+r.scenario_spend,0)).toBe(3150);
  expect(result.records.reduce((s,r)=>s+r.scenario_profit-r.baseline_profit,0)).toBeCloseTo(285.27,2);
  await expect(page.getByText('Scenario profit after ads',{exact:true})).toBeVisible();
});
test('custom report generates real data and CSV/JSON exports',async({page})=>{
  await start(page);
  await visit(page,'Reports');
  await page.getByLabel('Report scope').selectOption('orders');
  const response=page.waitForResponse(r=>r.url().endsWith('/api/reports')&&r.ok());
  await page.getByRole('button',{name:'Generate report'}).click();
  const data=await (await response).json();
  expect(data.records).toHaveLength(3);
  expect(data.records.reduce((s,r)=>s+r.revenue,0)).toBe(6970);
  await expect(page.getByRole('heading',{name:'Report results · 3 rows'})).toBeVisible();
  const csv=await download(page,page.getByRole('button',{name:'Download custom report CSV'}),'nexus_custom_report.csv');
  expect(csv.toString()).toContain('"revenue"');
  expect(csv.toString()).toContain('Everyday kit');
  const json=await download(page,page.getByRole('button',{name:'Download report configuration JSON'}),'nexus_report_config.json');
  expect(JSON.parse(json.toString()).scope).toBe('orders');
});
test('investigation runs real deterministic tools without API key and benchmark is visible',async({page})=>{
  await start(page);
  await visit(page,'AI assistant');
  await expect(page.getByRole('heading',{name:'Connected intelligence benchmark'})).toBeVisible();
  await expect(page.getByText('93.46%',{exact:true}).first()).toBeVisible();
  const response=page.waitForResponse(r=>r.url().endsWith('/api/analyst')&&r.ok());
  await page.getByRole('button',{name:'Run investigation'}).click();
  const data=await (await response).json();
  expect(data.mode).toBe('deterministic');
  expect(data.trace.some(t=>t.tool==='graph_traversal')).toBe(true);
  expect(data.answer).toContain('Limited edition');
  await expect(page.getByRole('heading',{name:'Investigation findings'})).toBeVisible();
  await expect(page.locator('.analyst-answer')).toContainText('Limited edition');
});
test('mobile navigation and main workspaces are usable',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await start(page);
  for(const name of ['Business connections','Budget planning','AI assistant','Reports','Overview']){
    await visit(page,name);
    await expect(page.getByRole('button',{name:'Menu',exact:true})).toBeVisible();
    await expect(page.locator('.sidebar')).not.toBeVisible();
    const heading=page.getByRole('heading',{level:1});
    const bounds=await heading.boundingBox();
    expect(bounds.x).toBeGreaterThanOrEqual(0);
    expect(bounds.x+bounds.width).toBeLessThanOrEqual(391);
  }
});
