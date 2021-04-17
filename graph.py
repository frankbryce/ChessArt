#!/usr/bin/python3.9

from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
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

class DrawType(Enum):
    SVG = 1
    PATH = 2

class Tour:
    def __init__(
            self,
            nxt: dict[Piece, Piece] = {
                Piece.N: Piece.N,
            },
            branch: int = 1,
            debug: bool = False,
            drawType: DrawType = DrawType.PATH,
            rad: int = 100,
            posSrtKey: Callable[Pos, float] = DefaultPosSrtKey) -> None:
        self.branch = branch
        self.nxt = nxt
        self.posSrtKey = posSrtKey
        self.rad = rad
        self.debug = debug
        self.drawType = drawType

    def Build(self, start: Plmt = Plmt(Piece.N, (0,0))) -> Board:
        if self.drawType not in (DrawType.SVG,DrawType.PATH):
            raise Exception(f'No support for {drawType} in Tour()')
        board = Board()
        drawer = BoardImage(board)
        cnt = 0
        plmts = []
        def _add(p, add=False):
            nonlocal cnt
            nonlocal plmts
            if self.debug:
                print(p.pstn, p.piece)
            if add:
                board.Add(p)
            if self.drawType == DrawType.SVG:
                drawer.DrawSvg(
                    subOutDir='knight_tour',
                    outFileName=f'{cnt}.svg',
                )
            elif self.drawType == DrawType.PATH:
                plmts.append(p)
            cnt += 1
            
        _add(start, True)
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
                _add(plmt)
                mvQ.extend(_mvs(plmt))
        if self.drawType == DrawType.PATH:
            BoardImage.DrawPath(plmts)
        return board


def main(
    bRad: str = "100",
    branch: str = "1",
    debug: str = "False",
    pRad: str = "0"):
    tour = Tour(rad=int(bRad), branch=int(branch), debug=(debug.lower()=="true"))
    board = tour.Build()

if __name__ == "__main__":
    main(*sys.argv[1:])

