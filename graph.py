#!/usr/bin/python3.9

from __future__ import annotations

from collections.abc import Iterable
from board import *
from image import *

class Graph:
    def __init__(
            self,
            nxt: dict[Piece, Piece] = {
                Piece.N: Piece.B,
                Piece.B: Piece.N,
            },
            rad: int = 100) -> None:
        self.rad = rad
        self.nxt = nxt

    def Generate(
            self,
            start: Plmt = Plmt(Piece.N, (0,0))) -> Board:
        board = Board()
        board.Add(start)
        def _mvs(last):
            mvs = list(Moves(last))
            return list(map(lambda m: (m, self.nxt[last.piece]), mvs))
        mvQ = _mvs(start)
        while len(mvQ) > 0:
            mv, piece = mvQ.pop()
            if abs(mv[0]) > self.rad or abs(mv[1]) > self.rad:
                continue
            plmt = Plmt(piece, mv)
            _, success = board.TryAdd(plmt)
            if success:
                mvQ.extend(_mvs(plmt))
        return board


def main(bRad: str = "100", pRad: str = "0"):
    graph = Graph(rad=int(bRad))
    board = graph.Generate()
    BoardImage(board, splot=Splotch(rad=int(pRad))).Draw()


if __name__ == "__main__":
    main(*sys.argv[1:])

