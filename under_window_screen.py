
import time
import win32gui
import win32ui
from ctypes import windll
from PIL import Image

hwnd = win32gui.FindWindow(None, 'Persona 5 Royal')

# Change the line below depending on whether you want the whole window
# or just the client area. 
t = time.time()
#left, top, right, bot = win32gui.GetClientRect(hwnd)
windll.user32.SetProcessDPIAware()
left, top, right, bot = win32gui.GetWindowRect(hwnd)
w = right - left
h = bot - top

hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()

saveBitMap = win32ui.CreateBitmap()
saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

saveDC.SelectObject(saveBitMap)

# Change the line below depending on whether you want the whole window
# or just the client area. 
#result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)

result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
print(result)

bmpinfo = saveBitMap.GetInfo()
bmpstr = saveBitMap.GetBitmapBits(True)

im = Image.frombuffer(
    'RGB',
    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
    bmpstr, 'raw', 'BGRX', 0, 1)

win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)

if result == 1:
    #PrintWindow Succeeded
    print(time.time()-t)
    im=im.crop((800, 1100, 1700, 1300))
    im.resize((450, 100))
    print(time.time()-t)
    im.save("test.png")
    print(time.time()-t)