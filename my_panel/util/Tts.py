#coding=utf-8
import pythoncom
from win32event import WaitForSingleObject
import win32com.client
import _thread
import logging
from collections import deque
from time import sleep
from win32event import WaitForSingleObject,INFINITE
import re

# reference: http://msdn.microsoft.com/en-us/library/ms723602%28VS.85%29.aspx

#
## <volume level=”60”></volume> 用于设置文本朗读的音量；
## <rate absspeed=”1”/>、<rate speed=”5”/> 分别用于设置文本朗读的绝对速度和相对速度；
## <pitch absmiddle=”2”/>、<pitch middle=”5”/> 分别用于设置文本朗读的绝对语调和相对语调；
## <emph></emph> 在他们之间的句子被视为强调；
## <spell></spell> 可以将单词逐个字母的拼写出来；
## <silence msec=”500”/> 表示停止发声，并保持500微秒；
## <context id=”date_mdy”>02/03/07</context> 可以按要求朗读出日期
## <voice required="Language=409"></voice> 用于设置朗读所用的语言，其中409表示使用英语，804表示使用汉语，而411表示日语。

# SpVoice Flags
SVSFDefault = 0
SVSFlagsAsync = 1
SVSFPurgeBeforeSpeak = 2
SVSFIsFilename = 4
SVSFIsXML = 8
SVSFIsNotXML = 16
SVSFPersistXML = 32
# Normalizer Flags
SVSFNLPSpeakPunc = 64
# Masks
SVSFNLPMask = 64
SVSFVoiceMask = 127
SVSFUnusedFlags = -128
# SpeechVoiceEvents
SVEStartInputStream = 2
SVEEndInputStream = 4
SVEVoiceChange = 8
SVEBookmark = 16
SVEWordBoundary = 32
SVEPhoneme = 64
SVESentenceBoundary = 128
SVEViseme = 256
SVEAudioLevel = 512
SVEPrivate = 32768
SVEAllEvents = 33790
# SpeechRunState http://msdn.microsoft.com/en-us/library/ms720850%28v=VS.85%29.aspx
SRSEWaiting4Speak=0 # 	A SpeechRunState value of zero represents a state in which the voice is waiting to speak. This condition is returned by ISpeechVoiceStatus.RunningState before the voice has begun speaking, and when the voice is interrupted by an alert voice.
SRSEDone = 1 # The voice has finished rendering all queued phrases.
SRSEIsSpeaking = 2 # The SpVoice currently claims the audio queue.


class TtsVoice(object):
	'''封装TTS的部分操作'''
	# 单实例
	_inited=False
	_singletons={}
	def __new__(cls,*args,**kwds):
		if cls not in cls._singletons: # 若还没有实例
			cls._singletons[cls]=object.__new__(cls) # 生成一个
		return cls._singletons[cls] # 返回这个实例

	def __init__(self):
		if not self.__class__._inited:
			print('%s instance init ...'%(self.__class__.__name__,))
			self.__class__._inited=True
		else:
			print('%s instance already inited .'%(self.__class__.__name__,))
			return


		self.logger=logging.getLogger(self.__class__.__name__)
		if __name__=='__main__':
			logging.basicConfig(level=logging.DEBUG,format='%(thread)d %(message)s')



		# 标识朗读角色的tag
		self._eTagBegin,self._eTagEnd=None,'</rate></voice>'
		self._cTagBegin,self._cTagEnd=None,'</rate></voice>'

		self.pChinese=re.compile('([\u4e00-\u9fa5]+)+?')
		self.pEnglish=re.compile('([^\u4e00-\u9fa5]+)+?')

		self.__pendingVoices=deque() # 待朗读队列

		self.__exitFlag=False
		self.__stopFlag=False
		self.__threadId=0
		self.__voice=None
		# 建立朗读控制线程
		self.__threadId=_thread.start_new_thread(self.VoiceThread,())
		while not self.__voice: # 等待线程中建立voice对象
			sleep(0.3)

	def ShowAllVoicesDesc(self):
		''' 將所有的Voice物件的資訊顯示出來。'''
		self.logger.debug('---- Voice List ----')
		for obj in self.__voice.GetVoices():
			self.logger.debug('Name: %s| Vendor: %s|Age: %s|Gender: %s|Language: %s|Id: %s', obj.GetAttribute('Name'),
				obj.GetAttribute('Vendor'),
				obj.GetAttribute('Age'),
				obj.GetAttribute('Gender'),
				obj.GetAttribute('Language'),
				obj.Id)
		self.logger.debug('---- End of Voice List ----')


	class EventHandler(object):
		'''事件处理类 使用: win32com.client.DispatchWithEvents("SAPI.SpVoice",Eventhandler)
		设置感兴趣的事件
		voice.EventInterests=SVEAllEvents'''
		def OnVoiceChange(self, StreamNumber, StreamPosition, VoiceObjectToken):
			""" 當指定的聲音被改變時，這個事件將會被觸發 """
			self.logger.debug('OnVoiceChange: StreamNumber=%s, StreamPosition=%s, VoiceObjectToken=%s' ,StreamNumber, StreamPosition, VoiceObjectToken)
		def OnAudioLevel(self, StreamNumber, StreamPosition, AudioLevel):
			""" 當指定的音量被改變時，這個事件將會被觸發 """
			self.logger.debug('OnAudioLevel: StreamNumber=%s, StreamPosition=%s, AudioLevel=%s' ,StreamNumber, StreamPosition, AudioLevel)
		def OnWord(self, StreamNumber, StreamPosition, CharacterPosition, Length):
			""" 當每念一個字時，這個事件就會被觸發 """
