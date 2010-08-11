#coding=utf-8
import sys

class _Const(object):
	''' 保存常量'''
	class ConstError(TypeError):pass
	def __new__(type):
		if not '_instance' in type.__dict__:
			type._instance=object.__new__(type)
		return type._instance

	def __setattr__(self,name,value):
		if name in self.__dict__:
			raise self.ConstError('Error!')
		self.__dict__[name]=value

sys.modules[__name__]=_Const()