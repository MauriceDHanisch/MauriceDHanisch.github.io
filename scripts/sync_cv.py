import os
import shutil
import subprocess

# Configuration
CV_REPO_URL = "git@github.com:MauriceDHanisch/CV_MHANISCH_US.git"
CV_REPO_PATH = "assets/cv_repo"
CV_PDF_NAME = "CV_Industry_US/CV_Industry_US.pdf"
DEST_PDF_PATH = "assets/pdf/Maurice_Hanisch_CV.pdf"

def sync_cv():
    # Clone repo if it doesn't exist
    if not os.path.exists(CV_REPO_PATH):
        print(f"CV repository not found. Cloning from {CV_REPO_URL}...")
        try:
            subprocess.run(
                ["git", "clone", CV_REPO_URL, CV_REPO_PATH],
                check=True
            )
            print("Repository cloned successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return
    else:
        # Pull latest changes if repo exists
        print(f"CV repository found. Pulling latest changes...")
        try:
            subprocess.run(
                ["git", "-C", CV_REPO_PATH, "pull"],
                check=True
            )
            print("Repository updated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error pulling repository: {e}")
            return

    # Construct source path
    src_pdf = os.path.join(CV_REPO_PATH, CV_PDF_NAME)
    
    if not os.path.exists(src_pdf):
        print(f"Error: PDF not found at {src_pdf}")
        return

    # Ensure destination directory exists
    os.makedirs(os.path.dirname(DEST_PDF_PATH), exist_ok=True)

    # Copy file
    try:
        shutil.copy2(src_pdf, DEST_PDF_PATH)
        print(f"Successfully copied CV to {DEST_PDF_PATH}")
    except Exception as e:
        print(f"Error copying file: {e}")

if __name__ == "__main__":
    sync_cv()
