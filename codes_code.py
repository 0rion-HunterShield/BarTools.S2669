from barcode import Code128,UPCA,EAN13,EAN8
from barcode.writer import ImageWriter
from PIL import Image
import matplotlib.pyplot as plt
import time,csv
from pathlib import Path
total=0

code_file=Path('/storage/3036-6438/Documents/newfile.txt')

if not code_file.exists():
    code_file=input("code_file: ")

with open(code_file,"r") as CSV:
    reader=csv.reader(CSV,delimiter=",")
    for num,code in enumerate(reader):
        total=num

with open(code_file,"r") as CSV:
    reader=csv.reader(CSV,delimiter=",")
    for num,code in enumerate(reader):
        try:
            try:
                code=code[0]
            except:
                code=input("line was empty code/skip/QUIT: ")
                if code == "QUIT":
                    exit("User Exit!")
                elif code == "skip" or code == '':
                    continue
            name=''
            msg="code:{}|code_length:{}|Of:{}/{}|CMDS: #ALT#: ".format(code,len(code),num+1,total)

            if len(code) == 8:
                t=''
                while t not in ['Code128','EAN','']:
                    t=input(msg.replace('#ALT#','Code128/EAN[Code128]/QUIT'))
                    if t == 'QUIT':
                        exit("user quit!")
                    if t in ['Code128','EAN']:
                        if t == 'Code128' or t == '':
                            c=EAN13(code,writer=ImageWriter())
                            name=c.save("{}.png".format(code))
                        else:
                            c=EAN8(code,writer=ImageWriter())
                            name=c.save("{}.png".format(code))
            elif len(code) == 12:
                t=input(msg.replace('#ALT#','UPCA/EAN[UPCA]/QUIT'))
                if t == 'QUIT':
                        exit("user quit!")
                while t.upper() not in ['UPCA','EAN','']:
                    t=input("UPCA/EAN/QUIT: ")
                    if t == 'QUIT':
                        exit("user quit!")
                if t.upper() == 'UPCA' or t == '':
                    c=UPCA(code,writer=ImageWriter())
                    name=c.save("{}.png".format(code))
                elif t.upper() == "EAN":
                    c=EAN13(code,writer=ImageWriter())
                    name=c.save("{}.png".format(code))
            else:
                c=Code128(code,writer=ImageWriter())
                name=c.save("{}.png".format(code))
            im=Image.open(name)
            plt.imshow(im)
            plt.show()
            plt.clf()
            im.close()
            time.sleep(1)
        except Exception as e:
            print(e)
