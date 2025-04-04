#!/usr/bin/env python3
"""
Tag the name field in Zwift workouts with an ID in the form [n], where n in an integer.
This ID indicates the group they belong to, it can be used to filter for a workout group in Golden Cheetah.
The user will be prompted to choose a directory containing workout files to process.
Output files are written to a directory of a similar name, with a suffix of _tagged.

Author: Robert Drohan
Copyright: Copyright 2025, Robert Drohan
License: GPLv3
Version: 1.01
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
    if selected_dir:
        return selected_dir
    exit("No directory selected.")


def make_path(path):
    """Create a directory path if it doesn't already exist."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def main():
    file_count = 0
    dir_count = 0

    # Initialize Tkinter and hide the root window
    root = tk.Tk()
    root.withdraw()

    # Ask the user for the source directory containing workout files
    in_dir_root = open_dir_dialog("Select workout directory")
    dir_nodes = os.path.split(in_dir_root)
    out_root_dir = os.path.join(dir_nodes[0], f"{dir_nodes[1]}_tagged")
    make_path(out_root_dir)

    # Walk through the directory tree
    for cur_dir_name, subdir_list, filename_list in os.walk(in_dir_root, topdown=True):
        dir_count += 1
        for in_filename in filename_list:
            in_fullpath = os.path.join(cur_dir_name, in_filename)

            # Process Zwift files with a .zwo or .xml extension
            fnx, file_extension = os.path.splitext(in_filename)
            if file_extension in ['.zwo', '.xml']:
                try:
                    # Open file with error handling for invalid UTF characters.
                    with open(in_fullpath, "r", encoding="utf-8", errors="replace") as xfile:
                        xml_content = xfile.read()

                    # Parse the cleaned up XML content
                    root = ET.fromstring(xml_content)

                except (IOError, ET.ParseError) as error:
                    print(f"Error processing file {in_fullpath}: {error}")
                    continue

                # Find and update the <name> element in the XML.
                name_element = root.find("name")
                if name_element is not None:
                    # Add the group ID to the name element
                    name_element.text += f" [{dir_count}]"
                    updated_xml = ET.tostring(root, encoding="unicode")

                    # Create the output file and write the updated XML to it.
                    relative_path = os.path.relpath(in_fullpath, in_dir_root)
                    inter_path = os.path.join(out_root_dir, relative_path)
                    inter_dirname = os.path.dirname(inter_path)
                    # Create the new directory name with the suffix
                    out_dirname = f"{inter_dirname}_[{dir_count}]"
                    output_fullpath = os.path.join(out_dirname, in_filename)
                    make_path(out_dirname)

                    try:
                        with open(output_fullpath, "w", encoding="utf-8") as xfile:
                            xfile.write(updated_xml)
                        file_count += 1
                    except IOError as error:
                        print(f"Error writing to file {output_fullpath}: {error}")

    print(f"Processed {dir_count} groups, {file_count} files.")


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Aborting. Python 3 must be installed!")
    main()
