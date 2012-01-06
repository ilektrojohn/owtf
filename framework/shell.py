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

The shell module allows running arbitrary shell commands and is critical to the framework in order to run third party tools
'''
#import shlex
import subprocess
from framework.lib.general import * 

class Shell:
	def __init__(self, CoreObj):
		self.DynamicReplacements = {} # Some settings like the plugin output dir are dynamic, config is no place for those
		self.Core = CoreObj

        def ShellPathEscape(self, Text):
                return MultipleReplace(Text, { ' ':'\ ', '(':'\(', ')':'\)' }).strip()

	def RefreshReplacements(self):
		self.DynamicReplacements['###PLUGIN_OUTPUT_DIR###'] = self.Core.Config.Get('PLUGIN_OUTPUT_DIR')

        def GetModifiedShellCommand(self, Command, PluginOutputDir):
		self.RefreshReplacements()
                return "cd "+self.ShellPathEscape(PluginOutputDir)+"; "+MultipleReplace(Command, self.DynamicReplacements)

        def shell_exec_monitor(self, Command):
                cprint("\nExecuting (Control+C to abort THIS COMMAND ONLY):\n"+Command)
                Output = ''
                try: # Stolen from: http://stackoverflow.com/questions/5833716/how-to-capture-output-of-a-shell-script-running-in-a-separate-process-in-a-wxpyt
                        proc = subprocess.Popen(Command, shell=True,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.STDOUT, 
						  bufsize=1)
                        while True:
                                line = proc.stdout.readline()
                                if not line:
                                        break
				# NOTE: Below MUST BE print instead of "cprint" to clearly distinguish between owtf output and tool output
                                print MultipleReplace(line, { "\n":"", "\r":"" }) # Show progress on the screen too!
                                Output += line # Save as much output as possible before a tool crashes! :)
                except KeyboardInterrupt:
			Output += self.Core.Error.UserAbort('Command', Output) # Identify as Command Level abort
                return Output

        def shell_exec(self, Command, **kwds):
                #Stolen from (added shell=True tweak, necessary for easy piping straight via the command line, etc):
                #http://stackoverflow.com/questions/236737/making-a-system-call-that-returns-the-stdout-output-as-a-string/236909#236909
                kwds.setdefault("stdout", subprocess.PIPE)
                kwds.setdefault("stderr", subprocess.STDOUT)
                p = subprocess.Popen(Command, shell=True, **kwds)
                return p.communicate()[0]

