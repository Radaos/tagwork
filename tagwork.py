#!/usr/bin/env python3
"""
Tags the name field in Zwift workouts with an ID in the form [n], where n is numeric.
This ID indicates the group they belong to, it can be used to filter for a workout group in Golden Cheetah.
Usage: On run, the user will be prompted to choose a directory containing workout files to process.
A new output directory with the suffix _tagged will be created in the same parent directory as the input.

Author: Robert Drohan
Copyright: Copyright 2025, Robert Drohan
License: GPLv3
Version: 1.02
Status: Release
"""

import sys
import os
import errno
import tkinter as tk
from tkinter.filedialog import askdirectory
import xml.etree.ElementTree as ET


def open_dir_dialog(user_msg):
    """Ask the user to specify a directory."""
    default_dir = 'C:\\'
    selected_dir = askdirectory(title=user_msg, initialdir=default_dir)
    return selected_dir or None


def make_path(path):
    """Create a directory path if it doesn't already exist."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def update_workout_xml(xml_content, group_id, file_dir):
    """Update the <name> and <description> elements in the XML."""
    try:
        xml_root = ET.fromstring(xml_content)
    except ET.ParseError as error:
        raise ValueError(f"XML parse error: {error}")

    # Update <name>
    name_element = xml_root.find("name")
    if name_element is None:
        name_element = ET.SubElement(xml_root, "name")
    name_element.text = (name_element.text or "") + f" [{group_id}]"

    # Update <description>
    desc_element = xml_root.find("description")
    if desc_element is None:
        desc_element = ET.SubElement(xml_root, "description")
    desc_element.text = (desc_element.text or "")
    desc_element.text = f"{file_dir}:  {desc_element.text}"

    return ET.tostring(xml_root, encoding="unicode")


def main():
    processed_file_count = 0

    # Initialize Tkinter and hide the root window
    tk_root_window = tk.Tk()
    tk_root_window.withdraw()

    # Ask the user for the source directory containing workout files
    input_workout_root_dir = open_dir_dialog("Select workout directory")
    tk_root_window.destroy()
    if not input_workout_root_dir:
        print("No directory selected. Exiting.", file=sys.stderr)
        sys.exit(1)

    input_root_parent_dir, input_root_dir_name = os.path.split(input_workout_root_dir)
    output_tagged_root_dir = os.path.join(input_root_parent_dir, f"{input_root_dir_name}_tagged")
    make_path(output_tagged_root_dir)

    # Maps input dir path to its hierarchical id (e.g., "2.1.3")
    directory_id_map = {input_workout_root_dir: ""}
    # Maps input dir path to the next child number
    child_directory_counter_map = {}

    for current_directory, subdirectories, filenames in os.walk(input_workout_root_dir, topdown=True):
        # Get parent id
        parent_directory = os.path.dirname(current_directory)
        parent_group_id = directory_id_map.get(parent_directory, "")

        # Assign id to current directory if not top-level
        if current_directory == input_workout_root_dir:
            current_group_id = ""
        else:
            # Get next child number for parent
            next_child_number = child_directory_counter_map.get(parent_directory, 1)
            current_group_id = f"{parent_group_id}-{next_child_number}" if parent_group_id else f"{next_child_number}"
            directory_id_map[current_directory] = current_group_id
            child_directory_counter_map[parent_directory] = next_child_number + 1

        # Prepare id assignment for subdirectories
        child_directory_counter_map[current_directory] = 1

        for filename in filenames:
            input_file_path = os.path.join(current_directory, filename)
            file_stem, file_extension = os.path.splitext(filename)
            if file_extension.lower() in ['.zwo', '.xml']:
                try:
                    with open(input_file_path, "r", encoding="utf-8", errors="replace") as xml_file:
                        xml_content = xml_file.read()
                    group_id = directory_id_map.get(current_directory, "")
                    normalized_current_dir = os.path.normpath(current_directory)
                    base_dir_name = os.path.basename(normalized_current_dir)
                    parent_dir_path = os.path.normpath(os.path.dirname(normalized_current_dir))
                    parent_base_dir_name = os.path.basename(parent_dir_path)
                    updated_xml = update_workout_xml(
                        xml_content,
                        group_id,
                        'File:' + parent_base_dir_name + '/' + base_dir_name + '/' + file_stem
                    )
                except (IOError, ValueError) as error:
                    print(f"Error processing file {input_file_path}: {error}", file=sys.stderr)
                    continue

            # Prepare output path
            relative_input_path = os.path.relpath(input_file_path, input_workout_root_dir)
            relative_input_dir = os.path.dirname(relative_input_path)
            if relative_input_dir == "":
                # File is in the top-level input directory
                output_directory = output_tagged_root_dir
            else:
                # Build the output path, tagging every directory in the path
                directory_parts = relative_input_dir.split(os.sep)
                tagged_directory_parts = []
                path_accumulator = input_workout_root_dir
                for directory_part in directory_parts:
                    path_accumulator = os.path.join(path_accumulator, directory_part)
                    group_tag = directory_id_map.get(path_accumulator, "")
                    tagged_directory_parts.append(f"{directory_part}_[{group_tag}]")
                output_directory = os.path.join(output_tagged_root_dir, *tagged_directory_parts)
            make_path(output_directory)
            output_file_path = os.path.join(output_directory, filename)

            try:
                with open(output_file_path, "w", encoding="utf-8") as xml_file:
                    xml_file.write(updated_xml)
                processed_file_count += 1
            except IOError as error:
                print(f"Error writing to file {output_file_path}: {error}", file=sys.stderr)

    print(f"Processed {len(directory_id_map)-1} groups, {processed_file_count} files.")


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Aborting. Python 3 must be installed!")
    main()
