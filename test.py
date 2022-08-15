from paddleocr import PaddleOCR
import time
from PIL import Image, ImageTk, ImageDraw
import tkinter, win32api, win32con, pywintypes
import imagesize
ocr = PaddleOCR(use_angle_cls=True, lang='en')

 
t = time.time()
res = ocr.ocr('./example/images/test2.png', cls=True)
#print(res)
print(time.time()-t)


root = tkinter.Tk()

width, height = imagesize.get('./example/images/test2.png')
img = Image.new('RGBA', (width, height), (255, 0, 0, 0))

draw = ImageDraw.Draw(img)
for i in res:
    print(i[0][0])
    draw.text((i[0][0][0], i[0][0][1]), i[1][0], fill=(255, 0, 0))

test = ImageTk.PhotoImage(img)
label = tkinter.Label(image=test, bg='white')#text='Text on the screen', font=('Times New Roman','80'), fg='black', bg='white')
label.master.overrideredirect(True)
label.master.geometry("+250+250")
label.master.lift()
label.master.wm_attributes("-topmost", True)
label.master.wm_attributes("-disabled", True)
label.master.wm_attributes("-transparentcolor", "white")

hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))

# The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)

label.pack()
print('-')
r = 0
def handle(event):
    print('---')
label.bind('<Tab>', handle)
while True:
    label.update()
    time.sleep(1)
    width, height = imagesize.get('./example/images/test2.png')
    img3 = Image.new('RGBA', (width, height), (255, 0, 0, 0))

    draw = ImageDraw.Draw(img3)
    
    draw.text((10,10), str(r), fill=(255, 0, 0))
    img3 =  ImageTk.PhotoImage(img3)
    label.configure(image=img3)
    #label.image = img3 
    #label.im = img.rotate(10)
    #label.master.geometry("+"+str(r) +"+"+str(r))
    r +=5
    print(r)
    label.update()
label.mainloop()