#!/usr/bin/python3.9

from __future__ import annotations

from collections.abc import Iterable
from configargparse import ArgParser
from enum import Enum
from board import *
from image import *
import json
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
            nxt: dict[str, str] = {
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
                map(lambda m: (m, Piece[self.nxt[last.piece.name]]),
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

def main(graphRadius, branch, debug, drawType, pixelRadius, nextPieceDict):
    tour = Tour(
        rad=int(graphRadius),
        branch=int(branch),
        drawType=DrawType[drawType],
        debug=(debug.lower()=="true"),
        nxt=json.loads(nextPieceDict))
    board = tour.Build()

if __name__ == "__main__":
    p = ArgParser(default_config_files=["graph.conf"])
    p.add("--branch",
          help="for tour graphs, the branching factor for each hop.")
    p.add("--debug", help="prints debugging info")
    p.add("--graphRadius", help="max abs(x) or abs(y) coord for graph.")
    p.add("--drawType", help="which DrawType to use for rendoring board")
    p.add("--pixelRadius", help="for .bmp renders, radius for each piece's color")
    p.add("--nextPieceDict", help="defines piece ordering for a Tour")
    main(**vars(p.parse_args()))

