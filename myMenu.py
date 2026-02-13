class xmenu:
    def __init__(self):
        self.inpakt=False
        self.strmode=0
        self.strrdy=False
        self.inp=0
        self.stack=[]
        self.inpstr=''
        self.myip=0

    def prompt(self):
        self.strmode=0
        if self.myip !=0:
            print (self.myip,end=">")
        else:
            print ('??',end=">")
    
    def strdone(self):
        self.strrdy=False
        self.inpstr=''
        
    def mach(self,ch):
        print(ch,end='')
        if self.strmode:
            if ch=='#':
                print()
                self.prompt()
            elif ch=='\b':
                self.inpstr=self.inpstr[:-1]
            elif ch=='\n':
                print(f">{self.inpstr}<")
                if self.inpstr =='':
                    self.prompt()
                else:
                    self.strrdy=True
                    print(self.strmode,end=':')
            else:
                self.inpstr+=ch
            return  True
            
        if ((ch >= '0') and (ch <= '9')):
            if (self.inpakt):
                self.inp = self.inp * 10 + (ord(ch) - 48)
            else:
                self.inpakt = True
                self.inp = ord(ch) - 48
            return True
        self.inpakt=False
        if  ch==",":
            self.stack.append(self.inp)
        elif ch=="+":
            self.inp=self.inp+self.stack.pop()
            print('=',self.inp)
        elif ch=="-":
            self.inp=self.stack.pop()-self.inp
            print('=',self.inp)
        elif ch==".":
            inp=stack.pop()
            print('=',inp)
        elif ord(ch)==228:
            self.inpstr=''
            self.strmode=1
        elif ord(ch)==246:
            self.inpstr=''
            self.strmode=2              
        elif ord(ch)==252:
            self.inpstr=''
            self.strmode=3            
        else:
            return False
        return True