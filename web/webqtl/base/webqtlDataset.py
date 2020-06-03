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

from htmlgen import HTMLgen2 as HT

import webqtlConfig

#import logging
#logging.basicConfig(filename="/tmp/gn.log", level=logging.INFO)
#_log = logging.getLogger("\gn\web\webqtl\base\webqtlDataset.py")

class webqtlDataset:
	"""
	Database class defines a database in webqtl, can be either Microarray, 	
	Published phenotype, genotype, or user input database(temp)
	"""

	def __init__(self, dbName, cursor=None):

		assert dbName
		self.id = 0
		self.name = ''
		self.displayname = ''
		self.type = ''
		self.riset = ''
		self.cursor = cursor

                #temporary storage
		if dbName.find('Temp') >= 0:
			self.searchfield = ['name','description']
			self.disfield = ['name','description']
			self.type = 'Temp'
			self.id = 1
			self.fullname = 'Temporary Storage'
			self.shortname = 'Temp'
		elif dbName.find('Publish') >= 0:
			self.searchfield = ['name','post_publication_description','abstract','title','authors']
			self.disfield = ['name','pubmed_id', 
					'pre_publication_description', 'post_publication_description', 'original_description', 
					'pre_publication_abbreviation', 'post_publication_abbreviation',
					'lab_code', 'submitter', 'owner', 'authorized_users',
					'authors','title','abstract', 'journal','volume','pages','month',
					'year','sequence', 'units', 'comments']
			self.type = 'Publish'
		elif dbName.find('Geno') >= 0:
			self.searchfield = ['name','chr']
			self.disfield = ['name','chr','mb', 'source2', 'sequence']
			self.type = 'Geno'
		else: #ProbeSet
			self.searchfield = ['name','description','probe_target_description',
				'symbol','alias','genbankid','unigeneid','omim',
				'refseq_transcriptid','probe_set_specificity', 'probe_set_blat_score']
			self.disfield = ['name','symbol','description','probe_target_description',
				'chr','mb','alias','geneid','genbankid', 'unigeneid', 'omim',
				'refseq_transcriptid','blatseq','targetseq','chipid', 'comments',
				'strand_probe','strand_gene','probe_set_target_region', 'proteinid',
				'probe_set_specificity', 'probe_set_blat_score','probe_set_blat_mb_start',
				'probe_set_blat_mb_end', 'probe_set_strand', 
				'probe_set_note_by_rw', 'flag']
			self.type = 'ProbeSet'
		self.name = dbName
		self.displayname = self.name
		if self.cursor and self.id == 0:
			self.retrieveName()
	
	def __str__(self):
		return self.name
	
	__repr__ = __str__


	def getRISet(self):
		assert self.cursor
		if self.type == 'Publish':
			query = '''
					SELECT 
						InbredSet.Name, InbredSet.Id
					FROM 
						InbredSet, PublishFreeze 
					WHERE 
						PublishFreeze.InbredSetId = InbredSet.Id AND 
						PublishFreeze.Name = "%s"
				''' % self.name
		elif self.type == 'Geno':
			query = '''
					SELECT 
						InbredSet.Name, InbredSet.Id
					FROM 
						InbredSet, GenoFreeze 
					WHERE 
						GenoFreeze.InbredSetId = InbredSet.Id AND 
						GenoFreeze.Name = "%s"
				''' % self.name
		elif self.type == 'ProbeSet':
			query = '''
					SELECT 
						InbredSet.Name, InbredSet.Id
					FROM 
						InbredSet, ProbeSetFreeze, ProbeFreeze 
					WHERE 
						ProbeFreeze.InbredSetId = InbredSet.Id AND 
						ProbeFreeze.Id = ProbeSetFreeze.ProbeFreezeId AND 
						ProbeSetFreeze.Name = "%s"
				''' % self.name
		else:
			return ""
		self.cursor.execute(query)
		RISet, RIID = self.cursor.fetchone()
		if RISet == 'BXD300':
			RISet = "BXD"
		self.riset = RISet
		self.risetid = RIID
		return RISet
		
	def retrieveName(self):
		assert self.id == 0 and self.cursor
		if self.type == 'ProbeSet':
			query = '''
				SELECT 
					Id, Name, FullName, ShortName, DataScale
				FROM 
					%sFreeze 
				WHERE 
					public > %d AND 
					(Name = "%s" OR FullName = "%s" OR ShortName = "%s")
			  '''% (self.type, webqtlConfig.PUBLICTHRESH, self.name, self.name, self.name)
			try:
				self.cursor.execute(query)
				self.id, self.name, self.fullname, self.shortname, self.datascale = self.cursor.fetchone()
			except:
				raise KeyError, `self.name`+' doesn\'t exist.'
		else:
			query = '''
				SELECT 
					Id, Name, FullName, ShortName 
				FROM 
					%sFreeze 
				WHERE 
					public > %d AND 
					(Name = "%s" OR FullName = "%s" OR ShortName = "%s")
			  '''% (self.type, webqtlConfig.PUBLICTHRESH, self.name, self.name, self.name)
			try:
				self.cursor.execute(query)
				self.id,self.name,self.fullname,self.shortname=self.cursor.fetchone()
			except:
				raise KeyError, `self.name`+' doesn\'t exist.'
	
	def genHTML(self, Class='c0dd'):
		return  HT.Href(text = HT.Span('%s Database' % self.fullname, Class= "fwb " + Class), 
			url= webqtlConfig.INFOPAGEHREF % self.name,target="_blank")
