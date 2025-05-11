import os
import sys


def setup_directories():
    """Create necessary directories for the project."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    dirs_to_create = [
        'static',            # For custom static files
        'staticfiles',       # For collected static files
        'media',             # For user uploaded files
        'media/uploads',     # For general uploads
        'media/user_images',  # For user profile images
        'templates',         # For custom templates
    ]

    created_count = 0
    for directory in dirs_to_create:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")
            created_count += 1
        else:
            print(f"Directory already exists: {dir_path}")

    # Create a .gitkeep file in empty directories to ensure they're tracked by git
    for directory in dirs_to_create:
        dir_path = os.path.join(base_dir, directory)
        gitkeep_path = os.path.join(dir_path, '.gitkeep')
        if not os.listdir(dir_path) and not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                pass
            print(f"Created .gitkeep in: {dir_path}")

    print(f"\nSetup complete! Created {created_count} new directories.")
    print("You can now run 'python manage.py collectstatic' to collect all static files.")


if __name__ == "__main__":
    setup_directories()
