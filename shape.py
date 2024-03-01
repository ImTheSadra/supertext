import math, os
import curses

class Shape:
    n = [1, 1, 1]
    m = 0
    a = 1
    b = 1
    dtext = []
    def __init__(self, m:float) -> None:
        window = curses.initscr()
        window.refresh()
        self.m = m
        self.width = curses.COLS//3
        self.height = curses.LINES//3
        for j in range(self.height):
            self.dtext.append([])
            for i in range(self.width):
                self.dtext[j].append(" ")
        curses.endwin()

    def shupershape(self, angle:float):
        parts = [
            math.pow(abs((1/self.a)*math.cos(angle*self.m/4)),self.n[1]),
            math.pow(abs((1/self.b)*math.sin(angle*self.m/4)),self.n[2])
        ]
        parts.append(
            self.n[0]*math.sqrt(parts[0]+parts[1])
        )

        if parts[2] == 0:return 0

        return 1 / parts[2]
    
    def draw(self):
        text = self.dtext.copy()

        dr = min([self.width, self.height])/2
        
        for angle in range(0, int((math.pi*2)*10), 1):
            angle = angle / 10
            r  = self.shupershape(angle)
            x  = dr * r * math.cos(angle);
            x += self.width/2.5
            y  = dr * r * math.sin(angle);
            y += self.height/2

            try:text[round(y)][round(x)] = "#"
            except:pass

        self.text = text
    
    def update(self):
        print()
        for j, line in enumerate(self.text):
            for i, char in enumerate(line):
                print(char, end="")
            print()

    def main(self):
        while True:
            os.system("clear")
            self.draw()
            self.update()