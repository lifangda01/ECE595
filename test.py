from keyboardCapture import keyCapture as key

k = key()
while 1:
    try:
        k.checkKey()
    except IOError:
        pass
    finally:
        pass
