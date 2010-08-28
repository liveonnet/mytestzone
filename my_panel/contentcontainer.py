#coding=utf-8
import codecs
import re
import logging
import os
import struct


class WordFile(object):
	def __init__(self,fname):
		try:
			self.wordlist=codecs.open(fname,encoding='gb18030').readlines()
		except UnicodeDecodeError:
			self.wordlist=codecs.open(fname,encoding='utf8').readlines()
		self.wordlist=[ i.strip() for i in self.wordlist if len(i.strip())!=0]
		self.maxidx=len(self.wordlist)-1
		self.curidx=0

	def __iter__(self):
		return self

	def __next__(self):
		if self.curidx<self.maxidx:
			self.curidx+=1
			return self.wordlist[self.curidx-1]
		else:
			raise StopIteration()

	def __len__(self):
		return len(self.wordlist)

	def __getitem__(self,key):
		return self.wordlist[key]

	def setStart(self,idx):
		if idx<self.maxidx:
			self.curidx=idx
		else:
			self.curidx=self.maxidx

	def getIdx(self):
		return self.curidx-1


class SubtitleFile(object):
	def __init__(self,fname):
		try:
			self.wordlist=codecs.open(fname,encoding='gb18030').readlines()
		except UnicodeDecodeError:
			self.wordlist=codecs.open(fname,encoding='utf8').readlines()

		logging.debug('use %s to split...',repr(os.linesep*2))
		self._wordlist=re.split(os.linesep*2,''.join(self.wordlist))
		if len(self._wordlist)<10:
			logging.debug('use %s to split...',repr(os.linesep))
			self._wordlist=re.split(os.linesep,''.join(self.wordlist))
		
		self.wordlist=self._wordlist
		logging.debug('len(self.wordlist)=%d',len(self.wordlist))
		logging.debug('self.wordlist[:3]=%s',self.wordlist[:3])
		self.maxidx=len(self.wordlist)-1
		self.curidx=0

	def __iter__(self):
		return self

	def __next__(self):
		if self.curidx<self.maxidx:
			self.curidx+=1
			return self.wordlist[self.curidx-1]
		else:
			raise StopIteration()

	def __len__(self):
		return len(self.wordlist)

	def __getitem__(self,key):
		return self.wordlist[key]

	def setStart(self,idx):
		if idx<self.maxidx:
			self.curidx=idx
		else:
			self.curidx=self.maxidx

	def getIdx(self):
		return self.curidx-1


class StartDictFile(object):
	__maxWordStrLen=256
	__maxOffsetLen=4
	__functionMaping={
		'm':'__readDict_m','l':'__readDict_l','g':'__readDict_g',
		't':'__readDict_t','x':'__readDict_x','y':'__readDict_y',
		'k':'__readDict_k','w':'__readDict_w','h':'__readDict_h',
		'r':'__readDict_r','W':'__readDict_W','P':'__readDict_P',
		'X':'__readDict_X','n':'__readDIct_n'}

	def __init__(self,fname):
		self.logger=logging.getLogger(self.__class__.__name__)
		self.__baseFileName=""
		tmp=fname.rpartition(".")
		if tmp[0] is None and tmp[1] is None:
			self.logger.debug("no dot found in filename %s",fname)
			self.__baseFileName=tmp[2]
		else:
			self.__baseFileName=tmp[0]
		self.__idxFileName=self.__baseFileName+".idx"
		self.__ifoFileName=self.__baseFileName+".ifo"
		self.__dictFileName=self.__baseFileName+".dict"

		self.__dictInfo={}
		self.__dictIndex={}


	def getIdxList(self):
		return sorted(self.__dictIndex.keys())


	def readIFO(self):
		with codecs.open(self.__ifoFileName,'r',encoding='utf-8') as f:
			for line in f:
				line=line.rstrip()
				if line.find("=")==-1:
					continue
				kv=line.split("=")
				if len(kv)<1:
					continue
				self.__dictInfo[kv[0]]=(len(kv)>1 and [kv[1]] or [None])[0]

		if self.__dictInfo["version"]=="3.0.0" and self.__dictInfo.has_key("idxoffsetbits"):
				self.__class__.__maxOffsetLen=int(self.__dictInfo["idxoffsetbits"])/8
				logging.debug("word_data_offset is %d bytes !",self.__class__.__maxOffsetLen)

		self.logger.debug("self.__dictInfo=%s",self.__dictInfo);


	def readIDX(self):
		with open(self.__idxFileName,'rb') as f:
			wordStr=""
			wordDataOffset=0
			wordDataSize=0
			offsetLen=4
			cnt=0
			while True:
				wordStr=self.__readUntilZero(f)
				if wordStr=="":
					self.logger.debug("wordStr=\"\",break!")
					break
				cnt+=1
