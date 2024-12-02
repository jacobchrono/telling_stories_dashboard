# https://chatgpt.com/share/6737011d-eef4-800a-9cc6-933945fb6dc4
# This is a script to generate a requirements.txt.
# The requirements.txt tells the streamlit cloud what versions of the packages I am using to run the script 
# final_dash_2.py. 

import subprocess
import os

# List of explicitly imported packages
packages = [
    "streamlit",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "statsmodels",
    "plotly"
]

# Specify the directory to save the requirements.txt file
repo_root = r"C:\Users\jakeq\OneDrive\Documents\github\telling_stories_dashboard"
output_file = os.path.join(repo_root, "requirements.txt")

def generate_requirements(packages, output_file):
    requirements = []
    for package in packages:
        try:
            # Get the installed version of the package
            result = subprocess.run(
                ["pip", "show", package],
                capture_output=True,
                text=True
            )
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                    requirements.append(f"{package}=={version}")
                    break
        except Exception as e:
            print(f"Error retrieving version for {package}: {e}")

    # Write to the requirements.txt file in the specified location
    with open(output_file, "w") as f:
        f.write("\n".join(requirements))
    print(f"Requirements file generated at: {output_file}")

# Generate the requirements.txt
generate_requirements(packages, output_file)
