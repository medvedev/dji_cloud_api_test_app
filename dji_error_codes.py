
class DjiErrorCodes:
    def __init__(self):
        error_codes = {}

        # Open the file in read mode
        with open('resources/dji_error_codes.txt', 'r') as file:
            # Process each line
            for line in file:
                # Split the line by space and convert the first part to int, second part is the string
                key, value = tuple(line.split(maxsplit=1))
                error_codes[int(key)] = value.strip()  # Strip to remove any trailing newline characters

        self.error_codes = error_codes

    def __getitem__(self, error_code):
        if error_code in self.error_codes:
            return self.error_codes[error_code]
        return None

