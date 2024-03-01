from shape import Shape
import sys, random

try:
    index = sys.argv.index("-m")+1
    if index == len(sys.argv):
        print("-m [value -> float]")
        sys.exit()
    m = sys.argv[index]
    m = float(m)
except:
    m = random.randint(0, 10)

shape = Shape(m)

shape.draw()

shape.update()

# curses.endwin()