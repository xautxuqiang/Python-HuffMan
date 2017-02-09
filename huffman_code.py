#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six, argparse

class HuffNode(object):
	def get_weight(self):
		raise NotImplementedError("The Abstract Node Class doesn't define 'get_weight'")

	def isleaf(self):
		raise NotImplementedError("The Abstract Node Class doesn't define 'isleaf'")

class LeafNode(HuffNode):
	def __init__(self, value=0, freq=0):
		super(LeafNode, self).__init__()
		self.value = value
		self.weight = freq

	def isleaf(self):
		return True

	def get_weight(self):
		return self.weight

	def get_value(self):
		return self.value

class IntlNode(HuffNode):
	def __init__(self, left_child=None, right_child=None):
		super(IntlNode, self).__init__()
		self.weight = left_child.get_weight() + right_child.get_weight()
		self.left_child = left_child
		self.right_child = right_child

	def isleaf(self):
		return False

	def get_weight(self):
		return self.weight

	def get_left(self):
		return self.left_child

	def get_right(self):
		return self.right_child

class HuffTree(object):
	def __init__(self, flag, value=0, freq=0, left_child=None, right_child=None):
		super(HuffTree, self).__init__()
		if flag == 0:
			self.root = LeafNode(value, freq)
		else:
			self.root = IntlNode(left_child.get_root(), right_child.get_root())
	
	def get_root(self):
		return self.root

	def get_weight(self):
		return self.root.get_weight()

	def traverse_huffman_tree(self, root, code, char_freq):
		if root.isleaf():
			char_freq[root.get_value()] = code
			print("字符 = %d/%c and 频率 = %d 编码 = %s") % (root.get_value(), chr(root.get_value()), root.get_weight(), code)
			return None
		else:
			self.traverse_huffman_tree(root.get_left(), code+'0', char_freq)
			self.traverse_huffman_tree(root.get_right(), code+'1', char_freq)


def buildHuffmanTree(list_hufftrees):
	while len(list_hufftrees) > 1:
		list_hufftrees.sort(key=lambda x: x.get_weight())
		temp1 = list_hufftrees[0]
		temp2 = list_hufftrees[1]
		list_hufftrees = list_hufftrees[2:]

		newed_hufftree = HuffTree(1, 0, 0, temp1, temp2)

		list_hufftrees.append(newed_hufftree)
	
	return list_hufftrees[0]

def compress(inputfilename, outputfilename):
	f = open(inputfilename,'rb')
	filedata = f.read()
	filesize = f.tell()

	char_freq = {}
	for x in range(filesize):
		tem = six.byte2int(filedata[x])
		if tem in char_freq.keys():
			char_freq[tem] = char_freq[tem] + 1
		else:
			char_freq[tem] = 1

	for tem in char_freq.keys():
		print tem,':',char_freq[tem]

	list_hufftrees = []
	for x in char_freq.keys():
		tem = HuffTree(0, x, char_freq[x], None, None)
		list_hufftrees.append(tem)
	#写入节点长度
	length = len(char_freq.keys())
	output = open(outputfilename, 'wb')

	a4 = length&255
	length = length >> 8
	a3 = length&255
	length = length >> 8
	a2 = length&255
	lenght = length >> 8
	a1 = length&255
	output.write(six.int2byte(a1))
	output.write(six.int2byte(a2))
	output.write(six.int2byte(a3))
	output.write(six.int2byte(a4))
	
	#写入字符和其对应的频率
	for x in char_freq.keys():
		output.write(six.int2byte(x))
		temp = char_freq[x]
		a4 = temp&255
		temp = temp >> 8
		a3 = temp&255
		temp = temp >> 8
		a2 = temp&255
		temp = temp >> 8
		a1 = temp&255
		output.write(six.int2byte(a1))
		output.write(six.int2byte(a2))
		output.write(six.int2byte(a3))
		output.write(six.int2byte(a4))
	
	#构造哈夫曼树	
	tem = buildHuffmanTree(list_hufftrees)
	tem.traverse_huffman_tree(tem.get_root(),'',char_freq)

	#对文件进行压缩
	code = ''
	for i in range(filesize):
		key = six.byte2int(filedata[i])
		code = code + char_freq[key]
		out = 0
		while len(code)>8:
			for x in range(8):
				out = out<<1
				if code[x] == '1':
					out = out | 1
			code = code[8:]
			output.write(six.int2byte(out))
			out = 0
	
	#最终不满8位的code
	output.write(six.int2byte(len(code))) #长度
	out = 0
	for i in range(len(code)):
		out = out<<1
		if code[i]=='1':
			out = out | 1
	for i in range(8-len(code)):
		out = out<<1
	output.write(six.int2byte(out)) #根据长度来得出前多少位有效

	output.close()

