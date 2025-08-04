#Project Specification Document\
##Project Title: Tagwork\
##Purpose: To enhance the organization and filtering of Zwift workout files by tagging workout metadata with hierarchical group identifiers derived from file structure.\
\
##Functional Requirements\
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
