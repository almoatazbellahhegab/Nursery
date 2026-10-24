/** Connected branch UI integration. Synthetic local accounts; no credential logging. */
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
const base='http://localhost:3300';
const branchName='Fictional Riverside '+Date.now();
const mobileName='Fictional Orchard '+Date.now();
let branchId;
async function check(id,action){try{await action();results.push({id,result:'Pass'});console.log(`${id}: Pass`);}catch(error){const detail=safe(error.message);results.push({id,result:'Fail',detail});console.log(`${id}: Fail — ${detail}`);}}
async function signIn(page,role){const email=`${role}@garden.example.test`;await page.goto(base);await page.getByLabel('Email',{exact:true}).fill(email);await page.getByLabel('Password',{exact:true}).fill(accounts[email]);await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByRole('heading',{name:'Staff attendance',exact:true}).waitFor();}
async function typeMobile(label,value){await mobile.getByLabel(label,{exact:true}).click();await mobile.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await mobile.keyboard.type(value,{delay:40});}
try{
  await check('BRANCH-WEB-CREATE-ASSIGN-DEACTIVATE',async()=>{
    await signIn(web,'administrator');
    await web.getByRole('button',{name:'Manage branches',exact:true}).click();
    await web.getByLabel('Branch name',{exact:true}).fill(branchName);
    await web.getByLabel('Branch email',{exact:true}).fill('office@example.test');
    await web.getByLabel('Capacity context',{exact:true}).fill('65');
    await web.getByRole('button',{name:'Save branch',exact:true}).click();
    await web.getByText('Branch saved.',{exact:true}).waitFor();
    const rows=await (await web.request.get(base+'/api/v1/branches')).json();
    const branch=rows.items.find(row=>row.name===branchName);assert.equal(branch.capacity,65);branchId=branch.id;
    const members=await (await web.request.get(base+'/api/v1/branches/members')).json();
    const manager=members.items.find(row=>row.email==='branch_manager@garden.example.test');
    await web.getByLabel('Organization member',{exact:true}).selectOption(manager.user_id);
    await web.getByRole('button',{name:'Assign branch',exact:true}).click();
    await web.getByText('Assignment saved. Access uses the current assignment.',{exact:true}).waitFor();
    await web.getByLabel('Active for new records',{exact:true}).uncheck();
    await web.getByRole('button',{name:'Save branch',exact:true}).click();
    await web.getByText('Branch saved.',{exact:true}).waitFor();
    const saved=await (await web.request.get(base+'/api/v1/branches/'+branchId)).json();
    assert.equal(saved.active,false);assert.equal(saved.version,3);
    await web.screenshot({path:path.join(root,'test-results/branch-web-en.png'),fullPage:true});
  });
  await check('BRANCH-MANAGER-CURRENT-SCOPE',async()=>{
    const manager=await browser.newPage();
    try{await signIn(manager,'branch_manager');
      const row=await (await manager.request.get(base+'/api/v1/branches/'+branchId)).json();
      assert.equal(row.name,branchName);assert.equal(row.active,false);
      assert.equal(await manager.getByRole('button',{name:'Manage branches',exact:true}).count(),0);
      const members=await (await web.request.get(base+'/api/v1/branches/members')).json();
      const member=members.items.find(row=>row.email==='branch_manager@garden.example.test');
      await web.getByLabel('Organization member',{exact:true}).selectOption(member.user_id);
      await web.getByRole('button',{name:'Remove branch access',exact:true}).click();
      await web.getByText('Assignment saved. Access uses the current assignment.',{exact:true}).waitFor();
      assert.equal((await manager.request.get(base+'/api/v1/branches/'+branchId)).status(),404);
    }finally{await manager.close();}
  });
  await check('BRANCH-FLUTTER-CREATE-WEB-PERSISTENCE',async()=>{
    await mobile.goto('http://localhost:3400');
    const placeholder=mobile.locator('flt-semantics-placeholder');await placeholder.waitFor({timeout:45000});await placeholder.evaluate(element=>element.click());
    await mobile.getByLabel('Email',{exact:true}).waitFor();
    await typeMobile('Email','administrator@garden.example.test');await typeMobile('Password',accounts['administrator@garden.example.test']);
    await mobile.getByRole('button',{name:'Sign in',exact:true}).click();
    await mobile.getByRole('button',{name:'Manage branches',exact:true}).click({timeout:30000});
    await mobile.getByRole('button',{name:'New branch',exact:true}).click();
    await typeMobile('Branch name',mobileName);
    await mobile.getByRole('button',{name:'Save branch',exact:true}).click();
    const created=mobile.getByRole('group',{name:new RegExp(mobileName)}).first();
    for(let attempt=0;attempt<12 && !await created.isVisible();attempt++){await mobile.mouse.move(200,600);await mobile.mouse.wheel(0,400);await mobile.waitForTimeout(150);}
    await created.waitFor();
    const rows=await (await web.request.get(base+'/api/v1/branches')).json();assert.ok(rows.items.some(row=>row.name===mobileName));
    await mobile.screenshot({path:path.join(root,'test-results/branch-mobile-en.png'),fullPage:true});
    await web.reload();await web.getByRole('button',{name:'Manage branches',exact:true}).click();
    await web.getByRole('button',{name:mobileName,exact:true}).waitFor();
  });
  await check('BRANCH-FLUTTER-ARABIC',async()=>{
    await mobile.getByRole('button',{name:'Back',exact:true}).click();
    await mobile.getByRole('button',{name:'العربية',exact:true}).click();
    await mobile.getByRole('button',{name:'إدارة الفروع',exact:true}).click();
    await mobile.getByRole('heading',{name:'الفروع',exact:true}).waitFor();
    await mobile.getByRole('button',{name:'فرع جديد',exact:true}).click();
    await mobile.getByLabel('اسم الفرع',{exact:true}).waitFor();
    await mobile.getByRole('button',{name:'حفظ الفرع',exact:true}).waitFor();
    await mobile.screenshot({path:path.join(root,'test-results/branch-mobile-ar.png'),fullPage:true});
  });
  await check('BRANCH-WEB-ARABIC',async()=>{
    await web.getByRole('button',{name:'العربية',exact:true}).click();
    assert.equal(await web.locator('html').getAttribute('dir'),'rtl');
    await web.getByRole('heading',{name:'الفروع',exact:true}).waitFor();
    await web.getByRole('button',{name:mobileName,exact:true}).click();
    await web.getByLabel('عضو المؤسسة',{exact:true}).waitFor();
    await web.getByLabel('حالة التشغيل',{exact:true}).waitFor();
    await web.screenshot({path:path.join(root,'test-results/branch-web-ar.png'),fullPage:true});
  });
}finally{await mobile.screenshot({path:path.join(root,'test-results/branch-mobile-last.png'),fullPage:true}).catch(()=>{});await fs.writeFile(path.join(root,'test-results/branch-mobile-aria.txt'),safe(await mobile.locator('body').ariaSnapshot().catch(()=>'')));await browser.close();}
const record={startedAt,completedAt:new Date().toISOString(),codeCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),result:results.every(item=>item.result==='Pass')?'Pass':'Fail',results,scope:'Compiled Next.js and Flutter web branch management against real PostgreSQL; Windows Chrome and mobile emulation',physicalIPhone:'Not run',nativeIPhone:'Not run',userAcceptance:'Pending'};
const file=path.join(root,'docs/testing/runs',startedAt.replace(/[:.]/g,'-')+'-branch-browsers.json');await fs.writeFile(file,JSON.stringify(record,null,2)+'\n');console.log(`Evidence: ${file}`);
if(record.result!=='Pass')process.exitCode=1;
