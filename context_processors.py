import subprocess

def git_commit_id():
    try:
        commit_id = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        commit_id = 'N/A'  # Handle the case where Git is not available or the repository is not initialized
    return {'git_commit_id': commit_id}