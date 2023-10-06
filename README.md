# File Sorter

This is a program to sort files in a given folder into categories based on the file extension.

It uses **multithreading** to concurrently move files into their respective category folders. File names are normalized by transliterating Cyrillic characters into Latin equivalents and replacing invalid characters with underscores. Conflicting file names are deduplicated by appending a counter.

Overall this provides a simple utility to automatically sort a messy folder of mixed file types into a clean organized folder structure.

## Usage

To run the program, execute:

```
python main.py --source <folder_path>
```

Where `<folder_path>` is the path to the folder whose files you want to sort.

After running, the program will create subfolders like `audio`, `video`, `documents` etc inside the given folder and move the files into their respective categories.

Supported categories:

- `audio`: mp3, ogg, wav, amr, flac
- `video`: avi, mp4, mov, mkv
- `documents`: doc, docx, txt, pdf, xlsx, pptx, odt
- `archives`: zip, gz, tar, 7z
- `images`: jpeg, png, jpg, svg, webp
- All other files go into the `other` category.

After sorting, empty subfolders are deleted. Any archives like .zip files in the 'archives' folder are extracted into the same location.

## Requirements
The following Python libraries are required:

- pathlib
- shutil
- threading
- logging
- py7zr (for extracting 7z archives)

## License
This project is licensed under the MIT License.
