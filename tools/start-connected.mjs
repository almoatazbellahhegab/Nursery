/** Launch only the project's connected API and compiled clients, keeping secrets in child env. */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {root,nodeRuntime} from './client-runtime.mjs';

const runtime=JSON.parse(fs.readFileSync(path.join(root,'.tools/database-runtime.json'),'utf8'));
const addresses=Object.entries(os.networkInterfaces()).filter(([name])=>!/virtual|vethernet|wsl|vmware|docker/i.test(name)).flatMap(([,items])=>(items??[]).filter(item=>item.family==='IPv4'&&!item.internal).map(item=>item.address));
const hosts=['localhost','127.0.0.1',...addresses];
const origins=hosts.flatMap(host=>[3000,3200,3300,3400].map(port=>`http://${host}:${port}`));
const env={...process.env,NURSERY_DATABASE_URL:runtime.dev_url,NURSERY_ENV:'local',NURSERY_ORIGINS:origins.join(','),NURSERY_MOBILE_PORT:'3400'};
const children=[
  spawn(path.join(root,'services/api/.venv/Scripts/python.exe'),['-m','uvicorn','nursery_api.main:app','--host','0.0.0.0','--port','8000'],{cwd:path.join(root,'services/api'),env,stdio:'inherit',windowsHide:true}),
  spawn(nodeRuntime(),[path.join(root,'apps/admin-web/node_modules/next/dist/bin/next'),'start','--hostname','0.0.0.0','--port','3300'],{cwd:path.join(root,'apps/admin-web'),env,stdio:'inherit',windowsHide:true}),
  spawn(nodeRuntime(),[path.join(root,'tools/serve-mobile.mjs')],{cwd:root,env,stdio:'inherit',windowsHide:true}),
];
let stopping=false;
function stop(){if(stopping)return;stopping=true;for(const child of children)child.kill();process.stdin.destroy();}
process.stdin.on('data',data=>{if(data.toString().trim()==='stop')stop();});
process.on('SIGINT',stop);process.on('SIGTERM',stop);
for(const child of children){child.on('error',error=>{console.error(error.message);stop();process.exitCode=1;});child.on('exit',code=>{if(!stopping){stop();process.exitCode=code??1;}});}
console.log('Connected workspace: http://localhost:3300');
console.log(`Mobile workspace: http://${addresses[0]??'localhost'}:3400`);
console.log('Credentials remain in ignored .tools/dev-accounts.json. No credential values are printed.');
