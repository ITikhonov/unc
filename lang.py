
class O:
	def __repr__(_):
		return 'O{'+str(_.__dict__)

S=O()

S.pool = {}
S.fn = {}



def Wpool():
	p=O()
	p.name=word()
	p.size=word()
	p.type=word()
	S.pool[p.name]=p


S.module=locals()

def register():
	for name,fn in S.module.items():
		if not name.startswith('W'): continue
		S.fn[name[1:]] = fn

def call():
	f=S.fn[S.word]
	apply(f)

def report():
	print 'At:',S.at.split('\n',1)[0]


def word():
	S.at = S.source
	S.word,S.source=S.source.split(None,1)
	return S.word


def lang():
	register()

	S.source=open('example.2').read()
	try:
		while True:
			word()
			call()
	except:
		report()
		raise

lang()
print S.pool


