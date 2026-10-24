/** End-to-end sales demo scenarios; no production acceptance. */
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import { root } from './client-runtime.mjs';
const require=createRequire(import.meta.url);
const {chromium}=require(path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const output=path.join(root,'test-results');await fs.mkdir(output,{recursive:true});
const startedAt=new Date().toISOString();const results=[];const errors=[];
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--enable-unsafe-swiftshader']});
const web=await browser.newPage({viewport:{width:1440,height:1000}});
const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
for(const page of [web,mobile]) page.on('pageerror',e=>errors.push(e.message));
const check=async(id,action)=>{try{await action();results.push({id,result:'Pass'});console.log(id+': Pass');}catch(e){results.push({id,result:'Fail',detail:e.message});console.log(id+': Fail — '+e.message);}};
const nav=async(name)=>web.getByRole('navigation').getByRole('button',{name,exact:true}).click();
const waitForAria=async(page,pattern)=>{
 let snapshot='';
 for(let attempt=0;attempt<100;attempt++){
  snapshot=await page.locator('body').ariaSnapshot();
  if(pattern.test(snapshot))return;
  await new Promise(resolve=>setTimeout(resolve,50));
 }
 assert.match(snapshot,pattern);
};
try{
 await check('DEMO-WEB-BASELINE',async()=>{
  assert.equal((await web.goto('http://localhost:3000')).status(),200);
  await web.getByRole('heading',{name:'Your nursery day, all together.'}).waitFor();
  assert.equal(await web.getByTestId('present-total').innerText(),'8 / 12');
  assert.equal(await web.locator('.scenario-card').count(),4);
  assert.match(await web.locator('.metrics').innerText(),/18,000/);
  await web.screenshot({path:path.join(output,'demo-dashboard-en.png'),fullPage:true});
 });
 await check('DEMO-WEB-ATTENDANCE-TIMELINE',async()=>{
  await web.getByRole('button',{name:'Start the morning story',exact:false}).click();
  await web.getByRole('button',{name:'Check in Farida Demo',exact:true}).click();
  await web.getByRole('button',{name:'Check out Farida Demo',exact:true}).waitFor();
  await nav('Overview');assert.equal(await web.getByTestId('present-total').innerText(),'9 / 12');
  await nav('Daily care');await web.getByRole('combobox',{name:'Child',exact:true}).selectOption('C009');
  await web.getByText('Arrival recorded in the demo.',{exact:true}).waitFor();
  await web.getByRole('combobox',{name:'Child',exact:true}).selectOption('C001');
  await web.getByRole('button',{name:'Add sample care update',exact:true}).click();
  await web.getByText('Garden play · explored leaves and colours with friends.',{exact:true}).waitFor();
 });
 await check('DEMO-WEB-FEES',async()=>{
  await nav('Fees & follow-up');
  assert.equal(await web.locator('tbody tr').count(),6);
  await web.getByRole('button',{name:'Preview reminder INV-26-003',exact:true}).click();
  assert.match(await web.getByRole('complementary',{name:'Reminder preview'}).innerText(),/1,500/);
  await web.getByRole('button',{name:'Record demo follow-up',exact:true}).click();
  await web.getByText('Previewed locally',{exact:true}).waitFor();
  await web.getByRole('checkbox',{name:'Outstanding invoices only'}).uncheck();
  assert.equal(await web.locator('tbody tr').count(),12);
 });
 await check('DEMO-WEB-ADMISSIONS-BRANCHES-RESET',async()=>{
  await nav('Admissions');
  await web.getByRole('button',{name:'Schedule sample visit Amira’s family',exact:true}).click();
  await web.getByText('Welcome the family · 27 October at 10:00',{exact:false}).waitFor();
  await web.getByRole('combobox',{name:'Branch',exact:true}).selectOption('B002');
  await web.getByRole('heading',{name:'Fares’s family',exact:true}).waitFor();
  assert.equal(await web.getByRole('heading',{name:'Amira’s family',exact:true}).count(),0);
  await nav('Attendance');assert.equal(await web.locator('tbody tr').count(),12);
  assert.match(await web.locator('tbody').innerText(),/Layla Demo/);
  assert.doesNotMatch(await web.locator('tbody').innerText(),/Adam Demo/);
  await web.getByRole('button',{name:'Reset demo',exact:true}).click();
  assert.equal(await web.getByTestId('present-total').innerText(),'8 / 12');
  await nav('Admissions');await web.getByRole('button',{name:'Schedule sample visit Amira’s family',exact:true}).waitFor();
  await nav('Daily care');assert.equal(await web.getByText('Garden play · explored leaves and colours with friends.',{exact:true}).count(),0);
  await nav('Fees & follow-up');await web.getByRole('button',{name:'Preview reminder INV-26-003',exact:true}).waitFor();
 });
 await check('DEMO-WEB-ARABIC-REFLOW',async()=>{
  await web.getByRole('button',{name:'العربية',exact:true}).click();
  assert.equal(await web.locator('html').getAttribute('dir'),'rtl');
  await nav('نظرة عامة');await web.getByRole('heading',{name:'يوم حضانتك، في مكان واحد.',exact:true}).waitFor();
  await web.screenshot({path:path.join(output,'demo-dashboard-ar.png'),fullPage:true});
  for(const width of [390,320]){
   await web.setViewportSize({width,height:844});
   for(const name of ['نظرة عامة','الفصول','الحضور','الرعاية اليومية','الرسوم والمتابعة','القبول']){
    await nav(name);assert.ok(await web.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),name+' must fit '+width);
   }
  }
  await web.screenshot({path:path.join(output,'demo-web-narrow-ar.png'),fullPage:true});
 });
 await check('DEMO-MOBILE-PARENT-STAFF-RESET',async()=>{
  assert.equal((await mobile.goto('http://localhost:3200')).status(),200);
  await mobile.locator('flutter-view').waitFor({state:'attached',timeout:60000});
  const placeholder=mobile.locator('flt-semantics-placeholder');if(await placeholder.count())await placeholder.evaluate(e=>e.click());
  await mobile.getByRole('button',{name:'العربية',exact:true}).waitFor({timeout:30000});
  await mobile.screenshot({path:path.join(output,'demo-mobile-parent-en.png'),fullPage:true});
  // Flutter semantics describes dropdowns as buttons; match the selected role.
  await fs.writeFile(path.join(output,'demo-mobile-initial-aria.txt'),await mobile.locator('body').ariaSnapshot());
  await mobile.getByRole('button',{name:'Demo experience Parent',exact:true}).click();
  await mobile.getByRole('menuitem',{name:'Teacher',exact:true}).click();
  const action=mobile.getByRole('button',{name:'Add sample care update',exact:true});
  await action.click();
  await waitForAria(mobile,/Garden play · explored leaves and colours with friends/);
  await mobile.getByRole('button',{name:'Demo experience Teacher',exact:true}).click();
  await mobile.getByRole('menuitem',{name:'Parent',exact:true}).click();
  await waitForAria(mobile,/Garden play · explored leaves and colours with friends/);
  await mobile.screenshot({path:path.join(output,'demo-mobile-staff-en.png'),fullPage:true});
  await mobile.getByRole('button',{name:'Reset demo',exact:true}).click();
  await mobile.getByRole('button',{name:'Demo experience Parent',exact:true}).waitFor();
 });
 await check('DEMO-MOBILE-ARABIC',async()=>{
  await mobile.getByRole('button',{name:'العربية',exact:true}).click();
  await mobile.getByRole('button',{name:'English',exact:true}).waitFor();
  assert.match(await mobile.locator('body').ariaSnapshot(),/آدم التجريبي|أقرب إلى طفلك/);
  await mobile.screenshot({path:path.join(output,'demo-mobile-parent-ar.png'),fullPage:true});
  assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  const font=await mobile.request.get('http://localhost:3200/assets/assets/fonts/NotoNaskhArabic-Regular.ttf');assert.equal(font.status(),200);
  assert.deepEqual(errors,[]);
 });
 await check('DEMO-MOBILE-DIRECT-VIEWS',async()=>{
  for(const view of ['parent','teacher']){
   await mobile.goto('http://localhost:3200/?view='+view);
   await mobile.locator('flutter-view').waitFor({state:'attached',timeout:60000});
   const placeholder=mobile.locator('flt-semantics-placeholder');
   if(await placeholder.count())await placeholder.evaluate(e=>e.click());
   const name='Demo experience '+(view==='teacher'?'Teacher':'Parent');
   await mobile.getByRole('button',{name,exact:true}).waitFor({timeout:30000});
   if(view==='teacher')await mobile.getByRole('button',{name:'Add sample care update',exact:true}).waitFor();
   await mobile.screenshot({path:path.join(output,'mobile-direct-'+view+'.png'),fullPage:true});
   await mobile.getByRole('button',{name:'Reset demo',exact:true}).click();
   await mobile.getByRole('button',{name,exact:true}).waitFor();
  }
 });
 await check('DEMO-LINKS-STATIC-BOUNDARIES',async()=>{
  const address=Object.entries(os.networkInterfaces()).flatMap(([name,values])=>(values??[]).filter(a=>a.family==='IPv4'&&!a.internal&&!/virtual|vethernet/i.test(name)).map(a=>a.address))[0];
  assert.ok(address);
  for(const port of [3000,3200])assert.equal((await fetch('http://'+address+':'+port)).status,200);
  for(const route of ['/.git/config','/..%2F..%2Fpackage.json'])assert.equal((await mobile.request.get('http://localhost:3200'+route)).status(),404);
 });
}finally{
 for(const [name,page]of [['web',web],['mobile',mobile]])await fs.writeFile(path.join(output,'demo-'+name+'-aria.txt'),await page.locator('body').ariaSnapshot());
 await browser.close();
 const record={startedAt,completedAt:new Date().toISOString(),codeCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),workingTreeChanges:execFileSync('git',['status','--porcelain'],{cwd:root,encoding:'utf8'}).trim(),scope:'Fictional client demo; local UI simulations only. No operational API/RLS acceptance.',environment:'Windows Chrome headless, desktop 1440px, responsive 390/320px and Flutter 390px mobile emulation',results,pageErrors:errors,physicalIPhone:'Not run',nativeIPhone:'Not run',userAcceptance:'Pending'};
 const file=path.join(root,'docs/testing/runs',startedAt.replace(/[:.]/g,'-')+'-demo-browsers.json');await fs.writeFile(file,JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify(record,null,2));if(results.some(r=>r.result==='Fail'))process.exitCode=1;
}
