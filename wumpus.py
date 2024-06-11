# Use a SAT solver to solve the wumpus world
import random
import sys
from pysat.solvers import Glucose3
from itertools import groupby

class WumpusWorld():

    _tokensDescr = { "S": "There is a smell in this cell",
            "M": "There is a monster in this cell",
            "B": "There is a breeze in this cell",
            "H": "There is a hole in this cell",
            "G": "Gold !"}

    def __init__(self, size=10):
        self._size = size
        self._grid = [[[]  for _ in range(size)] for _ in range(size)] # Don't try to access directy to this !
        self._visited = [[False for _ in range(size)] for _ in range(size)]
        self._tokens = list(WumpusWorld._tokensDescr.keys())
        self._x, self._y = (0, 0)
        self._visited[self._x][self._y] = True
        self._nbMoves = 0
        self._generateGrid()

    def _generateGrid(self):
        print(self._grid)
        i = 0
        while i < self._size:
            x, y = random.randint(1, self._size-1), random.randint(1, self._size-1)
            if "M" in self._grid[x][y] or "H" in self._grid[x][y] or "G" in self._grid[x][y]:
                continue
            token = "MH"[random.randint(0,1)] if i > 0 else "G"
            self._grid[x][y].append(token)
            if token != "G":
                effect = {"M":"O", "H":"B"}[token]
                for (xx, yy) in self._around((x,y)):
                    if effect not in self._grid[xx][yy]:
                        self._grid[xx][yy].append(effect)
            i += 1
    
    def _inBound(self, x):
        if x < 0 or x >= self._size: return False
        return True

    def _around(self, coord):
        (x,y) = coord
        toret = []
        for (dx,dy) in [(-1,0), (0,1), (1,0), (0,-1)]:
            if self._inBound(dx+x) and self._inBound(dy+y):
                toret.append((dx+x, dy+y))
        return toret            
    
    def _printSolution(self): # Do not use this!
        for x in range(self._size):
            for y in range(self._size):
                print("".join(self._grid[x][y]).ljust(4), end="")
            print()
    
    ########################################
            
    def getTokens(self):
        return self._tokens
    
    def tokenDescription(self, token):
        if token not in WumpusWorld._tokenDescr:
            return "Not a token"
        return WumpusWorld._tokenDescr[token]

    def getPosition(self):
        return self._x, self._y
    
    def moveHero(self, x, y):
        ''' Move the hero to coordinates (x,y). The new position must be one cell away (no diagonals) from the current pos. '''
        if x < 0 or y < 0 or x >= self._size or y >= self._size:
            print("ERROR IN MOVE")
            sys.exit(1)
        ok = False
        for (dx,dy) in [(-1,0), (0,1), (1,0), (0,-1)]:
            if (self._x + dx == x) and (self._y + dy == y):
                ok = True
                break
        if not ok:
            print("ERROR IN MOVE")
            sys.exit(1)

        self._x, self._y = x, y
        self._visited[self._x][self._y] = True
        self._nbMoves += 1
        for o in self._grid[self._x][self._y]:
            if o in ["G", "M", "H"]:
                return o
        return None

    def __str__(self):
        toret =  f"Position: ({self._x}, {self._y})\n"
        toret += f"Nb Moves: {self._nbMoves}\n\n"
        for x in range(self._size):
            for y in range(self._size):
                toret += "".join(self._grid[x][y] if self._visited[x][y] else ["??"]).ljust(4)
            toret += "\n"
        return toret

    
    def observe(self):
        '''Returns the observations in this cell'''
        return self._grid[self._x][self._y].copy()


