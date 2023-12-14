
from pathlib import Path
import csv
from barcode import UPCA,Code39,EAN8,EAN13
from barcode.writer import ImageWriter

codefile=Path('/storage/emulated/0/Download/newfile.txt')
if not codefile.exists():
    codefile=Path(codefile.name)
cmd=''
cmd_str=''
mode='w'

while True:
    mode=input("file open mode[a -> 'append',w -> 'new file']: ")
    if mode.lower() in ['a','w','w+']:
        break
    else:
        print("invalid mode!")
error_log=Path("NewTextFile.py.log")
with open(codefile.parent/error_log,"w+") as log:
    with open(codefile,mode) as ifile,open(str(codefile).replace(".txt","Code39.txt"),mode) as cd39:
        writers={}
        writers['UPCA/EAN13']=csv.writer(ifile,delimiter=";")
        writers['Code39/EAN8']=csv.writer(cd39,delimiter=";")
        writers['UPCA/EAN13'].writerow(['UPCA/EAN13',])
        writers['Code39/EAN8'].writerow(['Code39/EAN8',])
        while True:
            cmd=input("UPCA|Code39|EAN8/13|Quit{}:".format(cmd_str))
            for codec in [UPCA,Code39,EAN8,EAN13]:
                if cmd.lower() in ["quit"]:
                    exit("User quit!")
                elif cmd == '':
                      continue
                else:
                    try:
                        if codec in [UPCA,EAN13]:
                            c=codec(cmd,writer=ImageWriter())
                            line=[c,]
                            writers['UPCA/EAN13'].writerow(line)
                            break
                        elif codec in [Code39,EAN8]:
                            if codec == Code39:
                                c=codec(cmd,writer=ImageWriter(),add_checksum=False)
                            elif codec == EAN8:
                                c=codec(cmd,writer=ImageWriter())

                            line=[c,]
                            writers['Code39/EAN8'].writerow(line)
                            break
                    except Exception as e:
                        print(e)
                        log.write("+=Entry Start=+\n")
                        log.write(str(e)+"\n")
                        log.write(repr(e)+"\n")
                        log.write("Attempted Entry for CODE: {}\n".format(cmd))
                        log.write("=+Entry End+=\n")

