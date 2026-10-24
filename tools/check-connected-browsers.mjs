/** Real web/Flutter/PostgreSQL staff journey. Credential values are never logged. */
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {root} from './client-runtime.mjs';

const require=createRequire(import.meta.url);
const {chromium}=require(path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const accounts=JSON.parse(await fs.readFile(path.join(root,'.tools/dev-accounts.json'),'utf8'));
function safe(value){let text=String(value);for(const password of Object.values(accounts))text=text.replaceAll(password,'[redacted]');return text;}
const startedAt=new Date().toISOString();const results=[];
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--enable-unsafe-swiftshader']});
const web=await browser.newPage({viewport:{width:1440,height:1000}});
const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
const webBase='http://localhost:3300',mobileBase='http://localhost:3400';
const output=path.join(root,'test-results');await fs.mkdir(output,{recursive:true});
async function check(id,action){try{await action();results.push({id,result:'Pass'});console.log(`${id}: Pass`);}catch(error){const detail=safe(error.message);results.push({id,result:'Fail',detail});console.log(`${id}: Fail — ${detail}`);}}
async function signIn(page,role){
  const email=`${role}@garden.example.test`;
  await page.getByLabel('Email',{exact:true}).fill(email);
  await page.getByLabel('Password',{exact:true}).fill(accounts[email]);
  await page.getByRole('button',{name:'Sign in',exact:true}).click();
  await page.getByRole('heading',{name:'Staff attendance',exact:true}).waitFor({timeout:30000});
}
function teacherCard(){return web.locator('.workspace-roster article').filter({has:web.getByRole('heading',{name:'Teacher Demo',exact:true})});}
try{
  await check('CONNECTED-WEB-SIGNIN-AND-PERSIST',async()=>{
    await web.goto(webBase);
    await signIn(web,'teacher');
    const card=teacherCard();await card.waitFor();
    const out=card.getByRole('button',{name:'Check out',exact:true});
    if(await out.isVisible()){await out.click();await card.getByRole('button',{name:'Check in',exact:true}).waitFor();}
    await card.getByRole('button',{name:'Check in',exact:true}).click();
    await card.getByRole('button',{name:'Check out',exact:true}).waitFor();
    await web.reload();
    await teacherCard().getByRole('button',{name:'Check out',exact:true}).waitFor({timeout:30000});
    await web.screenshot({path:path.join(output,'connected-web-staff-en.png'),fullPage:true});
  });
  await check('CONNECTED-FLUTTER-SHARED-STATE',async()=>{
    await mobile.goto(mobileBase);
    const placeholder=mobile.locator('flt-semantics-placeholder');
    await placeholder.waitFor({timeout:45000});await placeholder.evaluate(element=>element.click());
    await mobile.getByRole('textbox',{name:'Email',exact:true}).waitFor({timeout:30000});
    const email='teacher@garden.example.test';
    await mobile.getByRole('textbox',{name:'Email',exact:true}).click();
    await mobile.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await mobile.keyboard.type(email,{delay:40});
    await mobile.getByLabel('Password',{exact:true}).click();
    await mobile.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await mobile.keyboard.type(accounts[email],{delay:40});
    await mobile.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await mobile.getByRole('button',{name:'Sign in',exact:true}).click();
    await mobile.getByRole('button',{name:'Check out',exact:true}).waitFor({timeout:30000});
    await mobile.screenshot({path:path.join(output,'connected-mobile-staff-en.png'),fullPage:true});
    await mobile.getByRole('button',{name:'Check out',exact:true}).click();
    await mobile.getByRole('button',{name:'Check in',exact:true}).waitFor({timeout:30000});
    await web.getByRole('button',{name:'Refresh',exact:true}).click();
    await teacherCard().getByRole('button',{name:'Check in',exact:true}).waitFor();
  });
  await check('CONNECTED-MANAGER-CORRECTION-AND-REPORT',async()=>{
    await web.getByRole('button',{name:'Sign out',exact:true}).click();
    await signIn(web,'branch_manager');
    assert.equal(await web.getByRole('combobox').first().locator('option').count(),1);
    await teacherCard().getByRole('button',{name:'History',exact:true}).click();
    await web.getByRole('heading',{name:'Correct a time',exact:true}).waitFor();
    const me=await (await web.request.get(webBase+'/api/v1/auth/me')).json();
    const employees=await (await web.request.get(webBase+'/api/v1/staff-attendance/employees?branch_id='+me.branches[0].id)).json();
    const employee=employees.items.find(item=>item.display_name==='Teacher Demo');
    const history=await (await web.request.get(webBase+`/api/v1/staff-attendance/history?branch_id=${me.branches[0].id}&employee_id=${employee.id}`)).json();
    const event=history.events.at(-1);assert.equal(event.action,'check_out');
    await web.getByLabel('Record',{exact:true}).selectOption(event.id);
    const corrected=new Date(new Date(event.effective_at).getTime()+1000).toISOString();
    const local=await web.evaluate(value=>{const date=new Date(value);date.setMinutes(date.getMinutes()-date.getTimezoneOffset());return date.toISOString().slice(0,19);},corrected);
    await web.getByLabel('Correct time (your device timezone)',{exact:true}).fill(local);
    await web.getByLabel('Reason',{exact:true}).fill('Confirmed against the staff register');
    await web.getByRole('button',{name:'Save correction',exact:true}).click();
    await web.getByText('Correction saved; the original is retained.',{exact:true}).waitFor();
    await web.getByText('Confirmed against the staff register',{exact:false}).first().waitFor();
    await web.getByRole('button',{name:'Daily report',exact:true}).click();
    await web.getByRole('heading',{name:'Daily presence',exact:false}).waitFor();
    await web.screenshot({path:path.join(output,'connected-web-correction.png'),fullPage:true});
  });
  await check('CONNECTED-ARABIC-AND-PARENT-DENIAL',async()=>{
    await mobile.getByRole('button',{name:'العربية',exact:true}).click();
    await mobile.getByRole('button',{name:'English',exact:true}).waitFor();
    assert.match(await mobile.locator('body').ariaSnapshot(),/التقرير اليومي/);
    await mobile.screenshot({path:path.join(output,'connected-mobile-staff-ar.png'),fullPage:true});
    await web.getByRole('button',{name:'العربية',exact:true}).click();
    assert.equal(await web.locator('html').getAttribute('dir'),'rtl');
    await web.getByRole('heading',{name:'حضور الموظفين',exact:true}).waitFor();
    await web.screenshot({path:path.join(output,'connected-web-staff-ar.png'),fullPage:true});
    await web.getByRole('button',{name:'English',exact:true}).click();
    await web.getByRole('button',{name:'Sign out',exact:true}).click();
    const email='parent@garden.example.test';
    await web.getByLabel('Email',{exact:true}).fill(email);await web.getByLabel('Password',{exact:true}).fill(accounts[email]);
    await web.getByRole('button',{name:'Sign in',exact:true}).click();
    await web.getByRole('heading',{name:'This account does not have staff workspace access.',exact:true}).waitFor();
    assert.equal((await web.request.get(webBase+'/api/v1/staff-attendance/employees?branch_id=00000000-0000-0000-0000-000000000000')).status(),403);
  });
}finally{
  await fs.writeFile(path.join(output,'connected-mobile-aria.txt'),safe(await mobile.locator('body').ariaSnapshot().catch(()=>'')));
  await browser.close();
}
const record={startedAt,completedAt:new Date().toISOString(),codeCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),result:results.every(item=>item.result==='Pass')?'Pass':'Fail',results,scope:'Real compiled Next.js and Flutter web against PostgreSQL-backed API; Windows Chrome plus mobile emulation',physicalIPhone:'Not run',nativeIPhone:'Not run',userAcceptance:'Pending'};
const file=path.join(root,'docs/testing/runs',startedAt.replace(/[:.]/g,'-')+'-connected-browsers.json');await fs.writeFile(file,JSON.stringify(record,null,2)+'\n');console.log(`Evidence: ${file}`);
if(record.result!=='Pass')process.exitCode=1;
