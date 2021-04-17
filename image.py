#!/usr/bin/python3.9

from __future__ import annotations

from board import *
from datetime import datetime
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
import svg_stack as ss

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
                

    def DrawBmp(self, loc: str = "images/tmp.bmp", rescale: int = 1) -> None:
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

    def DrawSvg(
            self,
            topOutDir: str = "images",
            subOutDir: str = datetime.now().strftime('%Y%m%d_%H%M%S'),
            outFileName: str = "tmp.svg",
            svgInDir: str = "svg",
            svgSz: int = 45) -> None:
        # build a dict of {row: [Plmt]}
        rowDict = {}
        for plmt in self.board.Placements():
            row = plmt.pstn[1]
            if row not in rowDict:
                rowDict[row] = []
            rowDict[row].append(plmt)

        rows = sorted(rowDict.keys())
        minRow = rows[0]
        maxRow = rows[-1]
        hlayouts = []
        for row in rows:
            if row in rowDict:
                # for each row, sort [Piece] by col
                r = sorted(rowDict[row], key=lambda p: p.pstn[0])
                minCol = r[0].pstn[0]
                maxCol = r[-1].pstn[0]
                # if first col isn't = bounding box minx, prepend empty piece
                if minCol > self.board.Box()[0][0]:
                    r = [Plmt(Piece.X, (self.board.Box()[0][0], row))] + r
                # if last col isn't = bounding box maxx, append empty piece
                if maxCol < self.board.Box()[1][0]:
                    r = [Plmt(Piece.X, (self.board.Box()[1][0], row))] + r
            else:
                # if no pieces in row, make a layout bookmarked by blanks
                r = [
                    Plmt(Piece.X, (self.board.Box()[0][0], row)),
                    Plmt(Piece.X, (self.board.Box()[1][0], row)),
                ]

            # put first item into hlayout. save last piece
            lastLyt = ss.HBoxLayout()
            color = "white"
            if plmt.pstn[0] == plmt.pstn[1] == 0:
                color = "black"
            lastLyt.addSVG(f"{svgInDir}/{color}/{r[0].piece.name}.svg",
                    alignment=ss.AlignLeft)
            lastPlmt = r[0]
            for plmt in r[1:]:
                # for each piece, create new hlayout, add last layout w/ proper spacing
                lyt = ss.HBoxLayout()
                lyt.setSpacing(svgSz * (plmt.pstn[0]-lastPlmt.pstn[0]-1))
                lyt.addLayout(lastLyt)
                color = "white"
                if plmt.pstn[0] == plmt.pstn[1] == 0:
                    color = "black"
                lyt.addSVG(f"{svgInDir}/{color}/{plmt.piece.name}.svg",
                        alignment=ss.AlignLeft)
                lastLyt, lastPlmt = lyt, plmt
            hlayouts.append(lastLyt)

        # for each hlayout, append into vlayout
        vlayout = ss.VBoxLayout()
        for hlayout in hlayouts:
            vlayout.addLayout(hlayout)

        # make doc and save to outdir
        doc = ss.Document()
        doc.setLayout(vlayout)
        loc = f"{topOutDir}/{subOutDir}/{outFileName}"
        os.makedirs(os.path.dirname(loc), exist_ok=True)
        doc.save(loc)

    @staticmethod
    def DrawPath(plmts: [Plmt]) -> None:
        fig = plt.figure(frameon=False)
        ax = plt.Axes(fig, [0.,0.,1.,1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        for i, plmt in enumerate(plmts):
            if i == len(plmts)-1:
                break
            plt.plot(
                [plmts[i].pstn[0], plmts[i+1].pstn[0]],
                [plmts[i].pstn[1], plmts[i+1].pstn[1]], 'ro-')
        fig.savefig(
            "images/tmp.png",
            bbox_inches='tight',
            pad_inches=0)

def main(imageLoc:str ='images/tmp.bmp', rescale: int=500) -> None:
    board = Board()

    for x in range(100):
        piece = Piece(np.random.randint(6)+1)
        board.Add(
            Plmt(piece,
                (np.random.randint(20), np.random.randint(20))),
            check = False)

    img = BoardImage(board)
    img.DrawBmp(imageLoc)
    img.DrawSvg()


if __name__ == "__main__":
    main(*sys.argv[1:])
