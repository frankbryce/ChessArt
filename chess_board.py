#!/usr/bin/python3

from __future__ import annotations

from enum import Enum
import os
import sys

class Piece(Enum):
    P = 1
    N = 2
    B = 3
    R = 4
    Q = 5
    K = 6


Pos = tuple[int, int]
class Plmt:
    def __init__(self, piece: Piece, pos: Pos) -> None:
        self.piece = piece
        self.pstn = pos


class Board:
    def __init__(self, plmts: list[Plmt] = []) -> None:
        self.plmts = set(plmts)
        self.pstns = dict(zip(map(lambda p: p.pstn, plmts), plmts))
        self.minx, self.maxx, self.miny, self.maxy = 0, 0, 0, 0


    def _boundingBoxRecomp(self, x, y):
        self.minx = min(x, self.minx)
        self.maxx = max(x, self.maxx)
        self.miny = min(y, self.miny)
        self.maxy = max(y, self.maxy)


    def Add(self, plmt: Plmt) -> Board:
        if plmt.pstn in self.pstns:
            raise Exception(
                f"Position {plmt.pstn} already has a piece on it")

        self.plmts.add(plmt)
        self.pstns[plmt.pstn] = plmt
        self._boundingBoxRecomp(plmt.pstn[0], plmt.pstn[1])
        return self

    def Remove(self, plmt: Plmt) -> Board:
        if plmt in self.plmts:
            self.plmts.remove(plmt)
            del self.pstns[plmt.pstn]
            if (plmt.pstn[0] in (self.minx, self.maxx) or
                plmt.pstn[1] in (self.miny, self.maxy)):
                self.minx, self.maxx, self.miny, self.maxy = 0, 0, 0, 0
                for pstn in self.pstns:
                    self._boundingBoxRecomp(pstn[0], pstn[1])
        else:
            raise Exception(
                    f"Placement {plmt} is not on the Board")
        return self

    def Print(self) -> None:
        os.system('clear')
        for plmt in self.plmts:
            # "+ 1" is because the terminal seems to be 1 indexed
            x = self.maxx - (plmt.pstn[0] - self.minx) + 1
            y = self.maxy - (plmt.pstn[1] - self.miny) + 1
            sys.stdout.write(f"\033[{y};{x}H{plmt.piece.name}")
        sys.stdout.flush()


def main():
    board = Board()

    # pawns
    for x in range(8):
       board.Add(Plmt(Piece.P, (x, 1)))
    
    # rooks
    board.Add(Plmt(Piece.R, (0, 0)))
    board.Add(Plmt(Piece.R, (7, 0)))

    # knights
    board.Add(Plmt(Piece.N, (1, 0)))
    board.Add(Plmt(Piece.N, (6, 0)))

    # bishops
    board.Add(Plmt(Piece.B, (2, 0)))
    board.Add(Plmt(Piece.B, (5, 0)))

    # royalty
    board.Add(Plmt(Piece.Q, (3, 0)))
    board.Add(Plmt(Piece.K, (4, 0)))

    board.Print()

if __name__ == '__main__':
    main(*sys.argv[1:])