def decompress(inputfilename, outputfilename):
	#解压缩文件
	f = open(inputfilename, 'rb')
	filedata = f.read()
	filesize = f.tell()
	
	#读取叶节点个数
	a1 = six.byte2int(filedata[0])
	a2 = six.byte2int(filedata[1])
	a3 = six.byte2int(filedata[2])
	a4 = six.byte2int(filedata[3])
	j = 0
	j = j | a1
	j = j << 8 
	j = j | a2
	j = j << 8
	j = j | a3
	j = j << 8
	j = j | a4

	leaf_node_size = j

	#读取频率信息
	char_freq = {}
	for i in range(leaf_node_size):
		#读取字符
		c = six.byte2int(filedata[4+i*5+0])
		#读取频率
		a1 = six.byte2int(filedata[4+i*5+1])
		a2 = six.byte2int(filedata[4+i*5+2])
		a3 = six.byte2int(filedata[4+i*5+3])
		a4 = six.byte2int(filedata[4+i*5+4])
		j = 0
		j = j | a1
		j = j << 8
		j = j | a2
                j = j << 8
		j = j | a3
                j = j << 8
		j = j | a4
                print "字符:%d/%c 频率:%d" % (c, chr(c), j)
		char_freq[c] = j
	
	#重建哈夫曼树
	list_hufftrees = []
	for x in char_freq.keys():
		tem = HuffTree(0, x, char_freq[x], None, None)
		list_hufftrees.append(tem)

	tem = buildHuffmanTree(list_hufftrees)
	tem.traverse_huffman_tree(tem.get_root(),'',char_freq)

	#解压缩
	output = open(outputfilename, 'wb')
	code = ''
	currnode = tem.get_root()
	for x in range(4+leaf_node_size*5, filesize):
		c = six.byte2int(filedata[x])
		for i in range(8):
			#最高位为1，则code + '1'
			if c&128:
				code = code + '1'
			else:
				code = code + '0'
			#左移一位
			c = c<<1
		#将编码翻译成字符
		while len(code) > 16:
			if currnode.isleaf():
				tem_byte = six.int2byte(currnode.get_value())
				output.write(tem_byte)
				currnode = tem.get_root()

			if code[0] == '1':
				currnode = currnode.get_right()
			else:
				currnode = currnode.get_left()
			code = code[1:]
	
	#处理最后16位
	#先分析前8位，得到最后有效code的长度
	sub_code = code[-16:-8]
	last_length = 0
	for i in range(8):
		last_length = last_length << 1
		if sub_code[i] == '1':
			last_length = last_length | 1

	code = code[-8:-8+last_length]
	
	while len(code) > 0:
		if currnode.isleaf():
			tem_byte = six.int2byte(currnode.get_value())
			output.write(tem_byte)
			currnode = tem.get_root()

		if code[0] == '1':
			currnode = currnode.get_right()
		else:
			currnode = currnode.get_left()
		code = code[1:]

	output.close()

	

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Compress")
	parser.add_argument("-f",metavar="flag",type=int,help="flag==0 compress file flag==1 decompress file")
	parser.add_argument("-i",metavar="inputfile",help="while file to compress")
	parser.add_argument("-o",metavar="outputfie",help="the file have been compressed to output")
	args = parser.parse_args()
	if args.f == 0:
		print 'compress file'
		compress(args.i, args.o)
	else:
		print 'decompress file'
		decompress(args.i, args.o)

	"""
	parser = argparse.ArgumentParser(description="Test HuffMan")
	parser.add_argument("-f",metavar="file",help="which file to access HuffManCode")
	args = parser.parse_args()
	
	f = open(args.f, 'rb')
	filedata = f.read()
	filesize = f.tell()

	char_freq = {}
	for x in range(filesize):
		tem = six.byte2int(filedata[x])
		if tem in char_freq.keys():
			char_freq[tem] = char_freq[tem] + 1
		else:
			char_freq[tem] = 1

	for tem in char_freq.keys():
		print tem,":",char_freq[tem]

	list_hufftrees = []
	for x in char_freq.keys():
		tem = HuffTree(0, x, char_freq[x], None, None)
		list_hufftrees.append(tem)

	tem = buildHuffmanTree(list_hufftrees)
	tem.traverse_huffman_tree(tem.get_root(),'',char_freq)
	"""
