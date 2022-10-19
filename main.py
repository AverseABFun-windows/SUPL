import sys,math,struct

class Scope:
	def __init__(self, parent, func, name):
		self.parent = parent
		self.children = []
		self.func = func
		self.name = name
		if parent != None:
			parent.children.append(self)

gs=Scope(None, lambda : None, "global")

suplfuncs = {"OUT":[
	gs,
	lambda s : print(globals().__getitem__(s.replace("~\\","").strip())) 
	if s.startswith("~\\") 
	else print(s), 
	"OUT"], "IN":[
	gs,
	lambda n,s : globals().__setitem__(n,input(s)), "IN"], "VAR":[
	gs,
	lambda n,d : globals().__setitem__(n,d),"VAR"
], "IF":[
	gs,
	lambda c,f,e : clparse([f.replace("'","\"")]) 
	if eval(c) 
	else clparse([e.replace("'","\"")]), 
"IF"]}

def clparse(data: list,name:str):
	tmp = []
	for i in data:
		for f in gs.children:
			#print(i)
			if i.startswith(f.name):
				tmp = i.replace(f.name,"")
				tmp = tmp.split(" ")
				inStr = False
				sts = [""]
				del tmp[0]
				for g in tmp:
					if g.endswith("\"") and inStr:
						sts[-1] = sts[-1]+g.replace("\"","").strip()
						inStr = False
					if inStr:
						sts[-1] = sts[-1]+g+" "
					if g.startswith("\"") and not inStr:
						inStr = True
						sts.append(g.replace("\"","")+" ")
				del sts[0]
				sts = sts[0]
				sts.strip()
				f.func(*sts.split(","))
		if i.startswith("IMPORT "):
			if not " FROM " in i:
				print("ERR: IMPORT STATEMENT {} INVALID".format(i))
				exit(1)
			tmp = i.replace("IMPORT ","")
			tmp = tmp.replace("FROM ","")
			tmp = tmp.split(" ")
			t = tmp[0].split(",")
			f = tmp[1]
			if f == "supl":
				for s in t:
					if s in suplfuncs:
						Scope(*suplfuncs[s])
					else:
						if s=="*":
							for k in suplfuncs:
								gs.children.append(Scope(*suplfuncs[k]))
						else:
							print("ERR: INVALID IMPORT {}".format(s))
							exit(1)


lgasm = {"MOV":0b1000,"ARH":0b1001,"LOG":0b1010}
def decBinary(arr, n):
    k = int(math.log2(n))
    while (n > 0):
        arr[k] = n % 2
        k = k - 1
        n = n//2
def binaryDec(arr, n):
    ans = 0
    for i in range(0, n):
        ans = ans + (arr[i] << (n - i - 1))
    return ans
def concat(m, n):
    k = int(math.log2(m)) + 1
    l = int(math.log2(n)) + 1
    a = [0 for i in range(0, k)]
    b = [0 for i in range(0, l)]
    c = [0 for i in range(0, k + l)]
    decBinary(a, m);
    decBinary(b, n);
    iin = 0
    for i in range(0, k):
        c[iin] = a[i]
        iin = iin + 1
    for i in range(0, l):
        c[iin] = b[i]
        iin = iin + 1
    return (binaryDec(c, k + l))

def lgcasm(data: list, name:str):
	tmp = []
	ttmp = []
	out = []
	for k in lgasm:
		gs.children.append(Scope(gs,lgasm[k],k))
	for i in data:
		for f in gs.children:
			#print(i)
			if i.startswith(f.name):
				tmp = i.replace(f.name,"")
				tmp = tmp.split(" ")
				del tmp[0]
				#del sts[0]
				tmp = tmp[0].split(",")
				for i in tmp:
					try:
						ttmp.append(int(i))
					except Exception:
						if i=="A":
							ttmp.append(1)
						if i=="B":
							ttmp.append(2)
						if i=="C":
							ttmp.append(3)
						if i=="D":
							ttmp.append(4)
						if i=="E":
							ttmp.append(5)
						if i=="F":
							ttmp.append(6)
						if i=="P":
							ttmp.append(7)
						if i=="R":
							ttmp.append(8)
				
				tmp = ttmp
				k = 19 - (int(math.log2(tmp[0])) + 1)
				v = 19 - (int(math.log2(tmp[1])) + 1)
				out.append(
					bin(concat(concat(
						f.func,concat(
							int("1"+("0"*k),2),
						tmp[0])),
							   concat(
							int("1"+("0"*v),2),
						tmp[1])
					)
					).replace("0b","")
				)
	out = "".join(out)
	outs = []
	t = False
	for i in out:
		if t==False:
			outs.append(i)
			t = True
		else:
			outs[-1] = int(outs[-1]+i)
			t = False
	file = open(name+".bgc",mode="bw", buffering=0)
	for i in outs:
		file.write(struct.pack('>H',i))
	file.close()
	file = open(name+".tgc",mode="w")
	file.write(out)

supltypes = {"cmdline":clparse, "asm":lgcasm}



def run(file, gc=Scope(None, lambda : None, "global"), *args):
	global gs
	gs = gc
	name = file
	file = open(file)
	dta = file.readlines()
	if not dta[0].startswith("TYPE "):
		print("ERR: TYPE OF PROGRAM NOT DEFINED")
		exit(1)

	data = []
	for i in dta:
		data.append(i.replace("\n",""))

	i = data[0].replace("TYPE ","")
	i = i.split(':')
	if i[0] == "supl":
		if i[1] in supltypes:
			del data[0]
			r = supltypes[i[1]]
			r(data,name.replace(".supl",""))
		else:
			print("ERR: INVALID TYPE {}".format(i[1]))
			exit(1)
	else:
		run(i[0]+".supl",gs=gs,*i)

run(sys.argv[1])