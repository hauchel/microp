class makro():
    def __init__(self):
        print("Howdy", __name__)
        self.maktxt=['5555t','0p'] #overwritten
        self.maknum=[]
        self.makptr=[]
    
    def makinfo(self):
        print("Makro num",self.maknum,"ptr",self.makptr)
        
    def makget(self):
        while True:
            if self.maknum==[]: return None
            p=self.makptr[0]
            tx=self.maktxt[self.maknum[0]]
            #print(p,tx)
            if  p< len(tx):
                c=tx[p]
                self.makptr[0]+=1
                return c
            self.maknum.pop(0)
            self.makptr.pop(0)
    
    def maksel(self,n):     
        if self.maknum!=[]:
            if n==self.maknum[0] : return # kann nicht selbst aufrufen
        self.maknum.insert(0,n)
        self.makptr.insert(0,0)
        self.makinfo()
        
    def makstop(self):
        self.maknum=[]
        self.makptr=[]
        print("makstop")
    
    def makloop(self):
        if self.maknum !=[]: self.makptr[0]=0
            
    def makshow(self):
        i = 0
        for m in self.maktxt:
            print(f"{i:>3}  {m}<")
            i += 1
        
    def makread(self):
        self.maktxt = ['0!'] # gleuch Zeilennummer in Datei 
        try:
            with open("makros.txt", "r") as file:
                for line in file:
                    self.maktxt.append(line.rstrip('\n \r'))
        except Exception as inst:
            sys.print_exception(inst)      
        self.makshow()
