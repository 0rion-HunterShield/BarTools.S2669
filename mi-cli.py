#!/usr/bin/env python3
import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta
import zipfile,tarfile
import base64
from ast import literal_eval
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from pathlib import Path
from matplotlib import image
from matplotlib import pyplot as plt

BASE=automap_base()
filename=Path("/storage/emulated/0/Documents/MBI/DB/dbase.db3")
if not filename.exists():
	raise Exception(str(filename.exists())+":"+str(filename))
dbfile="sqlite:///"+str(filename)
print(dbfile)
import sqlite3
z=sqlite3.connect(filename)
print(z)
ENGINE=create_engine(dbfile)
BASE.prepare(autoload_with=ENGINE)
TABLE=BASE.classes
class SystemMain:
	class UpdateItem:
		class LookupByBarcode:
			def __init__(self):
				pass
				
		class LookupByItemCode:
			def __init__(self):
				pass
				
		class LookupByItemId:
			def __init__(self):
				pass
				
		def __init__(self):
			while True:
				try:
					lookup_type=input("barcode|code|id|quit|back: ")
					lookup_type=lookup_type.lower()
					
					if lookup_type == "back":
						return
					elif lookup_type == "quit":
						exit("user quit")
					elif lookup_type == "barcode":
						self.LookupByBarcode()
					elif lookup_type == "code":
						self.LookupByItemCode()
					elif lookup_type == "id":
						self.LookupByItemId()
					else:
						raise Exception("Invalid Option!")
					break
				except Exception as e:
					print(e)
	
	class ItemsMode:
		def __init__(self,parent):
			self.parent=parent
			while True:
				menu=input("""
	Quit|Back
	Lookup|Add
	Update|Delete
				: """)
				menu=menu.lower()
				if menu =="quit":
					exit("user quit")
				elif menu == "back":
					break
				elif menu == "update":
					self.parent.UpdateItem()
				elif menu == "lookup":
					searchType=input("barcode|item_code|id:")
					with Session(ENGINE) as session:
						results=[]
						if searchType == "barcode":
							barcode=input("barcode: ")
							results=session.query(TABLE.Item).filter(TABLE.Item.Barcode==barcode,TABLE.Item.StorageId==self.parent.defaultStorage).all()
						elif searchType == "item_code":
							item_code=input("item_code: ")
							results=session.query(TABLE.Item).filter(TABLE.Item.Code==item_code,TABLE.Item.StorageId==self.parent.defaultStorage).all()
						while True:
							try:
								which=input("There are {} results: ".format(len(results)))
								if len(results) == 0:
									break
								which=int(which)
								if which == -1:
									break
								else:
									for key in results[which].__table__.columns:
										if key.name == "CategoryId":
											category=session.query(TABLE.Category).filter(TABLE.Category.CategoryId==getattr(results[which],key.name)).first()
											for key in category.__table__.columns:
												print("Category",'\t',key.name,getattr(category,key.name),sep=" : ")
										print(key.name,getattr(results[which],key.name),sep=" : ")
										#get customfields
										cflist=session.query(TABLE.ItemCustomField).filter(TABLE.ItemCustomField.ItemId==getattr(results[which],'ItemId')).all()
									for cf in cflist:
										attr=session.query(TABLE.CustomField).filter(TABLE.CustomField.CustomFieldId==cf.CustomFieldId).first()															
										for k in cf.__table__.columns:
											if k.name == "Value":
												print(k,getattr(cf,k.name),sep=" : ")
												print(results[which].ItemId,k,getattr(attr,"Name"),sep=" : ")
							except Exception as e:
								print(e)
	class Util:
		def view_image(image_path):
			b=image.imread(image_path)
			plt.imshow(b)
			plt.show()
									
	def __init__(self):
		self.defaultStorage=2
		while True:
			menu=input("""
Items|List|Misc|Quit
setDefaultStorage
			: """)
			menu=menu.lower()
			if menu == "quit":
				break
			elif menu == "items":
				self.ItemsMode=self.ItemsMode(parent=self)
			elif menu == "list":
				pass
			elif menu == "setdefaultstorage":
				while True:
					try:
						default=input("default  storage: ")
						default=int(default)
						self.defaultStorage=default
						break
					except Exception as e:
						print(e)
#TABLE=
SystemMain()