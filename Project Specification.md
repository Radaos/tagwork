# Project Specification Document
## Project Title: Tagwork Purpose: To enhance the organization and filtering of Zwift workout files by tagging workout metadata with hierarchical group identifiers derived from file structure.

## Functional Requirements
Workout Tagging System\
The application shall append a tag to each Zwift workout’s <name> field in one of the following formats:\
[i] — for workouts in a single-layer directory.\
[i-j] — for workouts in a nested directory structure, where:\
i identifies the top-level group.\
j identifies the sub-group.\
The tag shall always be placed at the end of the <name> field.\
Group Identification\
The system shall analyze the directory path of each workout file to determine its group assignment.\
For single-layer directories, a [i] tag shall be used.\
For nested directories, a [i-j] tag shall be used to represent both parent and child groups.\
The system shall support deeper hierarchies (e.g., [i-j-k]), though such cases are expected to be rare.\
Metadata Enhancement\
The application shall prepend the full directory path to the workout’s <description> field.\
This shall provide contextual information about the workout’s location within the file system.\
Search Optimization\
The tagged <name> and enriched <description> fields shall be compatible with filtering features in third-party software such as Golden Cheetah.\
The tagging shall enhance searchability and categorization of workouts based on their group hierarchy.

## Design Specifications
Technology Stack\
The application shall be developed using the Python programming language.\
It shall be compatible with standard Python environments and require no external dependencies beyond the standard library.\
File Structure\
The project shall include the following files:\
tagwork.py: Main script responsible for tagging logic.\
README.md: Documentation outlining usage, purpose, and setup instructions.\
LICENSE: Legal file specifying the use of the GPL-3.0 license.\
GC_workout_filter.png: Optional visual aid demonstrating the filtering effect in Golden Cheetah.\
Tag Format\
Tags shall strictly follow either the [i], [i-j], or [i-j-k] format.\
Tags shall be appended to the <name> field of each workout XML file.\
The application shall validate tag format consistency across all processed workouts.\
Directory-Based Grouping\
The application shall scan directories containing workout files.\
Each directory shall be treated as a distinct group, and nested directories shall be interpreted as sub-groups.\
The full directory path shall be prepended to the <description> field of each workout XML file.\
License\

The project shall be released under the GNU General Public License v3.0 (GPL-3.0), allowing free use, modification, and distribution under the same license terms.\