##				if cnt>=50:
##					logging.debug("reach 100 items,break.")
##					break
#				if cnt%5000==0:
#					logging.debug("processed %d",cnt)
#				if len(wordStr)>=256:
#					print str(len(wordStr))
#					logging.debug("wordStr>=256! (%d)",len(wordStr))
				wordDataOffset=self.__readNumber(f,self.__class__.__maxOffsetLen)
				wordDataSize=self.__readNumber(f)
				self.__dictIndex[wordStr]=(wordDataOffset,wordDataSize)
#				logging.debug('%s=%d,%d',wordStr,wordDataOffset,wordDataSize)

		self.logger.debug("len(self.__dictIndex)=%d",len(self.__dictIndex))

	def __readUntilZero(self,fileObj,maxRead=0,debug=False):
		if maxRead:
			return fileObj.read(maxRead)

		strRtn=""
		while True:
			by=fileObj.read(1).decode()
			if by=="\0" or by=="":
				break
			strRtn+=by

		return strRtn

	def __readNumber(self,fileObj,numberSize=4):
		strRtn=fileObj.read(numberSize)
		intRtn=struct.unpack("!i",strRtn)[0]
#		logging.debug("strRtn=|%s| intRtn=%d",' '.join(["%02X"%(ord(c)) for c in strRtn]),intRtn)
		return intRtn

	def getMeaning(self,strToSearch):
		if not self.__dictIndex:
			self.logger.debug("index file not load!")
			return None

		if not strToSearch:
			self.logger.debug("strToSearch is invalid!")
			return None

		self.logger.debug("strToSearch=|%s|",strToSearch)

		sametype=self.__dictInfo.get("sametypesequence")

		offset,size=self.__dictIndex.get(strToSearch,(None,None))
		if (not offset) or (not size):
			self.logger.debug("key not found!")
			return None
		self.logger.debug("offset=%d,size=%d",offset,size)

		rslt=''

		with open(self.__dictFileName,'rb') as f:
			f.seek(offset,os.SEEK_SET)
			cnt=0
			by=""
			if not sametype:
				self.logger.debug("sametypesequence not defined!")
				while cnt<size:
					by=f.read(1)
					cnt+=1
					tmpSize=0
					if not self.__class__.__functionMaping.has_key(by):
						self.logger.debug("can't judge data type %s!",ord(by))
						raise Exception()
					tmpSize,tmpText=getattr(self,"_"+self.__class__.__name__+self.__class__.__functionMaping[by])(f,offset,size)
					cnt+=tmpSize
			else:
#				logging.debug("sametypesequence=%s",sametype)
				for datatype in sametype:
					tmpSize=0
					if datatype not in self.__class__.__functionMaping:
						self.logger.debug("can't judge data type %s!",ord(datatype))
						raise Exception()
					tmpSize,tmpText=getattr(self,"_"+self.__class__.__name__+self.__class__.__functionMaping[datatype])(f,offset,size)
					rslt+=tmpText
					cnt+=tmpSize

		return rslt


	def __readDict_m(self,fileObj,offset,size,debug=False):
		# Word's pure text meaning.
		# The data should be a utf-8 string ending with '\0'.'
		strText=self.__readUntilZero(fileObj,size,debug).decode()