##			self.logger.debug('OnWord: StreamNumber=%s, StreamPosition=%s, CharacterPosition=%s, Length=%s %s' % (StreamNumber, StreamPosition, CharacterPosition, Length,s2v[StreamNumber-1][CharacterPosition:CharacterPosition+Length]))
			self.logger.debug('OnWord: StreamNumber=%s, StreamPosition=%s, CharacterPosition=%s, Length=%s' ,StreamNumber, StreamPosition, CharacterPosition, Length)
		def OnEnginePrivate(self, StreamNumber, StreamPosition, EngineData):
			""" 語音引擎內部的事件 """
			self.logger.debug ('OnEnginePrivate: StreamNumber=%s, StreamPosition=%s, EngineData=%s' ,StreamNumber, StreamPosition, EngineData)
		def OnSentence(self, StreamNumber, StreamPosition, CharacterPosition, Length):
			""" 當每念一個句子時，這個事件就會被觸發 """
			self.logger.debug ('OnSentence: StreamNumber=%s, StreamPosition=%s, CharacterPosition=%s, Length=%s' ,StreamNumber, StreamPosition, CharacterPosition, Length)
		def OnBookmark(self, StreamNumber, StreamPosition, Bookmark, BookmarkId):
			""" Bookmark """
			self.logger.debug ('OnBookmark: StreamNumber=%s, StreamPosition=%s, Bookmark=%s, BookmarkId=%s' ,StreamNumber, StreamPosition, Bookmark, BookmarkId)
		def OnStartStream(self, StreamNumber, StreamPosition):
			""" 當開始一段語音發音時，這個事件就會被觸發 """
			self.logger.debug ('OnStartStream: StreamNumber=%s, StreamPosition=%s' ,StreamNumber, StreamPosition)
		def OnEndStream(self, StreamNumber, StreamPosition):
			""" 當結束一段語音發音時，這個事件就會被觸發 """
			self.logger.debug ('OnEndStream: StreamNumber=%s, StreamPosition=%s\n' ,StreamNumber, StreamPosition)
		def OnPhoneme(self, StreamNumber, StreamPosition, Duration, NextPhoneId, Feature, CurrentPhoneId):
			""" 每發一個音，這個事件就會被觸發 """
			self.logger.debug ('OnPhoneme: StreamNumber=%s, StreamPosition=%s, Duration=%s, NextPhoneId=%s, Feature=%s, CurrentPhoneId=%s' ,StreamNumber, StreamPosition, Duration, NextPhoneId, Feature, CurrentPhoneId)
		def OnViseme(self, StreamNumber, StreamPosition, Duration, NextVisemeId, Feature, CurrentVisemeId):
			""" 每發一個韻母，這個事件就會被觸發 """
			self.logger.debug ('OnViseme: StreamNumber=%s, StreamPosition=%s, Duration=%s, NextVisemeId=%s, Feature=%s, CurrentVisemeId=%s' ,StreamNumber, StreamPosition, Duration, NextVisemeId, Feature, CurrentVisemeId)

	def _EventInterests(self):
		return self.__voice.EventInterests
	def _setEventInterests(self,value):
		self.__voice.EventInterests =value
	EventInterests=property(fget=_EventInterests,fset=_setEventInterests)

	def _Rate(self):
		return self.__voice.Rate
	def _setRate(self,value):
		self.__voice.Rate=value
	Rate=property(fget=_Rate,fset=_setRate)

	def _Volume(self):
		return self.__voice.Volume
	def _setVolume(self,value):
		self.__voice.Volume=value
	Volume=property(fget=_Volume,fset=_setVolume)

	def Speak(self,text,flags=SVSFlagsAsync):
		'''并非真正朗读 只是将请求放入队列中'''
		text=self.pEnglish.sub('%s\\g<1>%s'%(self._eTagBegin,self._eTagEnd),text)
		text=self.pChinese.sub('%s\\g<1>%s'%(self._cTagBegin,self._cTagEnd),text)

		self.__pendingVoices.append((text,flags))
		if self.__threadId==0 : # 建立朗读控制线程
			self.logger.debug('to create VoiceThread ...')
			self.__threadId=_thread.start_new_thread(self.VoiceThread,())

	def Skip(self,itemType,numItems):
		return self.__voice.Skip(itemType,numItems)

	def Pause(self):
		return self.__voice.Pause()

	def Resume(self):
		return self.__voice.Resume()

