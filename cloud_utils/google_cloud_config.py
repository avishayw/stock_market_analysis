import json

# GOOGLE_APPLICATION_CREDENTIALS
# credentials dict from file


def save_credentials_to_file(filename):
    with open(filename, 'w') as f:
        json.dump(credentials_dict, f)
    return filename
