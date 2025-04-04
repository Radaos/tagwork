#!/usr/bin/env python3
"""
Tag Zwift workout names with an ID in the form [n], where n in an integer.
This ID indicates the group they belong to, it can be used to filter for a group in Golden Cheetah.
The user will be prompted to choose a directory containing workout files to process.
Output files are written to a directory of a similar name, with a suffix of _tagged.

Author: Robert Drohan
Copyright: Copyright 2025, Robert Drohan
License: GPLv3
Version: 1.0
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
    initial_dir = 'C:\\'
    selected_dir = askdirectory(title=user_msg, initialdir=initial_dir)
    if selected_dir:
        return selected_dir
    exit("No directory selected.")


def make_path(path):
    """Create a directory path if it doesn't already exist."""
    try:
        os.makedirs(path)
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
    input_dir = open_dir_dialog("Select workout directory")
    input_dir_parts = os.path.split(input_dir)
    output_dir = os.path.join(input_dir_parts[0], f"{input_dir_parts[1]}_tagged")
    make_path(output_dir)

    for dirpath, dirnames, filenames in os.walk(input_dir, topdown=True):
        dir_count += 1
        for filename in filenames:
            input_file_path = os.path.join(dirpath, filename)
            file_name, file_extension = os.path.splitext(filename)

            # Process Zwift files with a .zwo or .xml extension
            if file_extension in ['.zwo', '.xml']:
                try:
                    # Read the file with error handling for invalid UTF characters
                    with open(input_file_path, "r", encoding="utf-8", errors="replace") as file:
                        xml_content = file.read()

                    # Parse the cleaned up XML content
                    root = ET.fromstring(xml_content)

                except IOError as error:
                    print(f"[IO] I/O Error {error.errno}: {error.strerror}")
                    continue
                except ET.ParseError as error:
                    print(f"XML Parsing Error: {error}")
                    continue
                else:
                    # Find and update the <name> element in the XML.
                    name_element = root.find("name")
                    if name_element is not None:
                        name_element.text += f" [{dir_count}]"
                        updated_xml = ET.tostring(root, encoding="unicode")

                        # Create the output file and write the updated XML to it.
                        relative_path = os.path.relpath(input_file_path, input_dir)
                        output_file_path = os.path.join(output_dir, relative_path)
                        output_file_dir = os.path.dirname(output_file_path)
                        make_path(output_file_dir)

                        try:
                            with open(output_file_path, "w", encoding="utf-8") as file:
                                file.write(updated_xml)
                            file_count += 1
                        except IOError as error:
                            print(f"Error writing to file {output_file_path}: {error}")

    print(f"Processed {dir_count} groups, {file_count} files.")


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Aborting. Python 3 must be installed!")
    main()
