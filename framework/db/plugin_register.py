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

The DB stores HTTP transactions, unique URLs and more. 
'''

from framework.lib.general import *
# Run DB field order:
# Start, End, Runtime, Command, LogStatus = self.Core.DB.DBCache['RUN_DB'][-1]#.split(" | ")
CODE = 0
TYPE = 1
PATH = 2
TARGET = 3 # The same plugin and type can be run against different targets, they should have different paths, but we need the target to get the right codes in the report
ARGS = 4 # Auxiliary plugins have metasploit-like arguments
REVIEW_OFFSET = 5

NAME_TO_OFFSET = { 'Code' : CODE, 'Type' : TYPE, 'Path' : PATH, 'Target' : TARGET, 'Args' : ARGS, 'ReviewOffset' : REVIEW_OFFSET }

class PluginRegister:
	def __init__(self, Core):
		self.Core = Core

	def NumPluginsForTarget(self, Target):
		return len(self.Search( { 'Target' : Target } ))

	def AlreadyRegistered(self, Plugin, Path, Target):
		return (len(self.Search( { 'Code' : Plugin['Code'], 'Target' : Target, 'Type' : Plugin['Type'], 'Path' : Path, 'Args' : Plugin['Args'] } )) > 0)

	def Add(self, Plugin, Path, Target): # Registers a Plugin/Path/Target combination only if not already registered
		if not self.AlreadyRegistered(Plugin, Path, Target):
			self.Core.DB.Add('PLUGIN_REPORT_REGISTER', [ Plugin['Code'], Plugin['Type'], Path, Target, Plugin['Args'], self.Core.Config.Get('REVIEW_OFFSET') ] )

	def Search(self, Criteria):
		return self.Core.DB.Search('PLUGIN_REPORT_REGISTER', Criteria, NAME_TO_OFFSET)

