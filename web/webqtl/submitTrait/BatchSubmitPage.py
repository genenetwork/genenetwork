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

import glob
from htmlgen import HTMLgen2 as HT
import os

from base.templatePage import templatePage
from utility import webqtlUtil
from base import webqtlConfig


# XZ, 09/09/2008: From home, click "Batch Submission".
# XZ, 09/09/2008: This class generate what you see		
#########################################
#      BatchSubmitPage
#########################################

class BatchSubmitPage(templatePage):

	def __init__(self, fd):

		templatePage.__init__(self, fd)

		self.dict['title'] = 'Batch Submission' 
		
		if not self.openMysql():
			return

		TD_LEFT = """
		<TD vAlign=top width="40%" bgColor=#eeeeee>
			<P class="title">Introduction</P>
			<BLOCKQUOTE>
				<P>The batch submission utility enables users to submit multiple
				traits at the same time for analysis by the GeneNetwork and 
				WebQTL. The data  will be stored on our server for no more than 
				24 hours. None of the submitted data are stored or copied 
				elsewhere.</P>
				<P>The file to be uploaded should follow correct format shown 
				in the <A Href="/sample.txt" class="normalsize" target="_blank">
				Sample</A>, <A Href="/sample2.txt" class="normalsize" 
				target="_blank">Sample2</A> text file.</P>
				<P>Please follow the <A href="http://www.genenetwork.org/faq.html#Q-22" class="normalsize" target="_blank">guide</A> for naming your traits.</P>
			</BLOCKQUOTE>
		</TD>
		"""
		TD_RIGHT = HT.TD(valign="top",width="60%",bgcolor="#eeeeee")
		main_title = HT.Paragraph("Batch Trait Submission Utility")
		main_title.__setattr__("class","title")

		#############################

		title1 = HT.Paragraph("1. Choose cross or RI set:")
		title1.__setattr__("class","subtitle")

		STEP1 = HT.TableLite(cellSpacing=2,cellPadding=0,width="90%",border=0)
		crossMenu = HT.Select(name='RISet', onChange='xchange()')
		
		sql = """
			SELECT Species.`Id`, Species.`MenuName`
			FROM Species
			ORDER BY Species.`OrderId`
			"""
		self.cursor.execute(sql)
		for species in self.cursor.fetchall():
			species_id = species[0]
			species_name = species[1]
			optgroup = HT.Optgroup(label = species_name)
			crossMenu.append(optgroup)
			sql = """
				SELECT InbredSet.`Id`, InbredSet.`Name`, InbredSet.`FullName`
				FROM InbredSet
				WHERE InbredSet.`SpeciesId`=%s
				ORDER BY InbredSet.`FullName`
				"""
			self.cursor.execute(sql, (species_id))
			for inbredset in self.cursor.fetchall():
				inbredset_name =  inbredset[1]
				inbredset_fullname =  inbredset[2]
				optgroup.append(tuple([inbredset_fullname, inbredset_name]))
		
		crossMenu.selected.append('BXD')
		crossMenuText = HT.Paragraph('Select the cross or recombinant inbred \
		    set from the menu below. ')
 		infoButton = HT.Input(type="button",Class="button",value="Info",\
 		    onClick="crossinfo2();")
		# NL, 07/27/2010. variable 'IMGSTEP1' has been moved from templatePage.py to webqtlUtil.py;
		TD1 = HT.TD(webqtlUtil.IMGSTEP1,width=58)
		TD2 = HT.TD()
		TD2.append(crossMenuText,crossMenu, infoButton)
		STEP1.append(HT.TR(TD1,TD2),HT.TR(HT.TD(colspan=2,height=20)))
		
		#############################
		title2 = HT.Paragraph("&nbsp;&nbsp;2. Enter Trait Data:")
		title2.__setattr__("class","subtitle")

		STEP2 = HT.TableLite(cellSpacing=2,cellPadding=0,width="90%",border=0)
		Para1 = HT.Paragraph()
		Para1.append('You can submit traits by entering a file name here. The \
		    file should contain a number of no more than 100 traits. The file \
		    should follow the file format described in this ', HT.Href(url=\
		    "/sample.txt",Class="normalsize", target="_blank", \
		    text= 'Sample'), ' text.')
		
		filebox = HT.Paragraph(HT.Input(type='file', name='batchdatafile', size=20))

		# NL, 07/27/2010. variable 'IMGSTEP2' has been moved from templatePage.py to webqtlUtil.py;		
		TD1 = HT.TD(webqtlUtil.IMGSTEP2,width=58)
		TD2 = HT.TD()
		TD2.append(Para1,filebox)
		STEP2.append(HT.TR(TD1,TD2),HT.TR(HT.TD(colspan=2,height=20)))
		
		#############################
		title3 = HT.Paragraph("&nbsp;&nbsp;3. Enter Dataset Name:")
		title3.__setattr__("class","subtitle")

		STEP3 = HT.TableLite(cellSpacing=2,cellPadding=0,width="90%",border=0)
		Para3 = HT.Paragraph()
		textfield = HT.Paragraph(HT.Input(type='text', name='datasetname', size=20, value="Temp"))

		TD1 = HT.TD(webqtlUtil.IMGSTEP3, width=58)
		TD2 = HT.TD()
		TD2.append(Para3, textfield)
		STEP3.append(HT.TR(TD1,TD2),HT.TR(HT.TD(colspan=2,height=20)))		
		
		#########################################
		hddn = {'FormID':'batSubmitResult'}
		
		form = HT.Form(cgi= os.path.join(webqtlConfig.CGIDIR, webqtlConfig.SCRIPTFILE), \
		enctype='multipart/form-data', name='crossChoice', submit=HT.Input(type='hidden'))
		
		submit = HT.Input(type='button' ,name='next', value='Next',onClick=\
		    'batchSelection(this.form);',Class="button") 			
		reset = HT.Input(type='reset' ,name='reset' ,value='Reset',Class="button")
		# NL, 07/27/2010. variable 'IMGNEXT' has been moved from templatePage.py to webqtlUtil.py;	
		form.append(HT.Blockquote(
			title1, HT.Center(STEP1,webqtlUtil.IMGNEXT),
			title2, HT.Center(STEP2,webqtlUtil.IMGNEXT),
			title3, HT.Center(STEP3,webqtlUtil.IMGNEXT)), HT.Center(HT.P(), submit, reset))
			
		for key in hddn.keys():
			form.append(HT.Input(name=key, value=hddn[key], type='hidden'))
		
		TD_RIGHT.append(main_title,form)
		
		self.dict['body'] = TD_LEFT + str(TD_RIGHT)
