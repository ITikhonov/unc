import sys
import pprint

UDP_PORT=7532

class O:
	def __repr__(_):
		return 'O{'+str(_.__dict__)

S=O()
S.pool = {}
S.fn = {}
S.macro = {}
S.band = {}
S.bundle = {}
S.c_op = {}
S.annex = O()
S.annex.body=[]
S.annex.module='main'
S.pro = O()
S.pro.body=[]
S.pro.module='main'
S.pack = {}

S.module = 'main'


def register_fn(fn):
	fn.module=S.module
	S.fn[fn.name+'@'+S.module]=fn

def find_fn(name):
	fn=S.fn.get(name)
	if not fn: return None
	return fn

def all_fns():
	return sorted(S.fn.values(), key=lambda fn: fn.name)
	


def c_name(name):
	return name.replace('-','_')

def Cc(op, line):
	c_output(line+'\n')


def Clit(op,v,r):
	s='\t{}[0]={};\n'.format(r,v)
	c_output(s)


def Csize(op,pool,r):
	size=S.pool[pool].size
	s='\t{}[0]={};\n'.format(r,size)
	c_output(s)

def Ctimes(op,rn,ri):
	s='\tfor({ri}[0]=0;{ri}[0]<{rn}[0];{ri}[0]++) '.format(ri=ri,rn=rn)
	c_output(s)

def Ctimesn(op,n,ri):
	s='\tfor({ri}[0]=0;{ri}[0]<{n};{ri}[0]++) '.format(ri=ri,n=n)
	c_output(s)

def Cloop(op,r):
	s='\tfor({}[0]=1;{}[0];) '.format(r,r)
	c_output(s)

def Cif(op,r):
	s='\tif({}[0]) '.format(r)
	c_output(s)

def Cfncall(op, func, *args):
	fn=find_fn(func)
	if not fn:
		fn=find_fn(func+'@'+S.c_module)
	if not fn:
		raise Exception('no function '+func)

	func=fn.c_name
	rs=[]
	for r in args:
		s='{}'.format(r)
		rs.append(s)

	sa=','.join(rs)
	s='\t{}({});\n'.format(func,sa)
	c_output(s)

def Cadd(op,a,b,r):
	s='\t{}[0]={}[0]+{}[0];\n'.format(r,a,b)
	c_output(s)

def Csub(op,a,b,r):
	s='\t{}[0]={}[0]-{}[0];\n'.format(r,a,b)
	c_output(s)

def Cmul(op,a,b,r):
	s='\t{}[0]={}[0]*{}[0];\n'.format(r,a,b)
	c_output(s)

def Cdiv(op,a,b,r):
	s='\t{}[0]={}[0]/{}[0];\n'.format(r,a,b)
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

def Ceq(op,a,b,r):
	s='\t{}[0]={}[0]=={}[0];\n'.format(r,a,b)
	c_output(s)

def Cret(op):
	s='\treturn;\n'
	c_output(s)

def Cmov(op,s,d):
	s='\t{}[0]={}[0];\n'.format(d,s)
	c_output(s)

def Cstorei(op,name,r,i):
	band=S.band.get(S.banded.get(name))
	bundle=S.bundle.get(S.bundled.get(name))
	p=S.pool.get(name)
	assert p
	assert not (band and bundle)
	if band:
		name=c_name(name)
		s='\t{}[{}[0]].{}={}[0];\n'.format(band.c_name,i,name,r)
		c_output(s)
	elif bundle:
		name=c_name(name)
		s='\t{}.{}[{}[0]]={}[0];\n'.format(bundle.c_name,name,i,r)
		c_output(s)
	else:
		name=c_name(name)
		s='\t{}[{}[0]]={}[0];\n'.format(p.c_name,i,r)
		c_output(s)

def Cfetchi(op,name,r,i):
	band=S.band.get(S.banded.get(name))
	bundle=S.bundle.get(S.bundled.get(name))
	p=S.pool.get(name)
	assert p
	assert not (band and bundle)
	if band:
		name=c_name(name)
		s='\t{}[0]={}[{}[0]].{};\n'.format(r,band.c_name,i,name)
		c_output(s)
	elif bundle:
		name=c_name(name)
		s='\t{}[0]={}.{}[{}[0]];\n'.format(r,bundle.c_name,name,i)
		c_output(s)
	else:
		name=c_name(name)
		s='\t{}[0]={}[{}[0]];\n'.format(r,p.c_name,i)
		c_output(s)

