# Custom Smashcima – Synthesizing Scores from Custom Symbols

[![License Apache 2.0](https://badgen.net/badge/license/apache2.0/blue)](https://github.com/OMR-Research/Smashcima/blob/main/LICENSE)
![Python Version](https://badgen.net/badge/python/3.8+/cyan)

<div align="center">
    <br/>
    <img src="docs/assets/smashcima-logo.svg" width="600px">
    <br/>
    <br/>
</div>

A fork of [Smashcima](https://github.com/OMR-Research/Smashcima), this project enables **synthetic generation of handwritten-style music scores** using **custom symbol images from a local folder** rather than from MUSCIMA++ writers.

---

## 🔍 Key Features

- ✅ Render synthetic handwritten musical scores using your own collection of musical symbols.
- ✅ Choose between the **Base** and **Tweaked** generation models.
- ✅ Automatically renders and saves each score page as a `.png` image.
- ✅ Processes batches of MusicXML files from a folder.

---

## 📦 Installation

Clone this repository and install dependencies inside a virtual environment:

```bash
git clone https://github.com/GerardAsbert/Smashcima.git
cd Smashcima

pip install -r requirements.txt

```
---

## 🚀 Usage

You can run the `generate_partitures.py` script to synthesize handwritten scores using either the base or tweaked rendering model.

```bash
python generate_partitures.py base /path/to/musicxml_folder /path/to/output_folder
```

### Arguments:

- `model_type`: `base` or `tweaked` – which model to use for rendering.
- `input_path`: Directory containing `.musicxml` files.
- `output_path`: Directory where the output `.png` images will be saved.

Each `.musicxml` file in the input folder will be rendered and saved as a `.png` file in the output folder.

---

## 🧠 How This Differs From Original Smashcima

- ✂️ **MUSCIMA++ dependency removed:** You can now render using your own glyph images.
- 📂 **Batch processing of MusicXML files:** Feed in a folder of MusicXML files.
- ⚙️ **Minimal CLI interface:** Easily select rendering model and input/output folders.

---
  
## 📚 References & Acknowledgements

This work is based on [Smashcima](https://github.com/OMR-Research/Smashcima), originally developed by:

> Jiří Mayer and Pavel Pecina. *Synthesizing Training Data for Handwritten Music Recognition*. 16th International Conference on Document Analysis and Recognition, ICDAR 2021.

---

## 📝 License

This project remains licensed under the [Apache License 2.0](https://github.com/OMR-Research/Smashcima/blob/main/LICENSE), following the terms of the original Smashcima repository.

---

## 👥 Contact

For contributions, questions, or bug reports, feel free to open an issue or reach out to the upstream maintainers via [Smashcima's GitHub](https://github.com/OMR-Research/Smashcima).

