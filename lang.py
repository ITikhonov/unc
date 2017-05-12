import pprint

class O:
	def __repr__(_):
		return 'O{'+str(_.__dict__)

S=O()
S.at = ''
S.pool = {}
S.fn = {}



def Wpool():
	p=O()
	p.name=word()
	p.size=word()
	p.type=word()
	S.pool[p.name]=p

def WS():
	S.source=S.source.split('\n',1)[1]

def Wfn():
	p=O()
	p.name=word()
	p.regs={}
	p.types = {}
	p.body=[]

	S.current=p
	S.fn[p.name]=p

def Wlit():
	r=word()
	value=word()

	register(r)
	S.current.body.append(('lit',r,value))


def Wmul():
	simple('mul rrr')
	
def Wmod():
	a=word()
	b=word()
	r=word()
	register(a,b,r)
	append('mod',a,b,r)

def Wend():
	S.current = None


def Wfetch():
	name=word()
	r=word()
	register(r)
	append('fetch',name,r)

def Wmov(): simple('mov rr')

def Wstore(): simple('store nr')
def Wstorei(): simple('storei nrr')
def Winc(): simple('inc r')
def Wlt(): simple('lt rrr')
def Wsize(): simple('size nr')
def Wloop(): simple('loop r')


def Wtype():
	r=word()
	type=word()
	register(r)
	S.current.types[r]=type


def simple(what):
	op,pat = what.split()
	instr = [op]
	for x in pat:
		if x == 'r':
			r=word()
			register(r)
			instr.append(r)
		elif x == 'n':
			n=word()
			instr.append(n)
		else:
			raise
	append(*instr)
	
	
def fncall(f):
	args=[]
	while not S.endline:
		r=word()
		args.append(r)

	append('fncall', f.name, *args)
	


def append(*args):
	S.current.body.append(args)

S.module=locals()


def builtins():
	for name,fn in S.module.items():
		if not name.startswith('W'): continue
		S.fn[name[1:]] = fn


def register(*regs):
	for r in regs:
		S.current.regs[r] = True



def call():
	f=S.fn[S.word]
	if hasattr(f,'name'):
		fncall(f)
	else:
		apply(f)


def report():
	S.source = S.source[:64]
	S.at = S.at[:64]
	print 'Line:',S.line.split('\n',1)[0]
	print 'At:',S.at.split('\n',1)[0]
	print
	print 'S:',S
	print

	for fn in S.fn.values():
		if hasattr(fn,'name'):
			print fn.name, fn.body



def strip():
	line = False
	for i in range(len(S.source)):
		c=S.source[i]
		if c in ' \t':
			continue
		if c in '\n;':
			S.line = S.source[1:]
			line = True
			continue
		break
		
	S.source=S.source[i:]
	S.at = S.source
	S.endline = line


def word():
	strip()
	for i in range(len(S.source)):
		c=S.source[i]
		if c in ' \n\t;':
			break

	S.word = S.source[:i]
	S.source=S.source[i:]
	strip()

	return S.word


def lang():
	builtins()

	S.source=open('example.2').read()
	S.line = S.source
	S.at = S.source
	try:
		while True:
			word()
			if S.word == '': break
			call()
	except:
		report()
		raise

lang()
pprint.pprint(S.pool)
for n,v in S.fn.items():
	if hasattr(v,'body'):
		pprint.pprint((n,v.regs.keys(),v.body))



