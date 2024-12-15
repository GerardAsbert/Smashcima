from re import M
import cv2
import smashcima as sc
import importlib.util
import sys
import os

'''file_path = "/home/gasbert/Desktop/Mashcima2/Smashcima/smashcima/orchestration/TweakedHandwrittenModel.py"
module_name = "TweakedHandwrittenModel"

# Load the module
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)'''

from smashcima.orchestration import TweakedHandwrittenModel
from smashcima.orchestration import BaseHandwrittenModel

model = BaseHandwrittenModel()

'''for file in os.listdir("/data/gasbert/datasets/datasets/generation_data/Mashcima/Writer01"):
    filename_mxml = file[:-3] + "musicxml"
    if filename_mxml == "FMT_C47_0001b.01.musicxml":
        scene = model("/data/gasbert/datasets/datasets/generation_data/TranscriptionsSMashcima/" + filename_mxml)
        for i, page in enumerate(scene.pages):
            bitmap = scene.render(page)
            #cv2.imwrite(f"page_{i}_quarterrests.png", bitmap)
            cv2.imwrite("dolores_partitures_wholepages/" + file, bitmap)'''




scene = model("/data2fast/users/gasbert/datasets/generation_data/Transcriptions/UAB_LICEU_222570.059.08.musicxml")

for i, page in enumerate(scene.pages):
    bitmap = scene.render(page)
    #cv2.imwrite(f"page_{i}_quarterrests.png", bitmap)
    cv2.imwrite(f"prova_uab_liceu.png", bitmap)