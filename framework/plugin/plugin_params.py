#!/usr/bin/env python
'''
owtf is an OWASP+PTES-focused try to unite great tools and facilitate pen testing
Copyright (c) 2011, Abraham Aranguren <name.surname@gmail.com> Twitter: @7a_ http://7-a.org
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;

The random module allows the rest of the framework to have access to random functionality
'''
#import random, string
from framework.lib.general import *
from collections import defaultdict

class PluginParams:
	def __init__(self, Core, Options):
		self.Core = Core
		self.RawArgs = Options['Args']
		self.Init = False
		self.NoArgs = []

	def ProcessArgs(self):
		self.Args = defaultdict(list)
		for Arg in self.RawArgs:
			Chunks = Arg.split('=')
			if len(Chunks) < 2:
				self.Core.Error.Add("USER ERROR: "+str(Chunks)+" arguments should be in NAME=VALUE format", 'user')
				return False 
			ArgName = Chunks[0]
			try:
				ArgValue = Arg.replace(ArgName, '')[1:]
			except ValueError:
				self.Core.Error.Add("USER ERROR: "+str(ArgName)+" arguments should be in NAME=VALUE format", 'user')
				return False 
			self.Args[ArgName] = ArgValue
		return True

	def ListArgs(self, Args, Mandatory = True):
		cprint("") # Newline
		if Mandatory:
			cprint("Mandatory parameters:")
		else:
			cprint("Optional parameters:")
		for ArgName, ArgDescrip in Args.items():
			if ArgDescrip == None:
				ArgDescrip = ""	
			cprint("- "+ ArgName + (30 - len(ArgName)) * '_' + ArgDescrip.replace('\n', "\n"))

	def GetArgsExample(self, FullArgList, Plugin):
		ArgsStr = []
		for Key, Value in MergeDicts(FullArgList['Mandatory'], FullArgList['Optional']).items():
			ArgsStr.append(Key)
		Pad = '=? '
		return Pad.join(ArgsStr) + Pad
	
	def ShowParamInfo(self, FullArgList, Plugin):
		cprint("\nInformation for "+self.ShowPlugin(Plugin))
		cprint("\nDescription: "+str(FullArgList['Description']))
		self.ListArgs(FullArgList['Mandatory'], True)
		if len(FullArgList['Optional']) > 0:
			self.ListArgs(FullArgList['Optional'], False)
		cprint("\nUsage: "+self.GetArgsExample(FullArgList, Plugin)+"\n")
		self.Core.Error.FrameworkAbort("User is only viewing options, exiting", False)

	def ShowPlugin(self, Plugin):
		return "Plugin: "+Plugin['Type']+"/"+Plugin['File']

	def DefaultArgFromConfig(self, Args, ArgName, SettingList):
		DefaultOrderStr = " (Default order is: "+str(SettingList)+")"
		for Setting in SettingList:
			if self.Core.Config.IsSet(Setting): # Argument is set in config
				Args[ArgName] = self.Core.Config.Get(Setting)
				cprint("Defaulted not passed '"+ArgName+"' to '"+str(Args[ArgName])+"'"+DefaultOrderStr)
				return True
		cprint("Could not default not passed: '"+ArgName+"'"+DefaultOrderStr)
		return False

	def GetArgList(self, ArgList, Plugin, Mandatory = True):
		if not self.Init:
			self.Init = True
			if not self.ProcessArgs(): # Process Passed arguments the first time only
				return self.RetArgError({}, Plugin) # Abort processing (invalid data)
		Args = {}
		for ArgName in ArgList:
			if ArgName not in self.Args:
				ConfigDefaultOrder = [ Plugin['Code']+'_'+Plugin['Type']+"_"+ArgName,  Plugin['Code']+'_'+ArgName, ArgName ]
				Defaulted = self.DefaultArgFromConfig(Args, ArgName, ConfigDefaultOrder)
				Value = ""
				if Defaulted or Mandatory == False:
					continue # The Parameter has been defaulted, must skip loop to avoid assignment at the bottom or Argument is optional = ok to skip
				self.Core.Error.Add("USER ERROR: "+self.ShowPlugin(Plugin)+" requires argument: '"+ArgName+"'", 'user')
				return self.RetArgError({}, Plugin) # Abort processing (invalid data)
			Args[ArgName] = self.Args[ArgName]
		#print "Args before return="+str(Args)
		return Args

	def GetArgError(self, Plugin):
		return Plugin['ArgError']

	def SetArgError(self, Plugin, Error = True):
		Plugin['ArgError'] = Error

	def RetArgError(self, ReturnValue, Plugin):
		self.SetArgError(Plugin, True)
		return ReturnValue
	
	def CheckArgList(self, FullArgList, Plugin):
		if not 'Mandatory' in FullArgList or not 'Optional' in FullArgList:
			self.Core.Error.Add("OWTF PLUGIN BUG: "+self.ShowPlugin(Plugin)+" requires declared Mandatory and Optional arguments")
			return self.RetArgError(True, Plugin)
		if not 'Description' in FullArgList:
			self.Core.Error.Add("OWTF PLUGIN BUG: "+self.ShowPlugin(Plugin)+" requires a Description")
			return self.RetArgError(False, Plugin)
		return True

	def SetArgsBasic(self, AllArgs, Plugin):
		if not AllArgs:
			return NoArgs 
		ArgsStr = []
		#print "self.Args="+str(self.Args)
		for ArgName, ArgValue in AllArgs.items():
			#print "Setting ArgName="+ArgName
			ArgsStr.append(ArgName+"="+str(self.Args[ArgName]))
			AllArgs[ArgName] = ArgValue
		Plugin['Args'] = ' '.join(ArgsStr) # Record arguments in Plugin dictionary
		#print "AllArgs="+str(AllArgs)
		return [ AllArgs ]

	def SetConfig(self, Args):
		for ArgName, ArgValue in Args.items():
			cprint("Overriding configuration setting '_"+ArgName+"' with value "+str(ArgValue)+"..")
			self.Core.Config.Set('_'+ArgName, ArgValue) # Pre-pend "_" to avoid naming collisions

	def GetPermutations(self, Args):
		#print "Args="+str(Args)
		Permutations = defaultdict(list)
		if not 'REPEAT_DELIM' in Args:
			return Permulations # No permutations
		Separator = Args['REPEAT_DELIM']
		for ArgName, ArgValue in Args.items():
			if ArgName == 'REPEAT_DELIM':
				continue # The repeat delimiter is not considered a permutation: It's the permutation delimiter :)
			#print "ArgName="+ArgName+", ArgValue="+str(ArgValue)
			Chunks = ArgValue.split(Separator)
			if len(Chunks) > 1:
				Permutations[ArgName] = Chunks
		return Permutations

	def SetPermutation(self, ArgName, Permutations, PermutationList):
		for i in range(0, len(PermutationList)):
			Count = 0
			for Perm in Permutations:
				PermArgs = PermutationList[i].copy() # 1st copy by value original arguments
				PermArgs[ArgName] = Perm # 2nd override argument with permutation
				if Count == 0: # Modify 1st existing record with permutation
					PermutationList[i] = PermArgs
				else:
					PermutationList.append(PermArgs) # 3rd store each subsequent permutation as a different set of args
				Count += 1

	def SetArgs(self, AllArgs, Plugin):
		ArgList = self.SetArgsBasic(AllArgs, Plugin)
		if not ArgList:
			return ArgList # Nothing to do
		Args = ArgList[0]
		PermutationList = [ Args ]
		for ArgName, Permutations in self.GetPermutations(Args).items():
			self.SetPermutation(ArgName, Permutations, PermutationList)
		if not PermutationList:
			return ArgList # No permutations, return original arguments
		return PermutationList

	def GetArgs(self, FullArgList, Plugin):
		self.SetArgError(Plugin, False)
		if not self.CheckArgList(FullArgList, Plugin):
			return self.NoArgs
		if 'O' in self.RawArgs: # To view available options
			self.ShowParamInfo(FullArgList, Plugin)
			return self.NoArgs # Abort processing, just showing options
		Mandatory = self.GetArgList(FullArgList['Mandatory'], Plugin, True)
		#print "Mandatory="+str(Mandatory)
		Optional = self.GetArgList(FullArgList['Optional'], Plugin, False)
		if self.GetArgError(Plugin):
			cprint("")
			cprint("ERROR: Aborting argument processing, please correct the errors above and try again")
			cprint("")
			return self.NoArgs # Error processing arguments, must abort processing	
		AllArgs = MergeDicts(Mandatory, Optional)
		#print "AllArgs="+str(AllArgs)
		return self.SetArgs(AllArgs, Plugin)

