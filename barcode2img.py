import tarfile
from PIL import Image
from barcode import UPCA
from barcode import EAN13,EAN8,Code128,Code39

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
import requests

DB=True
PROMPT_DB=False

p='/storage/emulated/0/Download/Database/MobileInventoryDB_13-12-2023_01-26-13.db3'
if DB:
	BASE=automap_base()
	filename=None
	if not PROMPT_DB:
		filename=Path(p)
	else:
		while True:
			q=input("DB Path|quit: ")
			if q.lower() == "quit":
				exit()
			else:
				if Path(q).exists():
					filename=Path(q)
					break
		
	#filename=Path("/storage/emulated/0/Download/MBI/MobileInventoryDB_09-12-2023_13-56-08.db3")
	if not filename.exists():
		raise Exception("DOES NOT EXIST:"+str(filename.exists())+":"+str(filename))
	dbfile="sqlite:///"+str(filename)
	print(dbfile)
	ENGINE=create_engine(dbfile)
	BASE.prepare(autoload_with=ENGINE)
	TABLE=BASE.classes


d=Path('codes')
if not d.exists():
	d.mkdir()
else:
	rmtree(d)
	d.mkdir()
codefile=Path('/storage/emulated/0/Download/newfile.txt')
while not codefile.exists():
	q=input('codefile Path|quit: ')
	if q.lower() == "quit":
		exit()
	codefile=Path(q)

date=datetime.now().strftime('%m.%d.%Y-%H.%M.%S')
package=Path('/storage/emulated/0/Documents/code2Img_{date}.zip'.format(date=date))
logPath=d/Path('error.log')
csvout='counts.csv'
l={}
with logPath.open('w') as log:
	with codefile.open('r') as code:
		with Path('log-counts.json').open('w+') as counts:
			reader=csv.reader(code,delimiter=',')
			for num,c in enumerate(reader):
				for code in [UPCA,Code39,EAN13,EAN8,Code128]:
					try:
						if len(c) > 0:
							if c[0] in l.keys():
								if len(c) == 1:
									l[c[0]]['qty']+=1
								else:
									try:
										l[c[0]]['qty']+=float(c[1])
									except Exception as e:
										l[c[0]]['qty']+=1
										print(e,"adding 1 instead")
							else:
								if len(c) == 1:
									l[c[0]]={'qty':1}
								else:
									try:
										#use third column index 2 for operator on value in stored
										l[c[0]]['qty']+=float(c[1])
									except Exception as e:
										l[c[0]]['qty']+=1
										print(e,"adding 1 instead")
								if DB:
									with Session(ENGINE) as session:
										r=TABLE.Item
										result=session.query(r).filter(r.Barcode==c[0]).first()
										if result:
											l[c[0]]['name']=result.Name
										else:
											l[c[0]]['name']='UNKNOWN'
							if code == Code39:
								print('code39 without checksum')
								cde=code(c[0],writer=ImageWriter(),add_checksum=False)
							else:
								cde=code(c[0],writer=ImageWriter())	
							print('working on',c,"using",code,'as',cde)
							cde.save(d/Path(c[0]))
						break
					except Exception as e:
						log.write(str(e)+"\n")
						log.write(repr(e)+"\n")
						log.write("barcode:{}".format(c)
						)
						log.write("line no.:{}".format(num))
						print(e)
			counts.write(json.dumps(l))
			
with Path(csvout).open("w+") as cv:
		writer=csv.writer(cv,delimiter=';')
		if DB:
			writer.writerow(['barcode','upca','qty','name'])
		else:
			writer.writerow(['barcode','upca','qty'])
		
		for barcode in l.keys():
			line=[]
			line.append(barcode)
			line.append(barcode[:-1])
			line.append(l[barcode]['qty'])
			if DB:
				line.append(l[barcode]['name'])	
			writer.writerow(line)
			
with zipfile.ZipFile(package,"w") as z:
	z.write(codefile)

	z.write('log-counts.json')
	Path('log-counts.json').unlink()
	
	
	
	z.write(csvout)
	Path(csvout).unlink()
	if DB:
		print('adding:',filename)
		#z.write(filename)

	z.write(d)
	for root,dirs,files in os.walk(d):
			p=Path(root)
			for dir in dirs:
				d=Path(dir)
				z.write(str(p/d))
			for n in files:
				F=Path(n)
				z.write(str(p/F))
	shutil.rmtree(d)
			
	z.write(Path(__file__))
	try:
		fg=requests.get('https://github.com/0rion-HunterShield/BarTools.S2669/blob/main/newtextfile.py')
		entry=Path('newtextfile.py')
		with entry.open('wb') as o:
			data=json.loads(fg.content.decode('utf-8'))
			f='\n'.join(data['payload']['blob']['rawLines'])
			o.write(f.encode())
		z.write(entry)
		fg=requests.get('https://github.com/0rion-HunterShield/BarTools.S2669/blob/main/barcode2img.py')
		entry=Path('barcode2img.py')
		with entry.open('wb') as o:
			data=json.loads(fg.content.decode('utf-8'))
			f='\n'.join(data['payload']['blob']['rawLines'])
			o.write(f.encode())
		z.write(entry)
	except Exception as e:
		log.write(str(e)+'/n')
		log.write(repr(e)+'/n')
