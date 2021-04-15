#!/usr/bin/python3.9

from __future__ import annotations

from collections.abc import Iterable
from board import *
from image import *

class Graph:
    def Generate(
            self,
            start: Plmt = Plmt(Piece.N, (0,0)),
            rad: int = 10) -> Board:
        board = Board()
        board.Add(start)
        pieceDict = {
            Piece.N: Piece.B,
            Piece.B: Piece.N,
        }
        def _mvs(last):
            mvs = list(Moves(last))
            return list(map(lambda m: (m, pieceDict[last.piece]), mvs))
        mvQ = _mvs(start)
        while len(mvQ) > 0:
            mv, piece = mvQ.pop()
            if abs(mv[0]) > rad or abs(mv[1]) > rad:
                continue
            plmt = Plmt(piece, mv)
            _, success = board.TryAdd(plmt)
            if success:
                mvQ.extend(_mvs(plmt))
        return board

def main(bRad: str = "100", pRad: str = "0"):
    graph = Graph()
    board = graph.Generate(rad=int(bRad))
    BoardImage(board, splot=Splotch(rad=int(pRad))).Draw()


if __name__ == "__main__":
    main(*sys.argv[1:])