##		strText=strText.replace('\n','\\n')
		return (len(strText)+1,strText)
	def __readDict_l(self,fileObj,offset,size):
		# Word's pure text meaning.
		# The data is NOT a utf-8 string, but is instead a string in locale
		# encoding, ending with '\0'.  Sometimes using this type will save disk
		# space, but its use is discouraged.
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_g(self,fileObj,offset,size):
		# A utf-8 string which is marked up with the Pango text markup language.
		# For more information about this markup language, See the "Pango
		# Reference Manual."
		# You might have it installed locally at:
		# file:///usr/share/gtk-doc/html/pango/PangoMarkupFormat.html
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_t(self,fileObj,offset,size):
		# English phonetic string.
		# The data should be a utf-8 string ending with '\0'.
		# Here are some utf-8 phonetic characters:
		# θʃŋʧðʒæıʌʊɒɛəɑɜɔˌˈːˑṃṇḷ
		# æɑɒʌәєŋvθðʃʒɚːɡˏˊˋ
		strPhonetic=""
		strPhonetic=self.__readUntilZero(fileObj)
		self.logger.debug("strPhonetic=|%s|",strPhonetic)
		return (len(strPhonetic)+1,strPhonetic)
	def __readDict_x(self,fileObj,offset,size):
		# A utf-8 string which is marked up with the xdxf language.
		# See http://xdxf.sourceforge.net
		# StarDict have these extention:
		# <rref> can have "type" attribute, it can be "image", "sound", "video"
		# and "attach".
		# <kref> can have "k" attribute.
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_y(self,fileObj,offset,size):
		# Chinese YinBiao or Japanese KANA.
		# The data should be a utf-8 string ending with '\0'.
		strYinBiao=""
		strYinBiao=self.__readUntilZero(fileObj)
		self.logger.debug("strYinBiao=|%s|",strYinBiao)
		return (len(strYinBiao)+1,strYinBiao)
	def __readDict_k(self,fileObj,offset,size):
		# KingSoft PowerWord's data. The data is a utf-8 string ending with '\0'.
		# It is in XML format.
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_w(self,fileObj,offset,size):
		# MediaWiki markup language.
		# See http://meta.wikimedia.org/wiki/Help:Editing#The_wiki_markup
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_h(self,fileObj,offset,size):
		''' Html codes.'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_r(self,fileObj,offset,size):
		'''# Resource file list.
		 The content can be:
		 img:pic/example.jpg	// Image file
		 snd:apple.wav		// Sound file
		 vdo:film.avi		// Video file
		 att:file.bin		// Attachment file
		 More than one line is supported as a list of available files.
		 StarDict will find the files in the Resource Storage.
		 The image will be shown, the sound file will have a play button.
		 You can "save as" the attachment file and so on.
		'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_W(self,fileObj,offset,size):
		''' wav file.
		 The data begins with a network byte-ordered guint32 to identify the wav
		 file's size, immediately followed by the file's content.
		'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_P(self,fileObj,offset,size):
		''' Picture file.
		 The data begins with a network byte-ordered guint32 to identify the picture
		 file's size, immediately followed by the file's content.
		'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_X(self,fileObj,offset,size):
		''' this type identifier is reserved for experimental extensions.'''
		self.logger.debug("not implement yet!")
		return (0,None)
	def __readDict_None(self,fileObj,offset,size):
		self.logger.debug("do nothing!",)
		return (0,None)

	def __readDict_n(self,fileObj,offset,size):
		'''WordNet data.'''
		self.logger.debug("not implement yet!")
		return (0,None)

	def loadFile(self):
		self.readIFO()
		self.readIDX()

		if self.__dictIndex:
			for key in self.__dictIndex.iterkeys():
				self.getMeaning(key)

	def Dict2Txt(self,ofilename):
		self.readIFO()
		idxFile=""
		dictFile=""
		with open(self.__idxFileName,'rb') as f:
			idxFile=f.read()
		lenidx=len(idxFile)
		with open(self.__dictFileName,'rb') as f:
			dictFile=f.read()
		lendict=len(dictFile)
		of=open(ofilename,'w')
		wordCnt=0
		s=[]
		idx=0
		try:
			while True:
				old_idx=idx
				while idx<lenidx:
					if idxFile[idx]=='\0':
						break
					idx+=1

				if old_idx==idx:
					self.logger.debug("wordStr=\"\",break!")
					break

				wordStr=buffer(idxFile,old_idx,idx-old_idx)
#				offset=ord(idxFile[idx+1])<<24|ord(idxFile[idx+2])<<16|ord(idxFile[idx+3])<<8|ord(idxFile[idx+4])
				offset=struct.unpack_from(">i",idxFile,idx+1)[0]
#				size=ord(idxFile[idx+5])<<24|ord(idxFile[idx+6])<<16|ord(idxFile[idx+7])<<8|ord(idxFile[idx+8])
				size=struct.unpack_from(">i",idxFile,idx+5)[0]

#				logging.debug("wordStr=%s,offset=%d,size=%d",wordStr,offset,size)
				idx+=9

#				wordCnt+=1
#				if wordCnt>10:
#					break

				strText=dictFile[offset:offset+size].replace('\n','\\n')
				s.append("%s\t%s\n"%(wordStr,strText))

			of.writelines(s)
		finally:
			of.close()

		self.logger.debug("done.")


if __name__ == '__main__':
	t=StartDictFile(r'D:\Program Files\StarDict\dic\stardict-langdao-ec-gb-2.4.2\langdao-ec-gb.ifo')
	t.readIFO()
	t.readIDX()
	print(t.getMeaning('test'))