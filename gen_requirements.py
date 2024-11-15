import os

repo_dir = "C:/Users/jakeq/OneDrive/Documents/github/telling_stories_dashboard"
os.system(f"pip freeze > {os.path.join(repo_dir, 'requirements.txt')}")