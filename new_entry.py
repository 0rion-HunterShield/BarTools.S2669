#/usr/bin/env python3

import csv
import pandas as pd
import base64,json
import random
from datetime import datetime
from pathlib import Path

class NewEntry:
	def __init__(self):
		sep=';'
		self.filename=Path('NewCode.csv')
		self.pc_path=str(Path().home()/Path('Documents')/self.filename)
		self.android_path=str(Path("/storage/emulated/0/Documents")/self.filename)
		self.bar_length=12
		self.code_length=8
		self.code_suffix="Local"
		self.barcode=''.join([str(random.randint(0,9)) for i in range(self.bar_length)])
		self.code='{code}-{suffix}'.format(code=''.join([str(random.randint(0,9)) for i in range(self.code_length)]),suffix=self.code_suffix)
		
		self.doe=datetime.strftime(datetime.now(),"%m/%d/%y")
		
		self.tags=''
		tags=[]
		while True:
			self.tags=input("Tag for Item(!q==NEXT): ")
			
			if self.tags not in ["!q",]:
				tags.append(self.tags)
			else:
				break
			print(tags)

		self.tags=','.join(tags)

		self.name=''
		while True:
			self.name=input("Name for Item(!q==NEXT): ")
			if self.name in ['!q',]:
				break
			if len(self.name) > 0:
				break

		self.df=pd.DataFrame(
			{
				'barcode':[self.barcode,],
				'name':[self.name,],
				'code':[self.code,],
				'doe':[self.doe,],
				'tags':[self.tags,],
			}
			)
		while True:
			whatAmI=input("Android or PC?[A|a==Android,P|p==PC]: ")
			if whatAmI.lower() not in ['a','p']:
				continue
			if whatAmI.lower() == 'p':
				self.df.to_csv(self.pc_path,index=False,sep=sep)
				print(self.pc_path)
				break
			elif whatAmI.lower() == 'a':
				self.df.to_csv(self.android_path,index=False,sep=sep)
				print(self.android_path)
				break

NewEntry()


