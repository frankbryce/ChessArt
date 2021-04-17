#!/usr/bin/python3.9

from __future__ import annotations

from collections.abc import Iterable
from board import *
from image import *
from typing import Callable

def DefaultPosSrtKey(pos: Pos) -> float:
    ret = abs(pos[0]) + abs(pos[1])
    if pos[0] > pos[1]:
        ret += 0.1
    else:
        ret -= 0.1
    return ret

class Graph:
    def __init__(
            self,
            nxt: dict[Piece, Piece] = {
                Piece.N: Piece.B,
                Piece.B: Piece.N,
            },
            branch: int = 1,
            rad: int = 100,
            posSrtKey: Callable[Pos, float] = DefaultPosSrtKey) -> None:
        self.branch = branch
        self.nxt = nxt
        self.posSrtKey = posSrtKey
        self.rad = rad

    def Generate(
            self,
            start: Plmt = Plmt(Piece.N, (0,0))) -> Board:
        board = Board()
        board.Add(start)
        def _mvs(last):
            # only return positions that aren't already on the board
            mvs = filter(lambda mv: not board.Check(mv), Moves(last))
            # sort them by the self.posSrtKey function
            ret = list(
                map(lambda m: (m, self.nxt[last.piece]),
                    sorted(mvs, key=self.posSrtKey)))
            # only return self.branch moves
            return ret[:self.branch]
        mvQ = _mvs(start)
        while len(mvQ) > 0:
            mv, piece = mvQ.pop()
            if abs(mv[0]) > self.rad or abs(mv[1]) > self.rad:
                continue
            plmt = Plmt(piece, mv)
            _, success = board.TryAdd(plmt)
            if success and plmt.piece != Piece.X:
                mvQ.extend(_mvs(plmt))
        return board


def main(bRad: str = "100", branch: str = "1", pRad: str = "0"):
    graph = Graph(rad=int(bRad), branch=int(branch))
    board = graph.Generate()
    board = BoardImage(board, splot=Splotch(rad=int(pRad)))
    board.DrawSvg()

if __name__ == "__main__":
    main(*sys.argv[1:])