class Joueur(): # Your class must inherit from it

    global_tableau = []

    def __init__(self, size = 10):
        self._wumpus = WumpusWorld(size)
        self._observations = [[[None]  for _ in range(size)] for _ in range(size)]
        self._size = size

    def varToStr(self,symbol, coord):
        encodage = {"M":1,"O": 2,"H": 3,"B":4,"G":5}
        return encodage[symbol] * 100 + coord[0] *10 + coord[1]

    def printConstraint(self,symbol1, symbol2, coord):

        for (x,y) in self._wumpus._around(coord):
            self.global_tableau.append([-self.varToStr(symbol1,coord),self.varToStr(symbol2,(x,y))])


    def printConstraintNeg(self,symbol1, symbol2, coord):

        for (x,y) in self._wumpus._around(coord):
            self.global_tableau.append([self.varToStr(symbol1, coord), -self.varToStr(symbol2,(x,y))])


    def printExclusionConstraint(self,symbol1, symbol2, coord):
        self.global_tableau.append([-self.varToStr(symbol1,coord),-self.varToStr(symbol2,coord)])
        self.global_tableau.append([-self.varToStr(symbol2,coord), -self.varToStr(symbol1,coord)])


    def doAllConstraints(self,coord):
        self.printConstraint("H", "B", coord) 
        self.printConstraint("M", "O", coord) 
        self.printConstraintNeg("O", "M", coord) 
        self.printConstraintNeg("B", "H", coord) 
        self.printExclusionConstraint("M","H",coord) 
        self.printExclusionConstraint("G","H",coord)
        self.printExclusionConstraint("G","M",coord)

        #On ajout à nos règles le fait qu'il n'y a aucun éléments en 0,0
        self.global_tableau.append([-self.varToStr("M",(0,0))])
        self.global_tableau.append([-self.varToStr("O",(0,0))])
        self.global_tableau.append([-self.varToStr("B",(0,0))])
        self.global_tableau.append([-self.varToStr("H",(0,0))])



    def testSolver(self,clausetest):
        solver = Glucose3()
        for clause in self.global_tableau:
            solver.add_clause(clause)

        solver.add_clause(clausetest)
        sat = solver.solve()
        solver.delete()
        if sat:
            return True
        else:
            return False



    def solve(self):
        print(self._wumpus._printSolution())

        ## Now prints all the constaints
        for x in range(self._size):
            for y in range(self._size):
                self.doAllConstraints((x,y))

        steps = 0
        while steps < 1500:

            #On print la carte
            print(self._wumpus)

            possibleMoves = []

            # on obtient les coordonnées du joueur
            x, y = self._wumpus.getPosition()
            print("Position joueur :", x, y)

            #On test les coordonnées pour gauche, droite, bas, haut
            for (dx_c, dy_c) in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                # On vérifie que notre IA est toujours dans la grille
                if x + dx_c >= 0 and y + dy_c >= 0 and x + dx_c < self._size and y + dy_c < self._size:
                    clause = [self.varToStr("M", (x + dx_c, y + dy_c))]
                    res = self.testSolver(clause)

                    clause2 = [self.varToStr("H", (x + dx_c, y + dy_c))]
                    res2 = self.testSolver(clause2)

                    if res == False and res2 == False:
                        print("Case possible :", (x + dx_c, y + dy_c))
                        possibleMoves.append((x + dx_c, y + dy_c))
                    else:
                        print("Possibilité de monstre ou de trou pour la case",x + dx_c," ", y + dy_c)

                    #On essaye de prendre des risques pour ne pas rester bloqué (s'active à partir du steps 600)
                    if self._observations[x][y] == ['O'] or self._observations[x][y] == ['B']:
                        if self._observations[x+dx_c][y+dy_c] == [None]:
                            liste_points_autour = self._wumpus._around((x+dx_c,y+dy_c))
                            nb_point_dangereux_autour = 0
                            for coord_target in liste_points_autour:
                                x_target,y_target = coord_target
                                if self._observations[x_target][y_target] == ['O'] or self._observations[x_target][y_target] == ['B'] or self._observations[x_target][y_target] == ['OB']:
                                    nb_point_dangereux_autour = nb_point_dangereux_autour + 1
                            if nb_point_dangereux_autour == 1:
                                if steps>600:
                                    possibleMoves.append((x + dx_c, y + dy_c))

                    


                
            assert len(possibleMoves) > 0
            print("moves possible : ",possibleMoves)
            move = random.choice(possibleMoves)
            x, y = move
            tokens = self._wumpus.moveHero(x, y)

            x, y = self._wumpus.getPosition()
            self._observations[x][y] = self._wumpus.observe()
            print("Observations sur la case", x,y ,": ", self._wumpus.observe())
            obs = self._wumpus.observe()

            if 'B' in obs:
                self.global_tableau.append([self.varToStr("B",(x,y))])
                print("on pose une clause pour le vent ! ")
            if 'O' in obs:
                self.global_tableau.append([self.varToStr("O",(x,y))])
                print("on pose une clause pour l'odeur ! ")

            if 'M' in obs:
                print("Dead")
                sys.exit(0)
            if 'H' in obs:
                print("Dead")
                sys.exit(0)

            if obs == []:
                print("ya rien sur la case")
                self._observations[x][y] = self._wumpus.observe()
                self.global_tableau.append([-self.varToStr("M",(x,y))])
                self.global_tableau.append([-self.varToStr("H",(x,y))])
                self.global_tableau.append([-self.varToStr("B",(x,y))])
                self.global_tableau.append([-self.varToStr("O",(x,y))])

            if tokens is not None and "G" in tokens:
                print("I FOUND THE GOLD!!!")
                self._wumpus._printSolution()
                sys.exit(0)
            steps += 1

            for x in range(self._size):
                for y in range(self._size):
                    print(self._observations[x][y])

            print("-----------------------------------------")

wumpus = WumpusWorld()
Joueur().solve()