##	def setVoice(self,name):
##		for v in self.__voice.GetVoices():
##			if v.GetDescription().find(name)!=-1:
##				self.__voice.Voice=v
##				break
##		else:
##			self.logger.debug('no voice charactor for name %s found!',name)

	def VoiceThread(self):
		'''控制朗读线程'''
		self.logger.debug('VoiceThread created.')
		pythoncom.CoInitialize()
		self.__voice=win32com.client.Dispatch("SAPI.SpVoice")
		while True:
			try:
				text,flag=self.__pendingVoices.popleft() # 取待朗读内容
			except IndexError:
				if self.__exitFlag==False:
					sleep(0.3)
				else:
					break # 退出线程
			else:
				self.logger.debug('%s\n\n',text)
				idx=self.__voice.Speak(text,flag)
##				self.logger.debug('idx=%d RuningState=%d',idx,self.__voice.Status.RunningState)
				while self.__voice.Status.RunningState in (SRSEWaiting4Speak, SRSEIsSpeaking): # 等待此次朗读完成
					if self.__stopFlag:
##						self.__voice.Speak('shit',SVSFPurgeBeforeSpeak)
						break
					sleep(0.3)

			if self.__stopFlag:
				self.__stopFlag=False
				del self.__voice
				break

		pythoncom.CoUninitialize()
		self.logger.debug('VoiceThread exit.')
		self.__threadId=0

	def setExitFlag(self):
		self.__exitFlag=True


	def setVoiceCharacter(self,chinese,english=None):
		if chinese:
			self._cTagBegin='''<voice required="Name={}"><rate speed="+5">'''.format(chinese)
		if english:
			self._eTagBegin='''<voice required="Name={}"><rate speed="-5">'''.format(english)

	def stop(self):
		'''立刻停止朗读'''
		self.__stopFlag=True

	def isSpeaking(self):
		return self.__voice.Status.RunningState==SRSEIsSpeaking


	def Q2B(self,s):
		'''全角转半角 除了空格其他的全角半角的公式为: 半角=全角-0xfee0'''
		def _Q2B(c):
			o=ord(c)
			if o==0x3000: o=0x0020
			else:	o-=0xfee0

			if o<0x0020 or o>0x7e:      #转完之后不是半角字符返回原来的字符
				return c
			return chr(o)

		return ''.join([_Q2B(i) for i in s])

if __name__ =='__main__':
	spk=TtsVoice()

	print('rate=%s volume=%s'%(spk.Rate,spk.Volume))
	spk.ShowAllVoicesDesc()
	# 选择语音角色 这里选择 Paul(Neospeech Text-To-Speech 16K Paul)

	##s2v=['''<voice required="Name=VW Wang" >与之相比，绝大部分架空还真是架在空中。</voice>''',
	##	'''<voice required="Name=VW Paul">this is a test</voice>''',
	##	'''<voice required="Name=VW Wang" >唧唧复唧唧，木兰当户织。</voice>''',
	##	'''<voice required="Name=VW Paul" >gets and sets the types of events.
	##I can speak <PITCH MIDDLE="+10">high</PITCH> and <PITCH MIDDLE="-10">low</PITCH>.
	##I can speak <VOLUME LEVEL="40">quietly</VOLUME> and <VOLUME LEVEL="100">loudly</VOLUME>.
	##<PRON SYM="d eh l f y">Delphi</PRON> developers!
	##<spell>python</spell><silence msec="500" />python
	##</voice>''',
	##	'''<voice required="Name=VW Wang" >举杯邀明月。</voice>''',
	##	'''<voice required="Name=VW Paul" >events received by the SpVoice object.</voice>''',
	##	'''<voice required="Name=VW Wang" >搜狗地图</voice>''']

	s2v=['''唧唧复唧唧''',
		'''this is a test''',
		'''木兰当户织。''',
		'''the types of events.''',
		'''举杯邀明月。''',
		'''events received by the SpVoice object.''',
		'''搜狗地图''']
	s2v1=['''爱老虎油''',
		'''this is a another test''',
		'''进程是程序执行时的一个实例。''',
		'''the types of events.''',
		'''举杯邀明月。''',
		'''events received by the SpVoice object.''',
		'''搜狗地图''']

	s2v2=['''快捷方式''',
		'''this is a another test''',
		'''进程是程序执行时的一个实例。''',
		'''the types of events.''',
		'''举杯邀明月。''',
		'''events received by the SpVoice object.''',
		'''搜狗地图''']

	spk.setVoiceCharacter('VW Wang','VW Paul')
	spk.Speak(''.join(s2v),SVSFlagsAsync)
	spk.Speak(''.join(s2v1),SVSFlagsAsync)


	##while not Finished:
	##	pythoncom.PumpWaitingMessages()
	input('press Enter to stop...\n')
	spk.stop()
	input('press Enter to read again...\n')
	spk.Speak(''.join(s2v2),SVSFlagsAsync)
	input('press Enter to exit...\n')
