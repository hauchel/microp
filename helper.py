# some routines

class tast16():
    def __init__(self,conn,tadr=39):
        self.con=conn
        self.tadr=tadr
        
    def finn(self,b):
        if   b== 7: return 4
        elif b==11: return 3
        elif b==13: return 2
        elif b==14: return 1
        else:       return 0
    
    def taste(self):
        a=self.con.readfrom(self.tadr,1)
        if a[0]==0xF0: return 0
        #print ('\nis:',bitw(a[0]))
        self.con.writeto(self.tadr,bytes([0x0f]))
        a=self.con.readfrom(self.tadr,1)
        sp=self.finn(a[0] & 0xF) # 7 11 13 14
        #print ('\n0f spa:',bitw(a[0]),'=',sp)
        if sp==0: return 0
        self.con.writeto(self.tadr,bytes([0xf0]))
        b=self.con.readfrom(self.tadr,1)
        zl=self.finn(b[0]>>4)
        #print ('f0 zle:',bitw(b[0]),'=',zl)
        if zl==0: return 0
        return zl*4 + sp - 4