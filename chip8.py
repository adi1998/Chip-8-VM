#!/usr/bin/python
# TODO : implement display

import sys

v = [0 for i in xrange(16)]
stack=[]
pc=0x200
mem = [0 for i in xrange(4096)]
I=0

def load_rom(fname):
	try:
		rom = map(ord,open(fname,'rb').read())
		if len(rom) > 4096-0x200:
			raise Exception
	except:	
		print "Error importing CHIP-8 rom \"{}\".".format(fname)
		exit(2)

	for i in xrange(len(rom)):
		mem[i + 0x200] = rom[i]

def get_inst():
	return (( (mem[pc] << 8) & 0xffff )+( mem[pc+1] & 0xff )) & 0xffff

def getx(inst):
	return (inst & 0xf00) >> 8

def gety(inst):
	return (inst & 0xf0) >> 4 	

def getnnn(inst):
	return inst & 0xfff

def getbyte(inst):
	return inst & 0xff

def getnib(inst):
	return inst & 0xf

def exec_inst():
	global pc
	global I
	inst = get_inst()
	nnn = getnnn(inst)
	x = getx(inst)
	y = gety(inst)
	kk = getbyte(inst)
	nib = getnib(inst)
	if inst == 0x00e0:
		print "display cleared"
		pc+=2
		return 0
	if inst == 0x00ee:
		pc=stack.pop()
		return 0
	if inst & 0xf000 == 0x0000:
		pc = nnn
		return 0
	if inst & 0xf000 == 0x1000:
		pc = nnn
		return 0
	if inst & 0xf000 == 0x2000:
		pc+=2
		stack.append(pc)
		pc = nnn
		return 0
	if inst & 0xf000 == 0x3000:
		pc+=2
		if v[x] == kkf:
			pc+=2
		return 0
	if inst & 0xf000 == 0x4000:
		pc+=2
		if v[x] != kk:
			pc+=2
		return 0
	if inst & 0xf00f == 0x5000:
		pc+=2
		if v[x] == v[y]:
			pc+=2
		return 0
	if inst & 0xf000 == 0x6000:
		pc+=2
		v[x] = kk
		return 0
	if inst & 0xf000 == 0x7000:
		pc+=2
		v[x] += kk
		return 0
	if inst & 0xf00f == 0x8000:
		pc+=2
		v[x] = v[y]
		return 0
	if inst & 0xf00f == 0x8001:
		pc+=2
		v[x] |= v[y]
		return 0
	if inst & 0xf00f == 0x8002:
		pc+=2
		v[x] &= v[y]
		return 0
	if inst & 0xf00f == 0x8003:
		pc+=2
		v[x] ^= v[y]
		return 0
	if inst & 0xf00f == 0x8004:
		pc+=2
		v[x] += v[y]
		if v[x] > 0xff:
			v[0xf] = 1
		else:
			v[0xf] = 0
		v[x] &= 0xff
		return 0
	if inst & 0xf00f == 0x8005:
		pc+=2
		if v[x] > v[y]: 
			v[0xf] = 1
		else: 
			v[0xf] = 0
		v[x] -= v[y]
		v[x] &= 0xff
		return 0
	if inst & 0xf00f == 0x8006:
		pc+=2
		v[0xf] = v[y] & 0x1
		v[y] = v[x] = v[y] >> 1
		return 0
	if inst & 0xf00f == 0x800e:
		pc+=2
		v[0xf] = v[y] & 0x1
		v[y] = v[x] = (v[y] << 1) & 0xff
		return 0
	if inst & 0xf00f == 0x9000:
		pc+=2
		if v[x] != v[y]:
			pc+=2
		return 0
	if inst & 0xf000 == 0xa000:
		pc+=2
		I = nnn
		return 0
	if inst & 0xf000 == 0xb000:
		pc = v[0]+nnn
		return 0
	if inst & 0xf000 == 0xc000:
		pc += 2
		v[x] = ord(urandom) & kk
		return 0
	if inst & 0xf000 == 0xd000:
		pass
	return 

def main():
	
	if len(sys.argv)==1:
		print "usage: ./chip8.py <chip-8-rom>"
		exit(1)
	
	load_rom(sys.argv[1])
	
	while True: # main loop
		exit_flag = exec_inst()	
		if exit_flag:
			break

if __name__ == "__main__":
	main()

exit(0)