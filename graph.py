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
            Piece.K: Piece.N,
            Piece.N: Piece.K,
        }
        mvQ = Moves(start)
        plmt = start
        while len(mvQ) > 0:
            mv = mvQ.pop()
            if abs(mv[0]) > rad or abs(mv[1]) > rad:
                continue
            plmt = Plmt(pieceDict[plmt.piece], mv)
            _, success = board.TryAdd(plmt)
            if success:
                mvQ.extend(Moves(plmt))
        return board

def main(rad: str = "100"):
    graph = Graph()
    board = graph.Generate(rad=int(rad))
    BoardImage(board).Draw()


if __name__ == "__main__":
    main(*sys.argv[1:])

