import pprint

class O:
	def __repr__(_):
		return 'O{'+str(_.__dict__)

S=O()
S.at = ''
S.pool = {}
S.fn = {}
S.c_op = {}
S.annex = O()
S.annex.body=[]
S.pro = O()
S.pro.body=[]


def Cc(op, line):
	c_output(line+'\n')


def Clit(op,v,r):
	s='\t{}[0]={};\n'.format(r,v)
	c_output(s)


def Csize(op,pool,r):
	size=S.pool[pool].size
	s='\t{}[0]={};\n'.format(r,size)
	c_output(s)

def Cloop(op,r):
	s='\tfor({}[0]=1;{}[0];) '.format(r,r)
	c_output(s)

def Cfncall(op, func, *args):
	rs=[]
	for r in args:
		s='{}'.format(r)
		rs.append(s)

	sa=','.join(rs)
	s='\t{}({});\n'.format(func,sa)
	c_output(s)

def Cmul(op,a,b,r):
	s='\t{}[0]={}[0]*{}[0];\n'.format(r,a,b)
	c_output(s)

def Cmod(op,a,b,r):
	s='\t{}[0]={}[0]%{}[0];\n'.format(r,a,b)
	c_output(s)

def Cinc(op,r):
	s='\t{}[0]++;\n'.format(r)
	c_output(s)

def Clt(op,a,b,r):
	s='\t{}[0]={}[0]<{}[0];\n'.format(r,a,b)
	c_output(s)

def Cmov(op,s,d):
	s='\t{}[0]={}[0];\n'.format(d,s)
	c_output(s)

def Cstorei(op,name,r,i):
	s='\t{}[{}[0]]={}[0];\n'.format(name,i,r)
	c_output(s)

def Cstore(op,name,r):
	s='\t{}[0]={}[0];\n'.format(name,r)
	c_output(s)

def Cfetchi(op,name,r,i):
	s='\t{}[0]={}[{}[0]];\n'.format(r,name,i)
	c_output(s)

def Cfetch(op,name,r):
	s='\t{}[0]={}[0];\n'.format(r,name)
	c_output(s)


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
	p.locals={}
	p.types = {}
	p.body=[]

	S.current=p
	S.fn[p.name]=p

def Wc():
	line, S.source=S.source.split('\n',1)
	append('c',line)

def Wanx():
	line, S.source=S.source.split('\n',1)
	S.annex.body.append(('c',line))

def Wpro():
	line, S.source=S.source.split('\n',1)
	S.pro.body.append(('c',line))

def Wlit():
	simple('lit nr')


def Wmul(): simple('mul r')
def Wmod(): simple('mod r')
def Wend(): S.current = None
def Wfetch(): simple('fetch nr')
def Wfetchi(): simple('fetchi nr')
def Wmov(): simple('mov r')
def Wstore(): simple('store nr')
def Wstorei(): simple('storei nr')
def Winc(): simple('inc r')
def Wlt(): simple('lt r')
def Wsize(): simple('size nr')
def Wloop(): simple('loop r')


def Wtype():
	type=word()
	r=word()
	register(r)
	S.current.types[r]=type


def simple(what):
	op,pat = what.split()
	instr = [op]

	if pat.startswith('n'):
		n=word()
		print what, n
		instr.append(n)
		pat=pat[1:]

	if pat!='r': raise

	s=word()
	for r in s:
		register(r)
		instr.append(r)
	append(*instr)
	
	
def fncall(name):
	r=word()
	append('fncall', name, *r)
	


def append(*args):
	S.current.body.append(args)

S.module=locals()


def builtins():
	for name,fn in S.module.items():
		if not name.startswith('W'): continue
		S.fn[name[1:]] = fn

	for name,fn in S.module.items():
		if not name.startswith('C'): continue
		S.c_op[name[1:]] = fn


def register(*regs):
	for r in regs:
		if r.islower():
			S.current.regs[r] = True
		else:
			S.current.locals[r] = True



def call():
	f=S.fn.get(S.word)
	if f is None or hasattr(f,'name'):
		fncall(S.word)
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


def parse():
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

def c_output(s):
	S.c_file.write(s)

def c_pools():
	for p in S.pool.values():
		s="{} {}[{}];\n".format(p.type,p.name,p.size)
		c_output(s)

def c_decl_args(fn):
	args=[]
	for p in sorted(fn.regs):
		type = fn.types.get(p,'uint64_t')
		args.append('{} {}[1]'.format(type,p))
	s=','.join(args)
	c_output(s)


def c_decl_locals(fn):
	for p in sorted(fn.locals):
		type = fn.types.get(p,'uint64_t')
		c_output('\t{} {}[1];\n'.format(type,p))


def c_decl_body(fn):
	S.c_current_i=0
	while True:
		if S.c_current_i==len(fn.body): break
		op=fn.body[S.c_current_i]

		f=S.c_op.get(op[0])

		if f is None:
			s='Compiler for {} not found'.format(op)
			raise Exception(s)

		S.c_current = fn
		try:
			apply(f,op)
		except:
			print 'Error at:',op
			raise

		S.c_current_i+=1
		

def c_declarations():
	args=[]
	for p in S.fn.values():
		if not hasattr(p,'body'): continue
		s="void {}(".format(p.name)
		c_output(s)
		c_decl_args(p)
		c_output(');\n')


def c_functions():
	args=[]
	for p in S.fn.values():
		if not hasattr(p,'body'): continue

		s="void {}(".format(p.name)
		c_output(s)
		c_decl_args(p)
		c_output(') {\n')
		c_decl_locals(p)
		c_decl_body(p)
		c_output('}\n\n')

def compile():
	S.c_file=open('test.c','w')
	c_output('#include <stdint.h>\n')

	c_decl_body(S.pro)
	c_pools()
	c_declarations()
	c_functions()
	c_decl_body(S.annex)



parse()
pprint.pprint(S.pool)
for n,v in S.fn.items():
	if hasattr(v,'body'):
		pprint.pprint((n,v.regs.keys(),v.body))


compile()



