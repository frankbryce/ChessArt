#!/usr/bin/python3.9

from __future__ import annotations

from board import *
import numpy as np
from PIL import Image
import os

Color = tuple[int, int, int]
ColorMap = dict[Piece, Color]
DefaultColorMap = {
    Piece.P: (128, 128, 0),
    Piece.N: (128, 0, 128),
    Piece.B: (0, 128, 128),
    Piece.R: (128, 0, 0),
    Piece.Q: (0, 128, 0),
    Piece.K: (0, 0, 128),
}

class BoardImage:
    def __init__(self,
            board: Board,
            border: int = 0,
            colorMap: ColorMap = DefaultColorMap,
            outDir: str = 'images') -> None:
        self.board = board
        self.colorMap = colorMap
        self.outDir = outDir
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
        self.subs = []

    def Add(self, board: Board) -> BoardImage:
        self.adds.append(img)
        return self

    def Sub(self, board: Board) -> BoardImage:
        self.subs.append(img)
        return self

    def Draw(self, loc: str, rescale: int = 1) -> None:
        img = Image.new('RGB', (self.box[1][0] - self.box[0][0] + 1,
                                self.box[1][1] - self.box[0][1] + 1))
        pixels = img.load() # Create the pixel map
        for plmt in self.board.Placements():
            x = plmt.pstn[0] - self.box[0][0]
            y = plmt.pstn[1] - self.box[0][1]
            pixels[x,y] = self.colorMap[plmt.piece]
        for add in self.adds:
            for plmt in add.Placements():
                x = plmt.pstn[0] - self.box[0][0]
                y = plmt.pstn[1] - self.box[0][1]
                pixels[x,y] += self.colorMap[plmt.piece]
        for sub in self.subs:
            for plmt in sub.Placements():
                x = plmt.pstn[0] - self.box[0][0]
                y = plmt.pstn[1] - self.box[0][1]
                pixels[x,y] -= self.colorMap[plmt.piece]
        img.resize((img.size[0]*rescale, img.size[1]*rescale))
        os.makedirs(os.path.dirname(loc), exist_ok=True)
        img.save(loc)


def main(imageLoc:str ='images/tmp.bmp', rescale: int=500):
    board = Board()

    # pawns
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