def Cfetch(op,name,r):
	name=c_name(name)
	s='\t{}[0]=pool_{}[0];\n'.format(r,name)
	c_output(s)

def Wmodule(name):
	S.module=name

def Wpool(name,type,size=1):
	p=O()
	p.name=name
	p.size=size
	p.type=type
	p.module=S.module
	assert p.name not in S.pool
	S.pool[p.name]=p

def Wpack(*bs):
	for b in bs:
		S.pack[b]=True

def Wband(name,*ps):
	p=O()
	p.name=name
	p.pools=ps
	p.module=S.module
	assert p.name not in S.band
	S.band[p.name]=p

def Wbundle(name,*ps):
	p=O()
	p.name=name
	p.pools=ps
	p.module=S.module
	assert p.name not in S.bundle
	S.bundle[p.name]=p

def WS():
	S.source=S.source.split('\n',1)[1]

def Wfn(name,args=None):
	p=O()
	p.name=name
	p.regs={}
	p.locals={}
	p.types = {}
	p.body=[]
	p.args=args if args else ''

	S.current=p
	register_fn(p)

def Wc():
	line, S.source=S.source.split('\n',1)
	append('c',line)

def Wanx():
	line, S.source=S.source.split('\n',1)
	S.annex.body.append(('c',line))

def Wpro():
	line, S.source=S.source.split('\n',1)
	S.pro.body.append(('c',line))

def Wlit(*_): simple()
def Wadd(*_): simple()
def Wsub(*_): simple()
def Wmul(*_): simple()
def Wdiv(*_): simple()
def Wmod(*_): simple()
def Wend(*_): S.current = None
def Wfetch(*_): simple()
def Wfetchi(*_): simple()
def Wmov(*_): simple()
def Wstore(*_): simple()
def Wstorei(*_): simple()
def Winc(*_): simple()
def Wlt(*_): simple()
def Weq(*_): simple()
def Wret(*_): simple()
def Wloop(*_): simple()
def Wif(*_): simple()
def Wtimes(*_): simple()
def Wtimesn(*_): simple()

def Weach(pool,regs):
	register(*regs)
	rn,ri=regs

	if '@' in pool:
		name,module=pool.split('@',1)
		pool_size='{}-size@{}'.format(name,module)
	else:
		pool_size=pool+'-size'

	append('fncall',pool_size,rn)
	append('times',rn,ri)


def Wtype(type,regs):
	type=type
	for r in regs:
		register(r)
		S.current.types[r]=type


def simple():
	if len(S.args)==0:
		append(S.word)
	elif len(S.args)==1:
		register(*S.args[0])
		append(S.word,*S.args[0])
	else:
		name,regs=S.args
		register(*regs)
		append(S.word,name,*regs)
		
	
	
def fncall(name):
	if len(S.args)==1:
		for r in S.args[0]:
			register(r)
		append('fncall', name, *S.args[0])
	elif len(S.args)==0:
		append('fncall', name)
	else:
		raise Exception(name)


def append(*args):
	S.current.body.append(args)

S.builtin_locals=locals()


def builtins():
	for name,fn in S.builtin_locals.items():
		if not name.startswith('W'): continue
		fn.name=name[1:]
		S.macro[fn.name]=fn

	for name,fn in S.builtin_locals.items():
		if not name.startswith('C'): continue
		S.c_op[name[1:]] = fn


def register(*regs):
	for r in regs:
		if r.islower():
			print 'Warning: old-style registers'
			report(True)
			S.current.locals[r] = True
		else:
			S.current.locals[r] = True



def call():
	m=S.macro.get(S.word)
	if m:
		apply(m,S.args)
		return

	fncall(S.word)


def lineno():
	l=len(S.line)
	pre=S.source_full[:-l]
	return len(pre.split('\n'))


def report(short=True):
	ln=lineno()
	text=S.line.split('\n',1)[0]


	print 'File: {}:{}: {}'.format(S.current_file,ln,text)
	print
	if not short:
		print 'S:',S
		print


def strip():
	line = False
	for i in range(len(S.source)):
		c=S.source[i]
		if c in ' \t':
			continue
		if c in '\n':
			continue
		break
		
	S.source=S.source[i:]


