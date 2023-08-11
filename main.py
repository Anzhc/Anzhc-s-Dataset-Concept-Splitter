from PyQt5 import QtWidgets, QtCore
from collections import Counter
from PyQt5 import QtGui
import os
import re
import shutil
import json

from PyQt5 import QtWidgets, QtCore

class TagManagerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window properties
        self.setWindowTitle("DatasetManager")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Input Path Section
        input_path_layout = QtWidgets.QHBoxLayout()
        self.input_path_edit = QtWidgets.QLineEdit()
        self.input_path_button = QtWidgets.QPushButton("Select Input Folder")
        self.input_path_button.clicked.connect(self.select_input_folder)
        self.subfolder_checkbox = QtWidgets.QCheckBox("Include Subfolders")

        input_path_layout.addWidget(self.input_path_edit)
        input_path_layout.addWidget(self.input_path_button)
        input_path_layout.addWidget(self.subfolder_checkbox)

        main_layout.addLayout(input_path_layout)

        # Main Horizontal Splitter
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left Widget (Tag Lists)
        left_widget = QtWidgets.QWidget()
        tag_categories_layout = QtWidgets.QHBoxLayout()
        left_widget.setLayout(tag_categories_layout)
        
        # Tag Categories Section
        self.tag_lists = {
            'Biggest Tags': QtWidgets.QListWidget(),
            'Potent Tags': QtWidgets.QListWidget(),
            'Potential Knowledge Tags': QtWidgets.QListWidget(),
            'Impotent Tags': QtWidgets.QListWidget(),
        }

        for category, list_widget in self.tag_lists.items():
            category_layout = QtWidgets.QVBoxLayout()

            # Category label
            category_label = QtWidgets.QLabel(category)
            category_layout.addWidget(category_label)

            # List widget for tags
            list_widget.setWordWrap(True)
            category_layout.addWidget(list_widget)

            # Select/Deselect buttons
            buttons_layout = QtWidgets.QHBoxLayout()
            select_button = QtWidgets.QPushButton("Select All")
            deselect_button = QtWidgets.QPushButton("Deselect All")
            select_button.clicked.connect(lambda _, lw=list_widget: self.select_all_tags(lw))
            deselect_button.clicked.connect(lambda _, lw=list_widget: self.deselect_all_tags(lw))
            buttons_layout.addWidget(select_button)
            buttons_layout.addWidget(deselect_button)
            category_layout.addLayout(buttons_layout)

            tag_categories_layout.addLayout(category_layout)

        # Add left widget to splitter
        main_splitter.addWidget(left_widget)

        # Right Widget (JSON Part)
        right_widget = QtWidgets.QWidget()
        json_config_layout = QtWidgets.QVBoxLayout()
        right_widget.setLayout(json_config_layout)

        # Instance Prompt Input
        self.instance_prompt_input = QtWidgets.QLineEdit()
        self.instance_prompt_input.setText("[filewords]")
        self.instance_prompt_input.setPlaceholderText("Enter instance prompt...")
        json_config_layout.addWidget(self.instance_prompt_input)

        # Instance Token Input and Checkbox
        instance_token_layout = QtWidgets.QHBoxLayout()
        self.instance_token_input = QtWidgets.QLineEdit()
        self.instance_token_input.setPlaceholderText("Enter instance token...")
        self.instance_token_checkbox = QtWidgets.QCheckBox("Add folder name to instance token")
        instance_token_layout.addWidget(self.instance_token_input)
        instance_token_layout.addWidget(self.instance_token_checkbox)
        json_config_layout.addLayout(instance_token_layout)

        # Class Data Directory Input
        self.class_data_dir_input = QtWidgets.QLineEdit()
        self.class_data_dir_input.setText("E:\\SD\\2\\sdui2\\models\\dreambooth\\class folder")
        self.class_data_dir_input.setPlaceholderText("Enter directory for class dataset...")
        json_config_layout.addWidget(self.class_data_dir_input)

        # Class Token Input
        self.class_token_input = QtWidgets.QLineEdit()
        self.class_token_input.setPlaceholderText("Enter class token...")
        json_config_layout.addWidget(self.class_token_input)

        # Class Prompt Input
        self.class_prompt_input = QtWidgets.QLineEdit()
        self.class_prompt_input.setText("[filewords]")
        self.class_prompt_input.setPlaceholderText("Enter prompt for class dataset...")
        json_config_layout.addWidget(self.class_prompt_input)

        # Class Negative Prompt Input
        self.class_negative_prompt_input = QtWidgets.QLineEdit()
        self.class_negative_prompt_input.setText("(worst quality, low quality:1.4)")
        self.class_negative_prompt_input.setPlaceholderText("Enter negative prompt for class dataset...")
        json_config_layout.addWidget(self.class_negative_prompt_input)

        # Slider for class_infer_steps
        class_infer_steps_label = QtWidgets.QLabel("Steps for class generation: 12")
        self.class_infer_steps_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.class_infer_steps_slider.setRange(5, 150)
        self.class_infer_steps_slider.setValue(12)
        self.class_infer_steps_slider.valueChanged.connect(lambda value: class_infer_steps_label.setText(f"Steps for class generation: {value}"))
        json_config_layout.addWidget(class_infer_steps_label)
        json_config_layout.addWidget(self.class_infer_steps_slider)

        # Slider for class_guidance_scale
        class_guidance_scale_label = QtWidgets.QLabel("CFG for class generation: 7")
        self.class_guidance_scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.class_guidance_scale_slider.setRange(1, 15)
        self.class_guidance_scale_slider.setValue(7)
        self.class_guidance_scale_slider.valueChanged.connect(lambda value: class_guidance_scale_label.setText(f"CFG for class generation: {value}"))
        json_config_layout.addWidget(class_guidance_scale_label)
        json_config_layout.addWidget(self.class_guidance_scale_slider)

        # Slider for n_save_sample
        n_save_sample_label = QtWidgets.QLabel("Number of samples per concept folder: 0")
        self.n_save_sample_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.n_save_sample_slider.setRange(0, 10)
        self.n_save_sample_slider.valueChanged.connect(lambda value: n_save_sample_label.setText(f"Number of samples per concept folder: {value}"))
        json_config_layout.addWidget(n_save_sample_label)
        json_config_layout.addWidget(self.n_save_sample_slider)

        # Slider for num_class_images_per
        num_class_images_per_label = QtWidgets.QLabel("Number of Class Images Per instance: 0")
        self.num_class_images_per_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.num_class_images_per_slider.setRange(0, 250)
        self.num_class_images_per_slider.setValue(0)
        self.num_class_images_per_slider.valueChanged.connect(lambda value: num_class_images_per_label.setText(f"Number of Class Images Per instance: {value}"))
        json_config_layout.addWidget(num_class_images_per_label)
        json_config_layout.addWidget(self.num_class_images_per_slider)

        # Slider for save_guidance_scale
        save_guidance_scale_label = QtWidgets.QLabel("CFG for sample images: 7")
        self.save_guidance_scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.save_guidance_scale_slider.setRange(1, 15)
        self.save_guidance_scale_slider.setValue(7)
        self.save_guidance_scale_slider.valueChanged.connect(lambda value: save_guidance_scale_label.setText(f"CFG for sample images: {value}"))
        json_config_layout.addWidget(save_guidance_scale_label)
        json_config_layout.addWidget(self.save_guidance_scale_slider)

        # Slider for save_infer_steps
        save_infer_steps_label = QtWidgets.QLabel("Steps for sample images: 12")
        self.save_infer_steps_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.save_infer_steps_slider.setRange(5, 150)
        self.save_infer_steps_slider.setValue(12)
        self.save_infer_steps_slider.valueChanged.connect(lambda value: save_infer_steps_label.setText(f"Steps for sample images: {value}"))
        json_config_layout.addWidget(save_infer_steps_label)
        json_config_layout.addWidget(self.save_infer_steps_slider)

        # Save Sample Prompt Input
        self.save_sample_prompt_input = QtWidgets.QLineEdit()
        self.save_sample_prompt_input.setText("[filewords]")
        self.save_sample_prompt_input.setPlaceholderText("Enter save sample prompt...")
        json_config_layout.addWidget(self.save_sample_prompt_input)

        # Save Sample Negative Prompt Input
        self.save_sample_negative_prompt_input = QtWidgets.QLineEdit()
        self.save_sample_negative_prompt_input.setText("(worst quality, low quality:1.4)")
        self.save_sample_negative_prompt_input.setPlaceholderText("Enter save sample negative prompt...")
        json_config_layout.addWidget(self.save_sample_negative_prompt_input)

        # Create JSON Checkbox
        self.create_json_checkbox = QtWidgets.QCheckBox("Create JSON File for D8 Dreambooth")
        json_config_layout.addWidget(self.create_json_checkbox)

        # Add the right widget to the main splitter
        main_splitter.addWidget(right_widget)

        # Destination Path Section
        destination_path_layout = QtWidgets.QHBoxLayout()
        self.destination_path_edit = QtWidgets.QLineEdit()
        self.destination_path_button = QtWidgets.QPushButton("Select Destination Folder")
        self.destination_path_button.clicked.connect(self.select_destination_folder)

        destination_path_layout.addWidget(self.destination_path_edit)
        destination_path_layout.addWidget(self.destination_path_button)

        main_layout.addLayout(destination_path_layout)

        # Start Button
        self.start_button = QtWidgets.QPushButton("Start Operation")
        self.start_button.clicked.connect(self.start_operation)

        main_layout.addWidget(self.start_button)

        # Setting main layout
        central_widget.setLayout(main_layout)

        self.show()


    def select_input_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder_path:
            self.input_path_edit.setText(folder_path)  # Assuming you have a QLineEdit for the input folder path
            # Set the default destination path to be a "sorted dataset" subfolder within the input folder
            destination_path = os.path.join(folder_path, "sorted dataset")
            self.destination_path_edit.setText(destination_path)  # Assuming you have a QLineEdit for the destination folder path
            self.load_and_populate_tags(folder_path, include_subfolders=self.subfolder_checkbox.isChecked())


    def load_and_populate_tags(self, folder_path, include_subfolders=False):
        tag_counts = Counter()
        total_images = 0

        # Load and Process Tags
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                if file_name.lower().endswith('.txt'):
                    total_images += 1  # Counting the number of images
                    tag_file_path = os.path.join(root, file_name)
                    with open(tag_file_path, 'r') as tag_file:
                        tag_string = tag_file.read().strip()
                        tags = re.split(r'\s*,\s*', tag_string)  # Split by commas, with or without spaces
                        tag_counts.update(tags)
            if not include_subfolders:
                break

        # Sort tags by count in descending order
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        # Threshold for tags that appear in more than 50% of images
        threshold = total_images * 0.5

        biggest_tags = [(tag, count) for tag, count in sorted_tags if count > threshold]
        potential_knowledge_tags = [item for item in sorted_tags if 15 <= item[1] <= 65]
        potent_tags = [item for item in sorted_tags if item[1] > 65]
        impotent_tags = [item for item in sorted_tags if item[1] < 15]


        # Populate Lists with Checkboxes
        for category, tags in [('Biggest Tags', biggest_tags), ('Potential Knowledge Tags', potential_knowledge_tags),
                            ('Potent Tags', potent_tags), ('Impotent Tags', impotent_tags)]:
            list_widget = self.tag_lists[category]
            list_widget.clear()
            for tag, count in tags:
                item = QtWidgets.QListWidgetItem(f"{tag} ({count})")
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                list_widget.addItem(item)

    def select_all_tags(self, list_widget):
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            item.setCheckState(QtCore.Qt.Checked)

    def deselect_all_tags(self, list_widget):
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            item.setCheckState(QtCore.Qt.Unchecked)

    def select_destination_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder_path:
            self.destination_path_edit.setText(folder_path)

    def get_selected_tags(self):
        selected_tags = []
        for category, list_widget in self.tag_lists.items():
            for index in range(list_widget.count()):
                item = list_widget.item(index)
                if item.checkState() == QtCore.Qt.Checked:
                    # Extract the tag and count from the text
                    text = item.text().strip()
                    tag, count_text = text.rsplit(' ', 1)
                    count = int(count_text.strip("()"))
                    selected_tags.append((tag, count))

        # Sort by count in ascending order
        selected_tags.sort(key=lambda x: x[1])
        return selected_tags

    def create_folders(self, tags, destination_path):
        for tag, _ in tags:
            folder_path = os.path.join(destination_path, tag)
            os.makedirs(folder_path, exist_ok=True)

    def copy_images_and_tags(self, tags, source_path, destination_path, include_subfolders=False):
        copied_images = set()
        tag_mapping = {tag: count for tag, count in tags}
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']

        # Print the tags for debugging
        print("Selected tags:", tags)

        strip_tag = self.instance_token_checkbox.isChecked()

        for root, _, files in os.walk(source_path):
            for file_name in files:
                if file_name.lower().endswith('.txt'):
                    tag_file_path = os.path.join(root, file_name)
                    image_name_base = file_name[:-4]
                    image_path = None

                    for ext in image_extensions:
                        potential_image_path = os.path.join(root, image_name_base + ext)
                        if os.path.exists(potential_image_path):
                            image_path = potential_image_path
                            break

                    if image_path and image_path not in copied_images:
                        with open(tag_file_path, 'r') as tag_file:
                            tag_content = tag_file.read()
                            file_tags = [tag.strip() for tag in tag_content.split(',')]

                            # Print the file tags for debugging
                            print("File tags:", file_tags)

                            matching_tag = min((tag for tag in file_tags if tag in tag_mapping), key=lambda t: tag_mapping.get(t, float('inf')), default=None)

                            # Print the matching tag for debugging
                            print("Matching tag:", matching_tag)

                            if matching_tag:
                                destination_folder = os.path.join(destination_path, matching_tag)

                                # Print the destination folder for debugging
                                print("Destination folder:", destination_folder)

                                if strip_tag:
                                    file_tags.remove(matching_tag)
                                    new_tag_content = ','.join(file_tags)
                                    with open(os.path.join(destination_folder, file_name), 'w') as new_tag_file:
                                        new_tag_file.write(new_tag_content)
                                else:
                                    shutil.copy(tag_file_path, destination_folder)

                                shutil.copy(image_path, destination_folder)
                                copied_images.add(image_path)

            if not include_subfolders:
                break

        return copied_images



    def create_unified_folder(self, copied_images, source_path, destination_path, include_subfolders=False):
        unified_folder = os.path.join(destination_path, 'assorted')
        os.makedirs(unified_folder, exist_ok=True)
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']

        for root, _, files in os.walk(source_path):
            for file_name in files:
                file_extension = os.path.splitext(file_name)[-1].lower()
                if file_extension in image_extensions:
                    image_path = os.path.join(root, file_name)
                    if image_path not in copied_images:
                        tag_file_path = os.path.join(root, file_name[:-len(file_extension)] + '.txt')
                        shutil.copy(image_path, unified_folder)  # Copy image file
                        if os.path.exists(tag_file_path):  # Check if tag file exists
                            shutil.copy(tag_file_path, unified_folder)  # Copy tag file
            if not include_subfolders:
                break

    def start_operation(self):
        # Get the source and destination paths
        source_path = self.input_path_edit.text()
        destination_path = self.destination_path_edit.text()

        # Check if paths are valid
        if not source_path or not destination_path:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select both input and destination folders.")
            return

        # Get the selected tags
        selected_tags = self.get_selected_tags()

        # Create folders for the selected tags
        self.create_folders(selected_tags, destination_path)

        # Copy images and tags to the new folders
        copied_images = self.copy_images_and_tags(selected_tags, source_path, destination_path, include_subfolders=self.subfolder_checkbox.isChecked())

        # Create a unified folder for the rest
        self.create_unified_folder(copied_images, source_path, destination_path, include_subfolders=self.subfolder_checkbox.isChecked())

        # Check if the JSON checkbox is checked
        if self.create_json_checkbox.isChecked():
            self.generate_json(destination_path, selected_tags)  # Assuming you have defined the method to generate the JSON

        # Open the root folder of the new dataset
        os.startfile(destination_path)


    def generate_json(self, destination_path, selected_tags):
        # Step 1: Collect Input Values
        class_data_dir = self.class_data_dir_input.text()
        class_guidance_scale = self.class_guidance_scale_slider.value()
        class_infer_steps = self.class_infer_steps_slider.value()
        class_negative_prompt = self.class_negative_prompt_input.text()
        class_prompt = self.class_prompt_input.text()
        class_token = self.class_token_input.text()
        instance_prompt = self.instance_prompt_input.text()
        instance_token = self.instance_token_input.text()
        n_save_sample = self.n_save_sample_slider.value()
        num_class_images_per = self.num_class_images_per_slider.value()
        save_guidance_scale = self.save_guidance_scale_slider.value()
        save_infer_steps = self.save_infer_steps_slider.value()
        save_sample_negative_prompt = self.save_sample_negative_prompt_input.text()
        save_sample_prompt = self.save_sample_prompt_input.text()

        # Assuming tag_folders are obtained from the selected tags in your application
        tag_folders = self.get_selected_tags()

        # Step 2: Construct JSON Object
        json_data = []
        for tag_tuple in selected_tags:
            tag_folder = tag_tuple[0]  # Extracting the tag name from the tuple
            # Create the instance_data_dir for this specific tag folder
            instance_data_dir = os.path.normpath(os.path.join(destination_path, tag_folder))
            entry = {
                "class_data_dir": os.path.join(class_data_dir, tag_folder),
                "class_guidance_scale": class_guidance_scale,
                "class_infer_steps": class_infer_steps,
                "class_negative_prompt": class_negative_prompt,
                "class_prompt": class_prompt,
                "class_token": class_token,
                "instance_data_dir": instance_data_dir,
                "instance_prompt": instance_prompt,
                "instance_token": f"{instance_token}, {tag_folder}" if self.instance_token_checkbox.isChecked() else instance_token,
                "is_valid": True,
                "n_save_sample": n_save_sample,
                "num_class_images_per": num_class_images_per,
                "sample_seed": 420420,
                "save_guidance_scale": save_guidance_scale,
                "save_infer_steps": save_infer_steps,
                "save_sample_negative_prompt": save_sample_negative_prompt,
                "save_sample_prompt": save_sample_prompt,
                "save_sample_template": ""
            }
            json_data.append(entry)
            # Add entry for assorted folder
        assorted_entry = {
            "class_data_dir": os.path.join(class_data_dir, "assorted"),
            "class_guidance_scale": class_guidance_scale,
            "class_infer_steps": class_infer_steps,
            "class_negative_prompt": class_negative_prompt,
            "class_prompt": class_prompt,
            "class_token": class_token,
            "instance_data_dir": os.path.normpath(os.path.join(destination_path, "assorted")),
            "instance_prompt": instance_prompt,
            "instance_token": instance_token,  # Adjust this as needed for the assorted folder
            "is_valid": True,
            "n_save_sample": n_save_sample,
            "num_class_images_per": num_class_images_per,
            "sample_seed": 420420,
            "save_guidance_scale": save_guidance_scale,
            "save_infer_steps": save_infer_steps,
            "save_sample_negative_prompt": save_sample_negative_prompt,
            "save_sample_prompt": save_sample_prompt,
            "save_sample_template": ""
        }
        json_data.append(assorted_entry)

        # Write the JSON data to a file
        with open(os.path.normpath(os.path.join(destination_path, 'config.json')), 'w') as json_file:
            json.dump(json_data, json_file, indent=0)

if __name__ == "__main__":
    def load_stylesheet(file_path):
        with open(file_path, "r") as file:
           return file.read()

    app = QtWidgets.QApplication([])

    # Load the stylesheet from the CSS file
    css_file_path = 'style.css'
    stylesheet = load_stylesheet(css_file_path)

    # Apply the loaded stylesheet to the application
    app.setStyleSheet(stylesheet)

    # Continue with the rest of your application code
    window = TagManagerApp()
    window.show()
    app.exec_()