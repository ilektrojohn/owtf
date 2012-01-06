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

The reporter module is in charge of producing the HTML Report as well as provide plugins with common HTML Rendering functions
'''
import os, re, cgi
from framework.lib.general import *
from collections import defaultdict

class Summary:
	def __init__(self, Core):
		self.Core = Core # Keep Reference to Core Object

	def InitNetMap(self):
		self.PluginsFinished = []
		self.NetMap = defaultdict(list)

	def InitMap(self, IP, Port):
		if IP not in self.NetMap:
			self.NetMap[IP] = defaultdict(list)
		if Port not in self.NetMap[IP]:
			self.NetMap[IP][Port] = []

	def GetSortedIPs(self):
		IPs = []
		for IP, Ports in self.NetMap.items():
			IPs.append(IP)
		return sorted(IPs)

	def GetSortedPorts(self, IP):
		Ports = []
		for Port, PortInfo in self.NetMap[IP].items():
			Ports.append(Port)
		return sorted(Ports)

	def AddToNetMap(self, Report):
		IP = Report['SummaryHostIP']
		Port = Report['SummaryPortNumber']
		self.InitMap(IP, Port)
		self.NetMap[IP][Port].append( Report['ReviewOffset'] )

	def MapReportsToNetMap(self, ReportType): 
		for Report in self.Core.DB.ReportRegister.Search( { 'ReportType' : ReportType } ):
			self.AddToNetMap(Report)

	def RenderNetMap(self):
		IPs = []
		for IP in self.GetSortedIPs():
			IPs.append(self.RenderIP(IP))
		return self.Core.Reporter.Render.DrawHTMLList(IPs)

	def RenderIP(self, IP):
		Ports = []
		for Port in self.GetSortedPorts(IP):
			Ports.append(self.RenderPortInfo(IP, Port))
		return IP + self.Core.Reporter.Render.DrawHTMLList(Ports)

	def CountPluginsFinished(self, ReviewOffset):
		FinishedForOffset = len(self.Core.DB.PluginRegister.Search( { 'ReviewOffset' : ReviewOffset } ))
		self.PluginsFinished.append( { 'Offset' : ReviewOffset, 'NumFinished' : FinishedForOffset } )

	def RenderPluginCountersAsJSON(self):
		Output = []
		for Info in self.PluginsFinished:# Offset, NumFinished 
			Output.append("'"+Info['Offset']+"' : '"+str(Info['NumFinished'])+"'")
		return "{" + ", ".join(Output) + "}"

	def RenderPortInfo(self, IP, Port):
		Offsets = []
		for ReviewOffset in sorted(self.NetMap[IP][Port]):
			ReportPath = self.Core.DB.ReportRegister.Search( { 'ReviewOffset' : ReviewOffset } )[0]['ReportPath']
			#print "IP="+str(IP)+", Port="+str(Port)+" -> ReviewOffset="+str(ReviewOffset)+", ReportPath="+str(ReportPath)
			Offsets.append(self.Core.Reporter.Render.DrawButtonLink(ReviewOffset, self.Core.GetPartialPath(ReportPath), { 'target' : '' } )+self.Core.Reporter.DrawCounters(False, ReviewOffset))
			self.CountPluginsFinished(ReviewOffset)
			#Output += "IP="+IP+", Port="+Port+"->"+
		return Port + self.Core.Reporter.Render.DrawHTMLList(Offsets)

	def RenderAUX(self):
		AuxSearch = self.Core.DB.ReportRegister.Search( { 'ReportType' : 'AUX' } )
		if len(AuxSearch) > 0: # Aux plugin report present, link to it from summary
			# To be passed to JavaScript: AuxSearch[0]['ReviewOffset']
			return self.Core.Reporter.Render.DrawButtonLink('Auxiliary Plugins', self.Core.GetPartialPath(AuxSearch[0]['ReportPath']), { 'class' : 'report_index', 'target' : '' } )
		return "" # Nothing to show

        def ReportStart(self):
		self.Core.Reporter.CounterList = []
		self.Core.Reporter.Header.Save('HTML_REPORT_PATH', { 'ReportType' : 'NetMap', 'Title' : 'Summary Report' } )

	def ReportFinish(self):
		self.ReportStart()
		self.InitNetMap()
		self.MapReportsToNetMap('URL')
		HTML = self.RenderNetMap()
		HTML += self.RenderAUX()
		HTML += """
<script>
var DetailedReport = false
var PluginCounters = """+self.RenderPluginCountersAsJSON()+"""
"""+self.Core.Reporter.DrawJSCounterList()+"""
</script>
"""
                with open(self.Core.Config.Get('HTML_REPORT_PATH'), 'a') as file:
                        file.write(HTML) # Closing HTML Report
		cprint("Summary report written to: "+self.Core.Config.Get('HTML_REPORT_PATH'))

