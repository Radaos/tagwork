#!/usr/bin/env python3
"""
Tags the name field in Zwift workouts with an ID in the form [n], where n is an integer.
This ID indicates the group they belong to, it can be used to filter for a workout group in Golden Cheetah.
The user will be prompted to choose a directory containing workout files to process.
It creates a new output directory with the suffix _tagged in the same parent directory as the input.

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
    file_count = 0

    # Initialize Tkinter and hide the root window
    root = tk.Tk()
    root.withdraw()

    # Ask the user for the source directory containing workout files
    in_dir_root = open_dir_dialog("Select workout directory")
    root.destroy()
    if not in_dir_root:
        print("No directory selected. Exiting.", file=sys.stderr)
        sys.exit(1)

    in_dir_root_parent, in_dir_root_name = os.path.split(in_dir_root)
    out_root_dir = os.path.join(in_dir_root_parent, f"{in_dir_root_name}_tagged")
    make_path(out_root_dir)

    # Maps input dir path to its hierarchical id (e.g., "2.1.3")
    dir_id_map = {in_dir_root: ""}
    # Maps input dir path to the next child number
    child_counter_map = {}

    for cur_dir_name, subdir_list, filename_list in os.walk(in_dir_root, topdown=True):
        # Get parent id
        parent_dir = os.path.dirname(cur_dir_name)
        parent_id = dir_id_map.get(parent_dir, "")

        # Assign id to current directory if not top-level
        if cur_dir_name == in_dir_root:
            cur_id = ""
        else:
            # Get next child number for parent
            child_num = child_counter_map.get(parent_dir, 1)
            cur_id = f"{parent_id}-{child_num}" if parent_id else f"{child_num}"
            dir_id_map[cur_dir_name] = cur_id
            child_counter_map[parent_dir] = child_num + 1

        # Prepare id assignment for subdirectories
        child_counter_map[cur_dir_name] = 1

        for in_filename in filename_list:
            in_fullpath = os.path.join(cur_dir_name, in_filename)
            file_stem, file_extension = os.path.splitext(in_filename)
            if file_extension.lower() in ['.zwo', '.xml']:
                try:
                    with open(in_fullpath, "r", encoding="utf-8", errors="replace") as xfile:
                        xml_content = xfile.read()
                    group_id = dir_id_map.get(cur_dir_name, "")
                    basedir = os.path.basename(os.path.normpath(cur_dir_name))
                    updated_xml = update_workout_xml(xml_content, group_id, 'File: ' + basedir + '/ ' + file_stem)
                except (IOError, ValueError) as error:
                    print(f"Error processing file {in_fullpath}: {error}", file=sys.stderr)
                    continue

            # Prepare output path
            relative_path = os.path.relpath(in_fullpath, in_dir_root)
            relative_dir = os.path.dirname(relative_path)
            if relative_dir == "":
                # File is in the top-level input directory
                out_dirname = out_root_dir
            else:
                # Build the output path, tagging every directory in the path
                parts = relative_dir.split(os.sep)
                tagged_parts = []
                path_so_far = in_dir_root
                for part in parts:
                    path_so_far = os.path.join(path_so_far, part)
                    tag = dir_id_map.get(path_so_far, "")
                    tagged_parts.append(f"{part}_[{tag}]")
                out_dirname = os.path.join(out_root_dir, *tagged_parts)
            make_path(out_dirname)
            output_fullpath = os.path.join(out_dirname, in_filename)

            try:
                with open(output_fullpath, "w", encoding="utf-8") as xfile:
                    xfile.write(updated_xml)
                file_count += 1
            except IOError as error:
                print(f"Error writing to file {output_fullpath}: {error}", file=sys.stderr)

    print(f"Processed {len(dir_id_map)-1} groups, {file_count} files.")


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Aborting. Python 3 must be installed!")
    main()
