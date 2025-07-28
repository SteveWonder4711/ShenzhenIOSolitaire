import curses


boardscreen = None
ioscreen = None
board = []
freespaces = []
freenum = 3
REDFONT = BLUEFONT = GREENFONT = None
triedstates = []
pilenums = [0, 0, 0]
roseslot = False



def inputboard(boardscreen, ioscreen):
    global board
    column = 0
    while column < 8:
        board.append([])
        while True:
            cardvalid = False
            card = ""
            input = ""
            while not cardvalid:
                boardscreen.move(len(board[-1])+3, column*2+1)
                input = boardscreen.getkey().upper()
                if len(card) == 0:
                    if input in "0123456789":
                        card += input
                        boardscreen.addstr(input)
                    elif input == "R":
                        card = "R"
                        cardvalid = True
                    elif input == "\n":
                        break
                    elif input == "D":
                        if len(board[-1]) > 0:
                            board[-1].pop()
                        elif len(board) > 1:
                            board.pop()
                            column -= 1
                        drawboard(boardscreen, board, freespaces, pilenums)
                elif len(card) == 1:
                    if input in "RGB":
                        card += input
                        cardvalid = True
                    elif input == "D":
                        card = ""
                        drawboard(boardscreen, board, freespaces, pilenums)

            if input == "\n":
                break
                
            board[-1].append(card)
            drawboard(boardscreen, board, freespaces, pilenums)
        column += 1

    
    



def fits(bottomcard, topcard):
    if topcard == "R" or bottomcard == "R":
        return False

    if bottomcard[0] == "0" or topcard[0] == "0":
        return False

    if (int(bottomcard[0]) == int(topcard[0]) + 1 and
        bottomcard[1] != topcard[1]
       ):
        return True

    return False


def ismoveable(column, row):
    if row == len(board[column])-1:
        return True

    if fits(board[column][row], board[column][row]) and ismoveable(column, row+1):
        return True

    return False


def getpossiblemoves(board):
    for x, column in enumerate(board):
        for y, card in enumerate(column):
            if not ismoveable(x, y):
                continue
            if y == len(column)-1 and len(freespaces) < freenum:
                print(f"card {card} at position {x, y} can be moved to free space")      
            for movecolumn in range(8):
                if fits(board[movecolumn][-1], card):
                    print(f"card {card} at position {x, y} can be moved to column {movecolumn}")

def cleanboard(board):
    cleaning = True
    while cleaning:
        cleaning = False
        for x, column in enumerate(board):
            for y, card in enumerate(column):
                if not ismoveable(x, y):
                    continue
                if card == "R":
                    roseslot = True
                    column.remove(card)
                    cleaning = True
                    continue
                
                

def drawcard(screen, x, y, card):
    color = REDFONT
    if card == "R":
        color = REDFONT
    elif card[1] == "R":
        color = REDFONT
    elif card[1] == "B":
        color = BLUEFONT
    elif card[1] == "G":
        color = GREENFONT
    
    screen.addstr(y, x, str(card[0]), color)
    

def drawboard(screen, board, freespaces, pilenums):
    screen.clear()
    screen.border()
    colors = ["R", "G", "B"]
    for x, column in enumerate(board):
        for y, card in enumerate(column):
            drawcard(screen, 2*x+1, y+3, card)

    for x, card in enumerate(freespaces):
        drawcard(screen, 2*x+1, 1, card)

    for x, num in enumerate(pilenums):
        if num == 0:
            continue
        drawcard(screen, 2*x+11, 1, num+colors[x])


def main(stdscr):
    global REDFONT, BLUEFONT, GREENFONT, ioscreen, boardscreen, board
    #Red Cards :3
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    REDFONT = curses.color_pair(1)
    #Blue Cards :3
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    BLUEFONT = curses.color_pair(2)
    #Green Cards :3
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    GREENFONT = curses.color_pair(3)
    stdscr.clear()
    stdscr.border()

    stdscr.keypad(False)

    #curses.curs_set(False)
    boardheight = 14
    boardwidth = 22

    boardscreen = stdscr.subwin(boardheight, boardwidth, 1, 1)
    boardscreen.border()

    ioscreen = stdscr.subwin(20, 22, boardheight+1, 1)
    ioscreen.border()
    ioscreen.scrollok(True)
    
    stdscr.refresh()

    inputboard(boardscreen, ioscreen)
    drawboard(boardscreen, board, freespaces, pilenums)
    boardscreen.refresh()
    stdscr.refresh()
    while True:
        curses.napms(500)
    

if __name__ == "__main__":
    curses.wrapper(main)
    print(board)

                

