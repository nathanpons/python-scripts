import zipfile
import os
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

def create_lambda_package(lambda_dir, output_name):
    """Creates a deployment package for AWS Lambda functions."""
    zip_path = os.path.join(lambda_dir, output_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(lambda_dir):
            # Skip __pycache__ directories and the output zip file itself
            if '__pycache__' in root or output_name in root:
                continue
            # Skip other lambda function directories
            if any(other_dir in root for other_dir in ['weather', 'recipe'] if other_dir not in lambda_dir):
                continue
            for file in files:
                # Skip this packaging script
                if file == 'create_lambda_package.py':
                    continue
                if file.endswith('.zip'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, lambda_dir)
                zipf.write(file_path, arcname)

    logging.debug(f"Created deployment package at {zip_path}")

if __name__ == "__main__":
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for item in os.listdir(script_dir):
            item_path = os.path.join(script_dir, item)

            if os.path.isdir(item_path) and not item.startswith('.') and not item.startswith('__'):
                logging.debug(f"Creating lambda package for directory: {item_path}/{item}")
                create_lambda_package(item_path, 'deployment_package.zip')

        logging.debug("All lambda packages created successfully.")
    except Exception as e:
        logging.error(f"Error creating lambda packages: {e}")


    