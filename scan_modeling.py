import subprocess, pathlib, re, json, collections, time
base=pathlib.Path(r'C:\Users\CAI BIN\Desktop\1')
out=base/'_work'; out.mkdir(exist_ok=True)
rg=r'C:\Users\CAI BIN\AppData\Local\OpenAI\Codex\bin\85e840bd9ad04c3b\rg.exe'
exclude=['Windows','WindowsApps','Program Files','Program Files (x86)','ProgramData','$Recycle.Bin','$RECYCLE.BIN','System Volume Information','texlive','node_modules','.git','.venv','venv','site-packages','anaconda3','miniconda3','.codex','.agents','.cache','Cache','Code Cache','GPUCache','Docker','DockerData','WSL','CodexData','CodexRepairBackup','CodexRepairTemp','CodexStableProfile','mingw64','Tencent Games','miHoYo Launcher','WpSystem','Driver']
allp=[]; errors=[]; stats={}
for root in ['C:\\','D:\\']:
    args=[rg,'--files','--hidden','--no-ignore','--no-messages']
    for x in exclude: args+=['-g','!**/'+x+'/**']
    args += ['-g','!**/AppData/Local/Packages/**','-g','!**/AppData/Local/Programs/**','-g','!**/AppData/Local/Microsoft/**','-g','!**/AppData/Local/Google/**','-g','!**/AppData/Local/OpenAI/**','-g','!**/AppData/Roaming/Code/**',root]
    r=subprocess.run(args,capture_output=True,encoding='utf-8',errors='replace')
    pp=r.stdout.splitlines(); allp+=pp; stats[root]={'paths':len(pp),'exit_code':r.returncode}
pathlib.Path(out/'all_paths.txt').write_text('\n'.join(allp),encoding='utf-8')
pattern=re.compile(r'数学建模|数模|统计建模|美赛|国赛|建模竞赛|建模比赛|CUMCM|MCM.?ICM|202[4-7].*[ABCDEＦF]题|[ABCDEF]题.*(?:202[4-7]|项目|论文)|翔宇杯|华数杯|Math.?Model|math_model|modeling|modelling',re.I)
matches=[p for p in allp if pattern.search(p)]
(out/'matches.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'scan_stats.json').write_text(json.dumps({'scanned':stats,'excluded_names':exclude,'matched':len(matches)},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'scanned':stats,'matched':len(matches)},ensure_ascii=False))
docs=[p for p in matches if pathlib.Path(p).suffix.lower() in ['.pdf','.docx','.doc','.tex','.md','.zip','.rar','.7z']]
print('\n'.join(docs[:230]))
print('TOP PARENTS',collections.Counter(str(pathlib.Path(p).parent) for p in matches).most_common(25))
