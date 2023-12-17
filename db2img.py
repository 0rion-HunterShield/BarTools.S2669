import tarfile
from PIL import Image
from barcode import UPCA
from barcode import EAN13,EAN8,Code128
from collections import OrderedDict
from barcode.writer import ImageWriter
from pathlib import Path
import csv,json,os
from shutil import rmtree
from datetime import datetime
import zipfile

import barcode,qrcode,os,sys,argparse
from datetime import datetime,timedelta
import zipfile,tarfile,shutil
import base64
from ast import literal_eval
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base as dbase
from sqlalchemy.ext.automap import automap_base
from pathlib import Path
import tempfile
DB=True
d=Path('codes')
if not d.exists():
	d.mkdir()
else:
	rmtree(d)
	d.mkdir()

codefile=Path('newfile.txt')

from tkinter import filedialog
tempdir=Path(tempfile.mkdtemp())
p=filedialog.askopenfilename()
#print(p)
#exit(p)
if p not in ['','.','..','/',None,-1]:
	if isinstance(p,tuple):
		if len(p) <= 0:
			exit("Please Provide a MobileInventoryPro *.bck Backup File!")
	backup_zip=Path(p)
else:
	if len(sys.argv) > 0:
		backup_zip=Path(sys.argv[1])
	else:
		exit("Please Provide a MobileInventoryPro *.bck Backup File!")

print(backup_zip,backup_zip.exists(),tempdir)
if backup_zip.exists():
	with open(tempdir/Path(backup_zip.name),"wb") as out,open(backup_zip,"rb") as ifile:
		while True:
			data=ifile.read(1024*1024)
			if not data:
				break
			out.write(data)

	z=zipfile.ZipFile(tempdir/Path(backup_zip.name),'r')
	z.extractall(tempdir)
	dbDir=tempdir/Path("Database")
	dbName=''
	for l in dbDir.iterdir():
		print(l)
		if l.suffix == '.db3':
			dbName=Path(l).absolute()
			break
	if dbName == '':
		raise Exception("dbName cannot be ''")
	print(dbName,"System Database")
else:
	dbDir=''
	dbName="MIB_ORIG.db"
AUTOBASE=automap_base()
engine=create_engine("sqlite:///{}".format(dbName))
AUTOBASE.prepare(engine,reflect=True)
TABLES_MIP=AUTOBASE.classes

date=datetime.now().strftime('%m.%d.%Y')
package=Path('allcodes_in_db.zip'.format(date=date))
logPath=d/Path('error.log')
csvout='counts.csv'
l={}
with logPath.open('w') as log,open(codefile,"w+") as cfile:
	with Path(csvout).open("w+") as cv:
		writer=csv.writer(cv,delimiter=';')
		writer.writerow(['barcode','item_code','name','qty','price','note','ImagePath'])
		with Session(engine) as session:
			with Path('log-counts.json').open('w+') as counts:
				cwriter=csv.writer(cfile,delimiter=";")
				cwriter.writerow(["barcode-processed",])
				with Session(engine) as session:
					results=session.query(TABLES_MIP.Item).all()
					results_count=len(results)
					for num,result in enumerate(results):
						for code in [UPCA,EAN13,EAN8,Code128]:
							c=result.Barcode
							if c:
								cwriter.writerow([result.Barcode,])
								try:
									if c != '':
										if c in l.keys():
											l[c]['qty']+=1
										else:
											l[c]=OrderedDict()
											l[c]['barcode']=c
											l[c]['item_code']=result.Code
											l[c]['name']=result.Name
											l[c]['qty']=1
											l[c]['price']=result.Price
											l[c]['note']=result.Note
											if result.ImagePath:
												l[c]['ImagePath']=str(Path(str(tempdir)[1:])/Path("Images")/Path(Path(result.ImagePath).name))
											else:
												l[c]['ImagePath']=''
											

											#might create itemcodes section as well
											if code == UPCA:
												cde=code(c,writer=ImageWriter())
												cde.save(d/Path(c))
											print("working on {} using {} at {}/{}".format(c,code,num,results_count))
											if 'barcode' in l[c].keys():
												writer.writerow([l[c][i] for i in l[c].keys()])
										break

								except Exception as e:
									log.write(str(e)+"\n")
									log.write(repr(e)+"\n")
									log.write("barcode:{}".format(c)
									)
									log.write("line no.:{}".format(num))
									print("working on {}/{} Error: '{}'".format(num,results_count,e))
							else:
								print("skipping {}/{}\n".format(num,results_count))	
								log.write("skipping {}/{}\n".format(num,results_count))	

				counts.write(json.dumps(l))
			
with zipfile.ZipFile(package.name,"w") as z:
	if codefile.exists():
		z.write(codefile)

	if Path('log-counts.json').exists():
		z.write('log-counts.json')
		Path('log-counts.json').unlink()
	
	
	if Path(csvout).exists():
		z.write(csvout)
		Path(csvout).unlink()
	if DB:
		print('adding:',dbName)
		z.write(dbName)

	z.write(d)
	for root,dirs,files in os.walk(d):
			p=Path(root)
			for dir in dirs:
				d=Path(dir)
				z.write(str(p/d))
			for n in files:
				F=Path(n)
				z.write(str(p/F))

	z.write(tempdir)
	for root,dirs,files in os.walk(tempdir):
			p=Path(root)
			for dir in dirs:
				dill=Path(dir)
				z.write(str(p/dill))
			for n in files:
				F=Path(n)
				z.write(str(p/F))

	shutil.rmtree(tempdir)
			
	z.write(Path(__file__))
	
