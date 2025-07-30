import curses
import copy
import math

boardscreen = None
ioscreen = None
board = []
freespaces = []
freenum = 3
REDFONT = BLUEFONT = GREENFONT = None
triedstates = []
pilenums = [0, 0, 0]
solutionfound = False
seenstates = []


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


def ismoveable(board, column, row):
    if row == len(board[column])-1:
        return True

    if fits(board[column][row], board[column][row+1]) and ismoveable(board, column, row+1):
        return True

    return False


def solve(board, freespaces, pilenums, ioscreen, startbar=0.0, endbar=100.0):
    global seenstates
    seenstates.append((copy.deepcopy(board), copy.copy(freespaces)))
    moves = getpossiblemoves(board, freespaces, pilenums)
    ioscreen.clear()
    ioscreen.addstr(str(startbar))
    ioscreen.refresh()
    for num, move in enumerate(moves):
        bardiff = endbar - startbar
        movebar = bardiff/len(moves)
        newboard = copy.deepcopy(board)
        newfreespaces = copy.deepcopy(freespaces)
        newpilenums = copy.deepcopy(pilenums)
        movecard(move, newboard, newfreespaces, newpilenums)
        seen = False
        for state in seenstates:    
            if boardequivalent(newboard, newfreespaces, state[0], state[1]):
                seen = True
                break
        if seen:
            continue
        
        if issolved(newboard, newfreespaces):
            return (True, [move])
        
        
        nextstep = solve(newboard, newfreespaces, newpilenums, ioscreen, startbar+movebar*num, startbar+movebar*(num+1))
        if nextstep[0]:
            nextstep[1].append(move)
            return nextstep
        
        
        

        

    return (False, [])

        





def getpossiblemoves(board, freespaces, pilenums):
    #moves are stored in the format of (columnfrom, depthfrom, columnto)
    #column 0-7 for normal board columns, 8 for free spaces, 9 for color piles, rose slot and dragon cleanups
    #for clearing up the dragons, columnfrom is 9 and depthfrom is 0-2 for R,G,B respectively
    normalmoves = []
    movestofreespace = []
    dragoncleanups = []
    movestopile = []

    dragonnums = [0]*3
    for card in freespaces:
        if card[0] == "0":
            findnum = "RGB".find(card[1])
            if findnum != -1:
                dragonnums[findnum] += 1

    for y, card in enumerate(freespaces):
        if card[0] == "X":
            continue
        cardcolor = "RGB".find(card[1])
        if pilenums[cardcolor] == int(card[0]) - 1:
            movestopile.append((8, y, 9))
        for movecolumn in range(8):
            if len(board[movecolumn]) == 0:
                normalmoves.append((8, y, movecolumn))
            elif fits(board[movecolumn][-1], card):
                normalmoves.append((8, y, movecolumn))

    for x, column in enumerate(board):
        for y, card in enumerate(column):
            if not ismoveable(board, x, y):
                continue
            if card == "R":
                movestopile.append((x, y, 9))
                continue
            cardcolor = "RGB".find(card[1])
            if card[0] == "0" and len(freespaces) < 3:
                    dragonnums[cardcolor] += 1
                    for i, num in enumerate(dragonnums):
                        if num == 4:
                            dragoncleanups.append((9, i, 9))
            if pilenums[cardcolor] == int(card[0]) - 1:
                movestopile.append((x, y, 9)) 
            for movecolumn in range(8):
                if len(board[movecolumn]) == 0:
                    normalmoves.append((x, y, movecolumn))
                elif fits(board[movecolumn][-1], card):
                    normalmoves.append((x, y, movecolumn))
            if y == len(column)-1 and len(freespaces) < 3:
                movestofreespace.append((x, y, 8))
    
    return movestopile + dragoncleanups + normalmoves + movestofreespace


def boardequivalent(board1, freespaces1, board2, freespaces2):
    takennums = []
    for column1 in board1:
        for x, column2 in enumerate(board2):
            if x in takennums:
                pass
            if column1 == column2:
                takennums.append(x)

    if set(takennums) != set([num for num in range(8)]):
        return False
    
    if set(freespaces1) != set(freespaces2):
        return False
    
    return True


def issolved(board, freespaces):
    for column in board:
        if len(column) != 0:
            return False
    for card in freespaces:
        if card[0] != "X":
            return False
    return True


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
        drawcard(screen, 2*x+11, 1, str(num)+colors[x])
    screen.refresh()



def movecard(move, board, freespaces, pilenums):
    #moves are stored in the format of (columnfrom, depthfrom, columnto)
    #column 0-7 for normal board columns, 8 for free spaces, 9 for color piles, rose slot and dragon cleanups
    #for clearing up the dragons, columnfrom is 9 and depthfrom is 0-2 for R,G,B respectively
    columnfrom, depthfrom, columnto = move
    movedcards = []
    if columnfrom in range(8):
        for x in range(len(board[columnfrom]) - depthfrom):
            movedcards.append(board[columnfrom].pop())
    elif columnfrom == 8:
        movedcards = [freespaces[depthfrom]]
        del freespaces[depthfrom]
    elif columnfrom == 9:
        color = "RGB"[depthfrom]
        for column in board:
            if len(column) == 0: continue
            if column[-1] == f"0{color}":
                column.pop()

        movedcards = [f"0{color}"]
    if columnto in range(8):
        while len(movedcards) > 0:
            board[columnto].append(movedcards.pop())
    elif columnto == 8:
        freespaces.append(movedcards[-1])
    elif columnto == 9:
        movecard = movedcards[-1]
        if movecard == "R":
            pass
        elif movecard[0] == "0":
            freespaces.append(f"X{movecard[1]}")
        else:
            colornum = "RGB".find(movecard[1])
            pilenums[colornum] += 1

            
        


def main(stdscr):
    global REDFONT, BLUEFONT, GREENFONT, ioscreen, boardscreen, board, pilenums, freespaces
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

    boardheight = 14
    boardwidth = 22

    boardscreen = stdscr.subwin(boardheight, boardwidth, 1, 1)
    boardscreen.border()
    
        
    ioborder = stdscr.subwin(20, 22, boardheight+1, 1)
    ioborder.border()
    ioscreen = ioborder.subwin(18, 20, boardheight+2, 2)
    ioscreen.scrollok(True)
    
    
    stdscr.refresh()

    inputboard(boardscreen, ioscreen)
    drawboard(boardscreen, board, freespaces, pilenums)
    boardscreen.refresh()
    stdscr.refresh()
    solution = solve(board, freespaces, pilenums, ioscreen)
    boardstepscreen = stdscr.subwin(boardheight, boardwidth, 1, boardwidth+1)
    curses.curs_set(False)
    if not solution[0]:
        ioscreen.addstr("no solution found")
    else:
        for num, step in enumerate(reversed(solution[1])):
            newboard = copy.deepcopy(board)
            newfreespaces = copy.deepcopy(freespaces)
            newpilenums = copy.deepcopy(pilenums)
            movecard(step, newboard, newfreespaces, newpilenums)
            drawboard(boardscreen, board, freespaces, pilenums)
            drawboard(boardstepscreen, newboard, newfreespaces, newpilenums)
            ioscreen.clear()
            ioscreen.addstr("#"*math.floor(20/len(solution[1])*num))
            ioscreen.refresh()
            board = newboard
            freespaces = newfreespaces
            pilenums = newpilenums
            ioscreen.getkey()
                

    

    

if __name__ == "__main__":
    curses.wrapper(main)
    



                

