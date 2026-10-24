/** Real MFA enrollment and cross-client verification; no secret screenshots/logs. */
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {root} from './client-runtime.mjs';
const python=path.join(root,'services/api/.venv/Scripts/python.exe');
execFileSync(python,[path.join(root,'tools/setup-security-fixture.py')],{cwd:root,encoding:'utf8'});
const require=createRequire(import.meta.url);
const {chromium}=require(path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const accounts=JSON.parse(await fs.readFile(path.join(root,'.tools/security-accounts.json'),'utf8'));
const sensitive=new Set(Object.values(accounts));
function safe(value){let text=String(value);for(const secret of sensitive)text=text.replaceAll(secret,'[redacted]');return text;}
function otp(secret,offset=0){return execFileSync(python,['-c','import sys,time,pyotp;print(pyotp.TOTP(sys.stdin.read()).at(time.time()+int(sys.argv[1])))',String(offset)],{input:secret,encoding:'utf8'}).trim();}
const startedAt=new Date().toISOString();const results=[];
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--enable-unsafe-swiftshader']});
const web=await browser.newPage({viewport:{width:1440,height:1000}});
const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
const base='http://localhost:3300';const email='security@garden.example.test';
let secret;let recovery=[];
async function check(id,action){try{await action();results.push({id,result:'Pass'});console.log(`${id}: Pass`);}catch(error){const detail=safe(error.message);results.push({id,result:'Fail',detail});console.log(`${id}: Fail — ${detail}`);}}
async function webLogin(){await web.getByLabel('Email',{exact:true}).fill(email);await web.getByLabel('Password',{exact:true}).fill(accounts[email]);await web.getByRole('button',{name:'Sign in',exact:true}).click();}
async function typeMobile(label,value){await mobile.getByLabel(label,{exact:true}).click();await mobile.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await mobile.keyboard.type(value,{delay:40});}
try{
  await check('MFA-WEB-ENROLL-AND-ACKNOWLEDGE-RECOVERY',async()=>{
    await web.goto(base);await webLogin();
    await web.getByRole('button',{name:'Account security',exact:true}).click();
    await web.getByRole('button',{name:'Set up authenticator',exact:true}).click();
    const input=web.getByLabel('Setup key',{exact:true});await input.waitFor();secret=await input.inputValue();sensitive.add(secret);
    const code=otp(secret);sensitive.add(code);
    await web.getByLabel('Verification code',{exact:true}).fill(code);
    await web.getByRole('button',{name:'Verify code',exact:true}).click();
    await web.getByRole('heading',{name:'Save your recovery codes',exact:true}).waitFor();
    recovery=await web.locator('section.panel li code').allTextContents();assert.equal(recovery.length,10);recovery.forEach(value=>sensitive.add(value));
    assert.equal(await web.getByRole('button',{name:'Continue to workspace',exact:true}).isEnabled(),false);
    await web.getByLabel('I saved these codes securely',{exact:true}).check();
    await web.getByRole('button',{name:'Continue to workspace',exact:true}).click();
    await web.getByRole('button',{name:'Manage branches',exact:true}).waitFor();
  });
  await check('MFA-FLUTTER-CURRENT-AUTHENTICATOR',async()=>{
    await mobile.goto('http://localhost:3400');const placeholder=mobile.locator('flt-semantics-placeholder');await placeholder.waitFor({timeout:45000});await placeholder.evaluate(element=>element.click());
    await mobile.getByLabel('Email',{exact:true}).waitFor();await typeMobile('Email',email);await typeMobile('Password',accounts[email]);
    await mobile.getByRole('button',{name:'Sign in',exact:true}).click();
    await mobile.getByLabel('Verification code',{exact:true}).waitFor({timeout:30000});
    assert.equal(await mobile.getByRole('button',{name:'Manage branches',exact:true}).count(),0);
    const code=otp(secret,30);sensitive.add(code);await typeMobile('Verification code',code);
    await mobile.getByRole('button',{name:'Verify code',exact:true}).click();
    await mobile.getByRole('button',{name:'Manage branches',exact:true}).waitFor();
  });
  await check('MFA-WEB-RECOVERY-AND-USED-CODE-DENIAL',async()=>{
    await web.getByRole('button',{name:'Sign out',exact:true}).click();await webLogin();
    await web.getByLabel('Verification method',{exact:true}).selectOption('recovery');
    await web.getByLabel('Verification code',{exact:true}).fill(recovery[0]);await web.getByRole('button',{name:'Verify code',exact:true}).click();
    await web.getByRole('button',{name:'Manage branches',exact:true}).waitFor();
    await web.getByRole('button',{name:'Sign out',exact:true}).click();await webLogin();
    await web.getByLabel('Verification method',{exact:true}).selectOption('recovery');
    await web.getByLabel('Verification code',{exact:true}).fill(recovery[0]);await web.getByRole('button',{name:'Verify code',exact:true}).click();
    await web.getByRole('alert').filter({hasText:'Check the code.'}).waitFor();
    const denied=await web.request.get(base+'/api/v1/branches');assert.equal(denied.status(),403);
    await web.getByLabel('Verification code',{exact:true}).fill(recovery[1]);await web.getByRole('button',{name:'Verify code',exact:true}).click();
    await web.getByRole('button',{name:'Manage branches',exact:true}).waitFor();
  });
  await check('MFA-ARABIC-CONTROLS-BOTH-CLIENTS',async()=>{
    await web.getByRole('button',{name:'العربية',exact:true}).click();await web.getByRole('button',{name:'أمان الحساب',exact:true}).click();
    await web.getByLabel('طريقة التحقق',{exact:true}).waitFor();assert.equal(await web.locator('html').getAttribute('dir'),'rtl');
    await web.screenshot({path:path.join(root,'test-results/security-web-ar.png'),fullPage:true});
    await mobile.getByRole('button',{name:'العربية',exact:true}).click();await mobile.getByRole('button',{name:'أمان الحساب',exact:true}).click();
    await mobile.getByLabel('رمز التحقق',{exact:true}).waitFor();
    await mobile.screenshot({path:path.join(root,'test-results/security-mobile-ar.png'),fullPage:true});
  });
}finally{await browser.close();}
const record={startedAt,completedAt:new Date().toISOString(),codeCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),result:results.every(item=>item.result==='Pass')?'Pass':'Fail',results,scope:'Real TOTP enrollment, session-bound MFA, recovery and compiled Next.js/Flutter clients against PostgreSQL; synthetic dedicated account only',physicalIPhone:'Not run',nativeIPhone:'Not run',userAcceptance:'Pending'};
const file=path.join(root,'docs/testing/runs',startedAt.replace(/[:.]/g,'-')+'-security-browsers.json');await fs.writeFile(file,JSON.stringify(record,null,2)+'\n');console.log(`Evidence: ${file}`);
if(record.result!=='Pass')process.exitCode=1;