def token():
	strip()
	S.line = S.source
	for i in range(len(S.source)):
		c=S.source[i]
		if c in ' \n\t':
			break

	parts=S.source[:i].split(',')
	S.word=parts[0]
	S.args=parts[1:]
	S.source=S.source[i:]
	strip()


def parse():
	builtins()
	for f in S.files:
		S.current_file=f
		S.source=open(f).read()
		S.source_full=S.source
		S.module='main'
		parse_one()


def parse_one():
	S.line = S.source
	try:
		while True:
			token()
			if S.word == '': break
			call()
	except:
		report()
		raise

def c_output(s):
	S.c_file.write(s)
	# S.c_file.write(' //' + S.line.split('\n')[0])
	# S.c_file.write('\n')


def c_bands():
	S.banded={}
	for b in S.band.values():
		ps=[S.pool[x] for x in b.pools]
		sizes=[x.size for x in ps]
		size=max(sizes)

		packing=''
		if b.name in S.pack:
			packing='__attribute__((__packed__)) '

		s='{}struct {} {{\n'.format(b.c_storage,b.c_name)
		c_output(s)
		for p in ps:
			p.size=size
			S.banded[p.name]=b.name
			s="\t{} {};\n".format(p.type,c_name(p.name))
			c_output(s)
		s='}} {}{}[{}];\n'.format(packing,b.c_name,size)
		c_output(s)


def c_bundles():
	S.bundled={}
	for b in S.bundle.values():
		ps=[S.pool[x] for x in b.pools]

		packing=''
		if b.name in S.pack:
			packing='__attribute__((__packed__)) '

		s='{}struct {} {{\n'.format(b.c_storage,b.c_name)
		c_output(s)
		for p in ps:
			S.bundled[p.name]=b.name
			s="\t{} {}[{}];\n".format(p.type,c_name(p.name),p.size)
			c_output(s)
		s='}} {}{};\n'.format(packing,b.c_name)
		c_output(s)


def c_pools():
	for p in S.pool.values():
		if p.name in S.banded: continue
		if p.name in S.bundled: continue
		s="{}{} {}[{}];\n".format(p.c_storage,p.type,p.c_name,p.size)
		c_output(s)


def c_decl_args(fn):
	args=[]
	if fn.args:
		regs=fn.args
	else:
		regs=sorted(fn.regs)
		if regs:
			print 'WARNING: deprecated no-args fn',fn.name,''.join(regs)

	for p in regs:
		type = fn.types.get(p,'uint64_t')
		args.append('{} {}[1]'.format(type,p))
	s=','.join(args)
	c_output(s)


def c_decl_locals(fn):
	for p in sorted(fn.locals):
		if p in fn.args:
			continue
		type = fn.types.get(p,'uint64_t')
		c_output('\t{} {}[1];\n'.format(type,p))


def c_decl_body(fn):
	S.c_module=fn.module
	S.c_current_i=0
	S.c_current_fn=fn
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
			print 'Error at:',op,'in',getattr(fn,'name'),'module',S.c_module
			raise

		S.c_current_i+=1
		

def c_declarations():
	for p in all_fns():
		if not hasattr(p,'body'): continue
		s="{}void {}(".format(p.c_storage,p.c_name)
		c_output(s)
		c_decl_args(p)
		c_output(');\n')


def c_functions():
	for p in all_fns():
		if not hasattr(p,'body'): continue

		s="{}void {}(".format(p.c_storage,p.c_name)
		c_output(s)
		c_decl_args(p)
		c_output(') {\n')
		c_decl_locals(p)
		c_decl_body(p)
		c_output('}\n\n')


def c_udp_handler_args(fn):
	args=[]
	offset='4'

	if fn.args:
		regs=fn.args
	else:
		regs=sorted(fn.regs)

	for p in regs:
		type = fn.types.get(p,'uint64_t')
		args.append('({}*)(packet+{})'.format(type,offset))
		offset=offset+'+sizeof({})'.format(type)
	s=','.join(args)
	c_output(s)


