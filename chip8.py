#!/usr/bin/python
from time import sleep
from os import urandom
from pygame import display, HWSURFACE, DOUBLEBUF, Color, draw, key
import pygame
import sys

scale_factor=10

display.init()
s = display.set_mode(((64*scale_factor),(32*scale_factor)), HWSURFACE | DOUBLEBUF, 8)
s.fill(Color(0,0,0,255))
display.flip()

v = [0 for i in xrange(16)]
stack=[]
pc=0x200
mem = [0 for i in xrange(4096)]
I=0
disp = [[0 for i in xrange(64)] for j in xrange(32)]
key_map = {
	49:1,
	50:2,
	51:3,
	52:4,
	53:5,
	54:6,
	55:7,
	56:8,
	57:9,
	58:0,
	97:0xa,
	98:0xb,
	99:0xc,
	100:0xd,
	101:0xe,
	102:0xf
}
DT=0

key_inv_map = {v: k for k, v in key_map.iteritems()}

class PCOutOfBoundsError(Exception):
	pass
colormap = {
	    0: Color(0, 0, 0, 255),
	    1: Color(255, 255, 255, 255)
	}
def update_display():
	
	for i in xrange(32):
		for j in xrange(64):
			draw.rect(s,colormap[disp[i][j]],(j*scale_factor,i*scale_factor,scale_factor,scale_factor))
	display.flip()

def load_rom(fname):
	try:
		rom = map(ord,open(fname,'rb').read())
		if len(rom) > 4096-0x200:
			raise Exception
	except:	
		print "Error importing CHIP-8 rom \"{}\".".format(fname)
		exit(2)

	font = open("hexsprites",'rb').read()

	for i,val in enumerate(font):
		mem[i]=ord(val)

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
	global DT
	inst = get_inst()
	nnn = getnnn(inst)
	x = getx(inst)
	y = gety(inst)
	kk = getbyte(inst)
	nib = getnib(inst)
	if inst == 0x00e0:
		pc+=2
		for i in xrange(32):
			disp[i]=[0 for j in xrange(64)]
		update_display()
		return 0
	if inst == 0x00ee:
		pc=stack.pop()
		return 0
	if inst & 0xf000 == 0x0000:
		pc+=2
		stack.append(pc)
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
		if v[x] == kk:
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
		v[x] = kk & 0xff
		return 0
	if inst & 0xf000 == 0x7000:
		pc+=2
		v[x] += kk
		v[x] = v[x] & 0xff
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
	if inst & 0xf00f == 0x8007:
		pc+=2
		if v[x] < v[y]: 
			v[0xf] = 1
		else: 
			v[0xf] = 0
		v[x] = v[y]-v[x]
		v[x] &= 0xff
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
		v[x] = (ord(urandom(1)) & kk) & 0xff
		return 0
	if inst & 0xf000 == 0xd000:
		pc+=2
		sprite = [map(int,bin(i)[2:].rjust(8,"0")) for i in mem[I:I+nib]]
		v[0xf] = 0
		for i in xrange(nib):
			for j in xrange(8):
				if disp[(v[y]+i) % 32][(v[x]+j) % 64] == sprite[i][j] == 1:
					v[0xf]=1 
				disp[(v[y]+i) % 32][(v[x]+j) % 64] ^= sprite[i][j]
		update_display()
		return 0
	if inst & 0xf0ff == 0xe09e:
		pc+=2
		pygame.event.get()
		key_stat = key.get_pressed()
		if key_stat[key_inv_map[v[x]]]==1:
			pc+=2
		return 0
	if inst & 0xf0ff == 0xe0a1:
		pc+=4
		key_stat=[]
		pygame.event.get()
		key_stat = key.get_pressed()
		if key_stat[key_inv_map[v[x]]]==1:
			pc-=2	
		return 0
	if inst & 0xf0ff == 0xf007:
		pc+=2
		v[x] = DT & 0xff
		return 0
	if inst & 0xf0ff == 0xf00a:
		pc+=2
		f=0
		while True:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					temp = key.get_pressed()
					for i in key_inv_map:
						if temp[key_inv_map[i]]:
							v[x]=i
							f=1 
							break
					if f==1:
						break
			if f==1:
				break
		return 0
	if inst & 0xf0ff == 0xf015:
		pc+=2
		DT=v[x]
		return 0
	if inst & 0xf0ff == 0xf018:
		pc+=2
		return 0
	if inst & 0xf0ff == 0xf01e:
		pc+=2
		I+=v[x]
		return 0
	if inst & 0xf0ff == 0xf029:
		pc+=2
		I = v[x]*5
		return 0
	if inst & 0xf0ff == 0xf033:
		pc+=2
		mem[I] = v[x]/100
		mem[I+1] = v[x]/10 % 10
		mem[I+2] = v[x] % 10
		return 0
	if inst & 0xf0ff == 0xf055:
		pc+=2
		for i in xrange(x+1):
			mem[I+i] = v[i]
		return 0
	if inst & 0xf0ff == 0xf065:
		pc+=2
		for i in xrange(x+1):
			v[i] = mem[I+i] & 0xff
		return 0
	return 1

def main():
	global DT
	if len(sys.argv)==1:
		print "usage: ./chip8.py <chip-8-rom>"
		exit(1)

	pygame.init()
	load_rom(sys.argv[1])
	last_ticks = pygame.time.get_ticks()
	
	while True: # main loop
		try:

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					display.quit()
					pygame.quit()
					exit()

			exit_flag = exec_inst()	

			now_ticks = pygame.time.get_ticks()
			if now_ticks - last_ticks > 16:
				diff = now_ticks - last_ticks
				ticks_passed = diff / 16
				DT = max(0,DT-ticks_passed)
				last_ticks = now_ticks - diff % 16

		except Exception as e:
			print e
			break
		if exit_flag:
			break

if __name__ == "__main__":
	main()

exit(0)