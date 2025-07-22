import argparse
import cv2
import os
from smashcima.orchestration import TweakedHandwrittenModel, BaseHandwrittenModel

def main(model_type: str, input_path: str, output_path: str):
    if model_type == "base":
        model = BaseHandwrittenModel()
    elif model_type == "tweaked":
        model = TweakedHandwrittenModel()
    else:
        raise ValueError("Model type must be either 'base' or 'tweaked'.")

    for file in os.listdir(input_path):
        scene = model(os.path.join(input_path, file))
        for i, page in enumerate(scene.pages):
            bitmap = scene.render(page)
            cv2.imwrite(os.path.join(output_path, file[:-8] + "png"), bitmap)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render MusicXML using Base or Tweaked Smashcima model.")
    parser.add_argument("model_type", choices=["base", "tweaked"], help="Which model to use: 'base' or 'tweaked'")
    parser.add_argument("input_path", type=str, help="Path to the MusicXML file")
    parser.add_argument("output_path", type=str, help="Directory to save rendered PNG files")

    args = parser.parse_args()

    os.makedirs(args.output_path, exist_ok=True)
    main(args.model_type, args.input_path, args.output_path)