def c_udp_handler():
	s="""
#include <sys/socket.h>
#include <sys/select.h>
#include <arpa/inet.h>

int udp_socket[1]; void udp_setup(void) {{
	udp_socket[0]=socket(AF_INET,SOCK_DGRAM,0);
	struct sockaddr_in a={{.sin_family=AF_INET,.sin_addr.s_addr=inet_addr("127.0.0.1"),.sin_port=htons({})}};
	bind(udp_socket[0],(struct sockaddr*)&a,sizeof(a));
}}

""".format(UDP_PORT)
	c_output(s)


	s="""
void udp_handler(void) {
	struct timeval tv;
	fd_set fds;
	FD_ZERO(&fds);
	FD_SET(udp_socket[0],&fds);
	tv.tv_sec=0;
	tv.tv_usec=0;
	int ret=select(udp_socket[0]+1,&fds,0,0,&tv);
	if(ret==0) return;
	if(ret==-1) {perror("udp"); return; }

	
	uint8_t packet[65535];
	struct sockaddr_in a;
	socklen_t alen=sizeof(a);
	int size=recvfrom(udp_socket[0],packet,sizeof(packet),0,(struct sockaddr*)&a,&alen);


	uint32_t *fn=(uint32_t *)packet;
	switch(*fn) {
"""
	c_output(s)

	opcode=0
	for p in all_fns():
		if not hasattr(p,'body'): continue
		s="\t\tcase {}: {}(".format(opcode, p.c_name)
		c_output(s)
		c_udp_handler_args(p)
		c_output('); break;\n')
		opcode+=1

	s="""
	}
	sendto(udp_socket[0],packet,size,0,(struct sockaddr*)&a,alen);
}
"""
	c_output(s)

def compile():
	S.c_file=open(S.output,'w')
	c_output('#include <stdint.h>\n')

	c_decl_body(S.pro)
	c_bands()
	c_bundles()
	c_pools()
	c_declarations()
	c_functions()

	c_udp_handler()

	c_decl_body(S.annex)

def generate_c_names():
	for fn in all_fns():
		n=c_name(fn.name)
		m=c_name(fn.module)
		fn.c_storage='static '
		fn.c_name='{}__from__{}'.format(n,m)

def generate_pool_c_names():
	for p in S.pool.values():
		n=c_name(p.name)
		m=c_name(p.module)
		p.c_storage='static '
		p.c_name='pool_{}__from__{}'.format(n,m)

def generate_band_c_names():
	for p in S.band.values():
		n=c_name(p.name)
		m=c_name(p.module)
		p.c_storage='static '
		p.c_name='band_{}__from__{}'.format(n,m)
		
def generate_bundle_c_names():
	for p in S.bundle.values():
		n=c_name(p.name)
		m=c_name(p.module)
		p.c_storage='static '
		p.c_name='bundle_{}__from__{}'.format(n,m)
		
		
		

def generate_pool_fns():
	for p in S.pool.values():
		name=p.name

		S.module=p.module

		fn=O()
		fn.name=name
		fn.args='a'
		fn.regs={'a':True}
		fn.locals={'A':True}
		fn.types = {'a':p.type,'A':'uint64_t'}
		fn.body=[('lit','0','A'),('fetchi',p.name,'a','A')]
		register_fn(fn)

		fn=O()
		fn.args='ab'
		fn.name=name+'-i';
		fn.regs={'a':True,'b':True}
		fn.locals={}
		fn.types = {'a':p.type,'b':'uint64_t'}
		fn.body=[('fetchi',p.name,'a','b')]
		register_fn(fn)

		fn=O()
		fn.args='a'
		fn.name=name+'-store'
		fn.regs={'a':True}
		fn.locals={'A':True}
		fn.types = {'a':p.type,'A':'uint64_t'}
		fn.body=[('lit','0','A'),('storei',p.name,'a','A')]
		register_fn(fn)

		fn=O()
		fn.args='ab'
		fn.name=name+'-storei';
		fn.regs={'a':True,'b':True}
		fn.locals={}
		fn.types = {'a':p.type,'b':'uint64_t'}
		fn.body=[('storei',p.name,'a','b')]
		register_fn(fn)

		fn=O()
		fn.args='a'
		fn.name=name+'-size';
		fn.regs={'a':True}
		fn.locals={}
		fn.types = {'a':'uint64_t'}
		fn.body=[('size',p.name,'a')]
		register_fn(fn)




def generate():
	generate_pool_fns()
	generate_pool_c_names()
	generate_band_c_names()
	generate_bundle_c_names()
	generate_c_names()


def temp_debug():
	pprint.pprint(S.pool)
	for n,v in all_fns().items():
		if hasattr(v,'body'):
			pprint.pprint((n,v.regs.keys(),v.body))


def main():
	S.output = sys.argv[1]
	S.files = sys.argv[2:]
	parse()
	generate()
	compile()


main()
