#!/usr/bin/env python3

import argparse
import numpy as np
from scipy import signal as sig
import wave

parser = argparse.ArgumentParser()
parser.add_argument("ofile", type=str, help="Output filepath")


class WaveData:
    rate: int = 44100
    sec: float = 1.0
    amp: float = 0.5
    BPM: int = 0
    mml: str = ""
    note_dur: float = 0.0
    shape: str = ""
    duty: float = 0.0
    width: float = 0.0
    base_freq: float = 440.0
    notes: dict[list[str], list[float]] = {}
    t_dur: float = 0.0
    output = np.array([])
    output16bit = np.array([])

    def __init__(
        self,
        mml: str,
        bpm: int = 120,
        duty: float = 0.5,
        width: float = 0.5,
        shape: str = "sin",
    ) -> None:
        self.set_freqs()
        self.BPM = bpm
        self.note_dur = 60.0 / float(bpm)
        self.duty = duty
        self.width = width
        self.shape = shape
        self.set_note_time()
        self.mml = mml

    def set_freqs(self):
        i_notes: list[str] = [
            "R",
            "C",
            "C#",
            "D",
            "D#",
            "E",
            "F",
            "F#",
            "G",
            "G#",
            "A",
            "A#",
            "B",
        ]
        for i, index in enumerate(i_notes):
            if i == 0:
                self.notes[0] = [0]
                continue
            self.notes[index] = 440.0 * 2.0 ** ((i - 10) / 12.0)

    def set_note_time(self):
        self.t_dur = np.linspace(0.0, self.note_dur, int(self.rate * self.note_dur))

    def get_note_list(self):
        if self.shape == "sin":
            self.mml_to_sin()
        elif self.shape == "sq":
            self.mml_to_square()
        self.convert_16bit()

    def mml_to_sin(self):
        for char in list(self.mml):
            self.output = np.append(
                self.output, np.sin(2.0 * np.pi * self.notes[char] * self.t_dur)
            )

    def mml_to_square(self):
        for char in list(self.mml):
            self.output = np.append(
                self.output,
                sig.square(2.0 * np.pi * self.notes[char] * self.t_dur, self.duty),
            )

    def convert_16bit(self):
        self.output16bit = self.output * np.iinfo(np.int16).max
        self.output16bit = self.output16bit.astype(np.int16)


def genarate(filename: str):
    print(filename)
    mml = "DCDC"
    wdata = WaveData(mml, bpm=120, duty=0.5, shape="sq")
    wdata.get_note_list()
    with wave.open(filename, mode="w") as ofile:
        ofile.setnchannels(1)
        ofile.setsampwidth(2)
        ofile.setframerate(wdata.rate)
        ofile.writeframes(wdata.output16bit)


if __name__ == "__main__":
    args = parser.parse_args()
    genarate(args.ofile)
