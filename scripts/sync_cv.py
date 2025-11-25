import os
import shutil
import sys

# Configuration
CV_REPO_PATH = "assets/cv_repo"
CV_PDF_NAME = "CV_Industry_US/CV_Industry_US.pdf"
DEST_PDF_PATH = "assets/pdf/Maurice_Hanisch_CV.pdf"

def sync_cv():
    # Check if repo exists
    if not os.path.exists(CV_REPO_PATH):
        print(f"Error: CV repository not found at {CV_REPO_PATH}")
        print("Please clone your private CV repository to this location:")
        print(f"  git clone git@github.com:MauriceDHanisch/CV_MHANISCH_US.git {CV_REPO_PATH}")
        print("  (Make sure to add it to .gitignore if you haven't already)")
        return

    # Construct source path
    src_pdf = os.path.join(CV_REPO_PATH, CV_PDF_NAME)
    
    if not os.path.exists(src_pdf):
        print(f"Error: PDF not found at {src_pdf}")
        return

    # Copy file
    try:
        shutil.copy2(src_pdf, DEST_PDF_PATH)
        print(f"Successfully updated CV at {DEST_PDF_PATH}")
    except Exception as e:
        print(f"Error copying file: {e}")

if __name__ == "__main__":
    sync_cv()
