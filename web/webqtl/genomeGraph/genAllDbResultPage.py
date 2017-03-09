# Copyright (C) University of Tennessee Health Science Center, Memphis, TN.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# This program is available from Source Forge: at GeneNetwork Project
# (sourceforge.net/projects/genenetwork/).
#
# Contact Drs. Robert W. Williams and Xiaodong Zhou (2010)
# at rwilliams@uthsc.edu and xzhou15@uthsc.edu
#
#
#
# This module is used by GeneNetwork project (www.genenetwork.org)
#
# Created by GeneNetwork Core Team 2010/08/10
#
# Last updated by GeneNetwork Core Team 2010/10/20

import string
import os
import time

from htmlgen import HTMLgen2 as HT

from base import webqtlConfig
from utility import webqtlUtil
from base.webqtlDataset import webqtlDataset
from base.templatePage import templatePage
from dbFunction import webqtlDatabaseFunction

######################################### 
#      Genome Scan PAGE
#########################################
class genAllDbResultPage(templatePage):

	def __init__(self,fd):

		templatePage.__init__(self,fd)

		if not self.openMysql():
			return

		self.database = fd.formdata.getvalue('database', '')
		db = webqtlDataset(self.database, self.cursor)

		try:
			if db.type != "ProbeSet" or not db.id:
				raise DbNameError
		except:
			print 'Content-type: text/html\n'
			heading = "Download Results"
			detail = ["Only results of microarray database are available to download."]
			self.error(heading=heading,detail=detail)
			self.write()
			return


                #XZ, protect confidential dataset.
		userExist = None
                self.cursor.execute('SELECT Id, Name, FullName, confidentiality, AuthorisedUsers FROM ProbeSetFreeze WHERE Name = "%s"' %  self.database)
                indId, indName, indFullName, indConfid, AuthorisedUsers = self.cursor.fetchall()[0]
                if indConfid == 1 and userExist == None:
                    try:

                        userExist = self.userName

                        #for the dataset that confidentiality is 1
                        #1. 'admin' and 'root' can see all of the dataset
                        #2. 'user' can see the dataset that AuthorisedUsers contains his id(stored in the Id field of User table)
                        if webqtlConfig.USERDICT[self.privilege] < webqtlConfig.USERDICT['admin']:
                            if not AuthorisedUsers:
                                userExist=None
                            else:
                                AuthorisedUsersList=AuthorisedUsers.split(',')
                                if not AuthorisedUsersList.__contains__(self.userName):
                                    userExist=None
                    except:
                        pass

                    if not userExist:
                        #Error, Confidential Database
                        heading = "Correlation Table"
                        detail = ["The %s database you selected is not open to the public at this time, please go back and select other database." % indFullName]
                        self.error(heading=heading,detail=detail,error="Confidential Database")
                        return
	
		self.cursor.execute("""
				Select 
					InbredSet.Name
				From
					ProbeSetFreeze, ProbeFreeze, InbredSet
				whERE
					ProbeSetFreeze.ProbeFreezeId = ProbeFreeze.Id AND
					ProbeFreeze.InbredSetId = InbredSet.Id AND
					ProbeSetFreeze.Id = %d
				""" % db.id)
		thisRISet = self.cursor.fetchone()[0]
		if thisRISet =='BXD300':
			thisRISet = 'BXD'

		#XZ, 06/26/2009: It seems that this query is not neccessary. It doesn't return any result.
		#XZ: It seems it is just for test purpose. The next try-except block does the real work.
		#XZ: I think it should be deleted to shorten the response time.	
		#self.cursor.execute("""
		#		Select 
		#			ProbeSet.Name, ProbeSet.symbol, ProbeSet.description, ProbeSet.Chr, ProbeSet.Mb, ProbeSetXRef.Locus, 
		#			ProbeSetXRef.LRS, ProbeSetXRef.pValue, ProbeSetXRef.additive, ProbeSetXRef.mean
		#		From
		#			ProbeSet, ProbeSetXRef
		#		whERE
		#			ProbeSetXRef.ProbeSetFreezeId = %d AND
		#			ProbeSetXRef.ProbeSetId = ProbeSet.Id AND
		#			ProbeSetXRef.Locus is not NULL 
		#		Order by
		#			ProbeSet.name_num
		#		""" % db.id)
		
		filename = os.path.join(webqtlConfig.SECUREDIR, db.name+'.result.xls')

		try:
			import random234
			if random.choice(range(10)) == 0:
				raise "ReCalculate"
			fp = open(filename, 'rb')
			text = fp.read()
			fp.close()
		except:
			self.cursor.execute("Select ProbeSetXRef.ProbeSetId from ProbeSetXRef where ProbeSetFreezeId=%d" % db.id)
			ProbeSetIds = self.cursor.fetchall()
			self.mouseChrLengthDict, sum = self.readMouseGenome(thisRISet)

			if ProbeSetIds:
				import reaper
				markerGMb = {}
				genotype_1 = reaper.Dataset()
				genotype_1.read(os.path.join(webqtlConfig.GENODIR, thisRISet + '.geno'))
				for chr in genotype_1:
					chrlen = self.mouseChrLengthDict[chr.name]
					for locus in chr:	
						markerGMb[locus.name] = [chr.name, locus.Mb, locus.Mb + chrlen]
				
				text = []
				text.append(['ProbeSetId', 'Symbol', 'Description', 'Target Description', 'Chr', 'TMb', 'TGMb', 'Locus', 'LRS', 'Additive', 'pvalue', 'markerChr', 'markerMb', 'markerGMb', 'meanExpression'])
				ProbeSetIdList = []
				for ProbeSetId in ProbeSetIds:
					ProbeSetIdList.append(ProbeSetId[0])
					if len(ProbeSetIdList)==1000:
						ProbeSetIdStr = ','.join(map(str, ProbeSetIdList))
						ProbeSetIdList = []

						cmd = """
							Select 
								ProbeSet.Name, ProbeSet.symbol, ProbeSet.description,ProbeSet.Probe_Target_Description,ProbeSet.Chr, ProbeSet.Mb, 
								ProbeSetXRef.Locus, ProbeSetXRef.LRS, ProbeSetXRef.pValue, 
								ProbeSetXRef.additive, ProbeSetXRef.mean
							From
								ProbeSet, ProbeSetXRef
							Where
								ProbeSetXRef.ProbeSetFreezeId = %s AND
								ProbeSetXRef.ProbeSetId = ProbeSet.Id AND
								ProbeSetXRef.Locus is not NULL AND
								ProbeSet.Id in (%s)
							Order by
								ProbeSet.name_num
						""" % (db.id, ProbeSetIdStr)

						self.cursor.execute(cmd)
						results = self.cursor.fetchall()

						for result in results:
							_Id, _symbol, _desc,_targetDesc, _chr, _TMb, _marker, _lrs, _pvalue, _additive, _mean = result
							if _marker == "-":
								continue
							if not _additive:
								_additive = ""
						
							try:
								_TGMb = _TMb + self.mouseChrLengthDict[string.strip(_chr)]
							except:
								_TGMb = ""

							result2 = [_Id, _symbol, _desc, _targetDesc, _chr, _TMb, _TGMb, _marker, _lrs, _additive, _pvalue]
							try:
								result2 += markerGMb[_marker]
							except:
								result2 += ['', '', '']
							result2 += [_mean]
							text.append(map(str, result2))

				#XZ, 06/29/2007: This block is dealing with the last several probesets that fall out of the 1000-probeset block. 
				if ProbeSetIdList:
					ProbeSetIdStr = ','.join(map(str, ProbeSetIdList))

					cmd = """
						Select 
							ProbeSet.Name, ProbeSet.symbol, ProbeSet.description,ProbeSet.Probe_Target_Description, ProbeSet.Chr, ProbeSet.Mb, 
							ProbeSetXRef.Locus, ProbeSetXRef.LRS, ProbeSetXRef.pValue, 
							ProbeSetXRef.additive, ProbeSetXRef.mean
						From
							ProbeSet, ProbeSetXRef
						Where
							ProbeSetXRef.ProbeSetFreezeId = %s AND
							ProbeSetXRef.ProbeSetId = ProbeSet.Id AND
							ProbeSetXRef.Locus is not NULL AND
							ProbeSet.Id in (%s)
						Order by
							ProbeSet.name_num
					""" % (db.id, ProbeSetIdStr)

					self.cursor.execute(cmd)
					results = self.cursor.fetchall()

					for result in results:
						_Id, _symbol, _desc, _targetDesc,_chr, _TMb, _marker, _lrs, _pvalue, _additive, _mean = result
						if _marker == "-":
							continue
						if not _additive:
							_additive = ""
					
						try:
							_TGMb = _TMb + self.mouseChrLengthDict[string.strip(_chr)]
						except:
							_TGMb = ""

						result2 = [_Id, _symbol, _desc,_targetDesc,  _chr, _TMb, _TGMb, _marker, _lrs, _additive, _pvalue]
						try:
							result2 += markerGMb[_marker]
						except:
							result2 += ['', '', '']
						result2 += [_mean]
						text.append(map(str, result2))

				self.gentextfile(db, text)
				
			else:
				heading = "Download Results"
				detail = ["Database calculation is not finished."]
				self.error(heading=heading,detail=detail)
				return
				
	def gentextfile(self, db, text):
		#
		db.getRISet()
		info = self.getinfo(db.name)
		#
		group = db.riset
		species = webqtlDatabaseFunction.retrieveSpecies(self.cursor, group)
		type = info[4]
		database = db.fullname
		#
		metadatainfofile = "http://www.genenetwork.org/webqtl/main.py?FormID=sharinginfo&GN_AccessionId=%s" % info[1]
		originaldata = "http://datafiles.genenetwork.org/download/GN%s/" % info[1]
		contactinformation = "%s %s, %s, %s, %s, %s %s %s, Tel. %s, %s" % (info[22], info[23], info[33], info[24], info[25], info[26], info[27], info[28], info[29], info[30])
		#
		attachment = ""
		attachment += ("Data source: GeneNetwork http://www.genenetwork.org/\n")
		attachment += ("Citations: http://www.genenetwork.org/reference.html\n")
		
		attachment += ("Species: %s\n" % species)
		attachment += ("Group: %s\n" % group)
		attachment += ("Type: %s\n" % type)
		attachment += ("Database: %s\n" % database)
		
		attachment += ("Metadata info file: %s\n" % metadatainfofile)
		attachment += ("Original data: %s\n" % originaldata)
		attachment += ("Contact Information: %s\n" % contactinformation)
		
		attachment += ("Date: %s\n" % time.strftime("%B %d, %Y", time.gmtime()))
		attachment += ("Time: %s\n" % time.strftime("%H:%M", time.gmtime()))
		
		attachment += "\n"
		attachment += ("Funding for The GeneNetwork: NIAAA (U01AA13499, U24AA13513), NIDA, NIMH, and NIAAA (P20-DA21131), NCI MMHCC (U01CA105417), and NCRR (U01NR 105417)\n")
		attachment += ("PLEASE RETAIN DATA SOURCE INFORMATION WHENEVER POSSIBLE\n")
		attachment += "\n"
		
		rowindex = 0
		for row in text:
			if rowindex == 0:
				row.insert(0, 'Index')
			else:
				row.insert(0, rowindex)
			rowindex += 1
			attachment += string.join(map(lambda cell : str(cell).replace("\r\n", " ").strip(), row), '\t') + "\n"
		
		self.content_type = 'text/plain'
		self.content_disposition = 'attachment; filename=%s' % ('export-%s.txt' % time.strftime("%y-%m-%d-%H-%M"))
		self.attachment = attachment
		
	def getinfo(self, infopagename):
		sql = """SELECT InfoPageName, GN_AccesionId, Species.MenuName, Species.TaxonomyId, Tissue.Name, InbredSet.Name, GeneChip.GeneChipName, GeneChip.GeoPlatform,
			AvgMethod.Name, Datasets.DatasetName, Datasets.GeoSeries, Datasets.PublicationTitle, DatasetStatus.DatasetStatusName, Datasets.Summary, Datasets.AboutCases,
			Datasets.AboutTissue, Datasets.AboutDataProcessing, Datasets.Acknowledgment, Datasets.ExperimentDesign, Datasets.Contributors, Datasets.Citation, Datasets.Notes,
			Investigators.FirstName, Investigators.LastName, Investigators.Address, Investigators.City, Investigators.State, Investigators.ZipCode, Investigators.Country,
			Investigators.Phone, Investigators.Email, Investigators.Url, Investigators.Url, Organizations.OrganizationName, InvestigatorId, DatasetId, DatasetStatusId,
			Datasets.AboutPlatform, InfoFileTitle, Specifics
			FROM InfoFiles
			LEFT JOIN Species USING (SpeciesId)
			LEFT JOIN Tissue USING (TissueId)
			LEFT JOIN InbredSet USING (InbredSetId)
			LEFT JOIN GeneChip USING (GeneChipId)
			LEFT JOIN AvgMethod USING (AvgMethodId)
			LEFT JOIN Datasets USING (DatasetId)
			LEFT JOIN Investigators USING (InvestigatorId)
			LEFT JOIN Organizations USING (OrganizationId)
			LEFT JOIN DatasetStatus USING (DatasetStatusId)
			WHERE InfoPageName=%s
			"""
		self.cursor.execute(sql, infopagename)
		return self.cursor.fetchone()
		
	def readMouseGenome(self, RISet):
		ldict = {}
		lengths = []
		sum = 0
		#####################################
		# Retrieve Chr Length Information
		#####################################
		self.cursor.execute("""
			Select 
				Chr_Length.Name, Length from Chr_Length, InbredSet 
			where 
				Chr_Length.SpeciesId = InbredSet.SpeciesId AND
				InbredSet.Name = '%s'
			Order by 
				Chr_Length.OrderId
			""" % RISet)
		lengths = self.cursor.fetchall()
		ldict[lengths[0][0]] = 0
		prev = lengths[0][1]/1000000.0
		sum += lengths[0][1]/1000000.0
		for item in lengths[1:]:
			ldict[item[0]] = prev
			prev += item[1]/1000000.0
			sum += item[1]/1000000.0
		return ldict, sum
