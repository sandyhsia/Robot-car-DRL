import msvcrt

print("...")

while True:
    if ord(msvcrt.getch()) == 27:
        break

