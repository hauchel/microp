import ssd1306
class disp():
    def __init__(self, con):
        self.disp = ssd1306.SSD1306_I2C(128, 64, con)
        self.disp.rotate(True)
        self.disp.text(__name__, 0, 0, 1)
        self.disp.show()
        self.oldtx = [''] * 6
        self.scale=3
        # 8x8 Bitmap
        self.digits = {
         '0': [0x3C,0x66,0x6E,0x76,0x66,0x66,0x3C,0x00],
         '1': [0x18,0x38,0x18,0x18,0x18,0x18,0x7E,0x00],
         '2': [0x3C,0x66,0x06,0x1C,0x30,0x66,0x7E,0x00],
         '3': [0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00],
         '4': [0x0C,0x1C,0x3C,0x6C,0x7E,0x0C,0x0C,0x00],
         '5': [0x7E,0x60,0x7C,0x06,0x06,0x66,0x3C,0x00],
         '6': [0x1C,0x30,0x60,0x7C,0x66,0x66,0x3C,0x00],
         '7': [0x7E,0x66,0x06,0x0C,0x18,0x18,0x18,0x00],
         '8': [0x3C,0x66,0x66,0x3C,0x66,0x66,0x3C,0x00],
         '9': [0x3C,0x66,0x66,0x3E,0x06,0x0C,0x38,0x00],
         ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
         '.': [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x00],
         'A': [0x18,0x3C,0x66,0x66,0x7E,0x66,0x66,0x00],
         'V': [0x66,0x66,0x66,0x66,0x66,0x3C,0x18,0x00]
        }

    def fill(self, col):
        self.disp.fill(col)
        self.disp.show()

    def zeigtx(self, tx): # tx list 0..5
        di = False
        for i in range(6):
            if tx[i] != self.oldtx[i]:
                di = True
                self.oldtx[i] = tx[i]
        if di:
            self.disp.fill(0)
            for i in range(6):
                self.disp.text(tx[i], 0, i * 10, 1)
            self.disp.show()
    
    def draw_char(self,ch, x, y, scale=3):
        if ch in self.digits:
            bitmap = self.digits[ch]
        else:
            bitmap=self.digits['.']
        for row in range(8):
            bits = bitmap[row]
            for col in range(8):
                if bits & (1 << (7 - col)):
                    self.disp.fill_rect(
                        x + col * scale,
                        y + row * scale,
                        scale,
                        scale,
                        1
                    )
                    
    def draw_text(self,text, x=0, y=0):
        spacing=2
        for ch in str(text):
            self.draw_char(ch, x, y, self.scale)
            x += (8 * self.scale) + spacing
