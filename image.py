#!/usr/bin/python3.9

from __future__ import annotations

from board import *
from enum import Enum
import numpy as np
from PIL import Image
import os

Color = tuple[int, int, int]
ColorMap = dict[Piece, Color]
DefaultColorMap = {
    Piece.X: (0, 0, 0),
    Piece.P: (128, 128, 0),
    Piece.N: (128, 0, 128),
    Piece.B: (0, 128, 128),
    Piece.R: (128, 0, 0),
    Piece.Q: (0, 128, 0),
    Piece.K: (0, 0, 128),
}

class SplotchType(Enum):
    SQUARE = 1

class Splotch:
    def __init__(self, typ: SplotchType = SplotchType.SQUARE, rad: int = 0) -> None:
        self.typ = typ
        self.rad = rad

class BoardImage:
    def __init__(self,
            board: Board,
            border: int = 0,
            colorMap: ColorMap = DefaultColorMap,
            splot: Splotch = Splotch(),
            outDir: str = 'images') -> None:
        self.board = board
        self.colorMap = colorMap
        self.outDir = outDir
        self.splot = splot
        assert border >= 0
        self.box = (
            (
                min(board.Box()[0][0], board.Box()[1][0])
                - border,
                min(board.Box()[0][1], board.Box()[1][1])
                - border
            ),
            (
                max(board.Box()[0][0], board.Box()[1][0])
                + border,
                max(board.Box()[0][1], board.Box()[1][1])
                + border
            ),
        )

        # Lazy Load bmp generation when you add images together
        self.adds = []

    def Add(self, board: Board) -> BoardImage:
        self.adds.append(img)
        return self

    def _drawPiece(self, pixels, plmt: Plmt) -> pixels:
        xc = plmt.pstn[0] - self.box[0][0]
        yc = plmt.pstn[1] - self.box[0][1]
        if self.splot.typ == SplotchType.SQUARE:
            for rx in range(self.splot.rad*2+1):
                for ry in range(self.splot.rad*2+1):
                    x = min(max(xc - self.splot.rad + rx, 0), self.box[1][0]
                        - self.box[0][0])
                    y = min(max(yc - self.splot.rad + ry, 0), self.box[1][1]
                        - self.box[0][1])
                    pixels[x,y] = (
                        (pixels[x,y][0] + self.colorMap[plmt.piece][0]) % 256,
                        (pixels[x,y][1] + self.colorMap[plmt.piece][1]) % 256,
                        (pixels[x,y][2] + self.colorMap[plmt.piece][2]) % 256
                    )
        else:
            raise Exception(f"Unsupported splotch type {self.splot.typ}")
        return pixels
                

    def Draw(self, loc: str = "images/tmp.bmp", rescale: int = 1) -> None:
        img = Image.new('RGB', (self.box[1][0] - self.box[0][0] + 1,
                                self.box[1][1] - self.box[0][1] + 1))
        pixels = img.load() # Create the pixel map
        for plmt in self.board.Placements():
            self._drawPiece(pixels, plmt)
        for add in self.adds:
            for plmt in add.Placements():
                self._drawPiece(pixels, plmt)
        img.resize((img.size[0]*rescale, img.size[1]*rescale))
        os.makedirs(os.path.dirname(loc), exist_ok=True)
        img.save(loc)


def main(imageLoc:str ='images/tmp.bmp', rescale: int=500) -> None:
    board = Board()

    for x in range(25000):
        piece = Piece(np.random.randint(6)+1)
        board.Add(
            Plmt(piece,
                (np.random.randint(500), np.random.randint(500))),
            check = False)

    img = BoardImage(board)
    img.Draw(imageLoc)


if __name__ == "__main__":
    main(*sys.argv[1:])
