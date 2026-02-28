# Setup SSH (mac/windows git bash)

Note: On windows, use git bash. The setup commands don't work on cmd

1) ssh-keygen -t ed25519 -C "somename@device"
2) eval "$(ssh-agent -s)"
3) ssh-add ~/.ssh/id_ed25519
4) pbcopy < ~/.ssh/id_ed25519.pub (mac)
   cat ~/.ssh/id_ed25519.pub | clip (windows git bash)
5) GitHub → Settings → SSH and GPG keys → New SSH key
6) git clone  git@github.com:ChristianGeyer/image-pipeline.git (clone)
   git remote set-url origin git@github.com:ChristianGeyer/image-pipeline.git (change link if needed, already cloned)
7) ssh -T git@github.com

# Git workflow

1) git checkout main
   git pull origin main
2) git checkout -b feature/calibration-module
3) git branch (to check branches)
4) git add .
   git commit -m "message"
5) git push -u origin feature/calibration-module (first push)
   git push (after the first)
6) Github -> Compare&PullRequest -> Review Changes -> Merge
7) git branch -d feature/calibration-module
8) git push origin --delete feature/calibration-module

# Venv Setup (mac)

1) python3 -m venv .venv
2) source .venv/bin/activate
3) python -m pip install --upgrade pip
4) python -m pip install -r requirements.txt
5) python -m pip install -e .

# Venv Setup (windows git bash)

1) python -m venv .venv
2) source .venv/Scripts/activate
3) python -m pip install --upgrade pip
4) python -m pip install -r requirements.txt
5) python -m pip install -e .