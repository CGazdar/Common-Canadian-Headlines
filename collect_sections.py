import subprocess, sys
ids = "standardfreeholder thespec thewhig lfpress niagarafallsreview nugget owensoundsuntimes peterboroughexaminer pentictonherald timescolonist brandonsun acadienouvelle intelligencer brantfordexpositor recorder reddeeradvocate chathamdailynews vocm yukonnews whitehorsestar".split()
out = []
for o in ids:
    r = subprocess.run([sys.executable, "url_sections.py", o], capture_output=True, text=True)
    out.append(f"=== {o}\n{r.stdout}{r.stderr}")
    print("done", o, flush=True)
open("url_sections_nov.txt", "w", encoding="utf-8").write("\n".join(out))
print("Wrote url_sections_nov.txt with", sum(s.count(chr(10)) for s in out), "lines")
