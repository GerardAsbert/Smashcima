import xml.etree.ElementTree as ET
import os

# Load the MusicXML file
path = "/data/gasbert/datasets/datasets/generation_data"
input_folder = "/Transcriptions/"
output_folder= "/TranscriptionsSMashcima/"
if not os.path.exists(path + output_folder):
    os.mkdir(path + output_folder)
for file in os.listdir(path + input_folder):
    file_path = path + input_folder + file 
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Iterate through all <supports> elements with attribute "new-system"
    for parent in root.findall(".//supports/.."):  # Find the parent elements of <supports>
        for supports in parent.findall("supports"):
            if supports.get("attribute") == "new-system" and supports.get("value") == "yes":
                parent.remove(supports)
                #supports.set("value", "no")
    for measure in root.findall(".//measure"):
        # Find <print> elements within each <measure>
        for print_elem in measure.findall("print"):
            if print_elem.get("new-system") == "yes":
                # Remove the <print> element
                measure.remove(print_elem)

    # Save the modified MusicXML file
    output_file_path = path + output_folder + file # Replace with your output path
    tree.write(output_file_path, encoding="utf-8", xml_declaration=True)

    print(f"Modified MusicXML saved to {output_file_path}")