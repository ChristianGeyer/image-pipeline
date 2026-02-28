# Setup SSH

1) ssh-keygen -t ed25519 -C "somename@device"

2) eval "$(ssh-agent -s)"

3) ssh-add ~/.ssh/id_ed25519

4) pbcopy < ~/.ssh/id_ed25519.pub

5) GitHub → Settings → SSH and GPG keys → New SSH key

6) git remote set-url origin git@github.com:ChristianGeyer/image-pipeline.git

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

3) python3 -m pip freeze > requirements.txt

4) python3 -m pip install -e .

# Venv Setup (windows PowerShell)

1) py -m venv .venv

2) .\.venv\Scripts\activate

3) python -m pip install -r requirements.txt

4) python -m pip install -e .