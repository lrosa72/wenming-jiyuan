import re, glob
for f in ["/workspace/网文创作/正文存稿/第103章-路走多宽.md","/workspace/网文创作/正文存稿/第104章-第一封异族信.md","/workspace/网文创作/正文存稿/第105章-废石山的邻居.md","/workspace/网文创作/正文存稿/第106章-弯钩的影子.md"]:
    c=open(f,encoding='utf-8').read()
    m=re.search(r'^📊 章节元数据',c,re.M)
    body=c[:m.start()] if m else c
    body=re.sub(r'^# .+\n','',body); body=re.sub(r'^> \*.*\n','',body)
    body=re.sub(r'> 🎵[^\n]*\n(?:> [^\n]*\n?)*','',body)
    n=len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]',body))
    bad=[]
    if not (2800<=n<=3200): bad.append(f"LEN {n}")
    if '\ufffd' in c: bad.append("FFFD")
    if re.search(r'不是.{0,20}是',body): bad.append("BUSHI")
    if bad: print("FAIL",f,bad)
    else: print("OK",f,n)
