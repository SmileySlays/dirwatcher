Dirwatcher
==========

Program to watch the changes of files in a given directory for a string.

To call you must give it the string, the name of the directory, and then an optional file extension or time interval as arguments.

Creates a .log file that logs all the errors, instances of a string in a file, and any files deleted or added in the directory.

Main
----

Hooks the signals up with the os while also creating start and end banners,
and calling the watch_directory() function with the arguments passed through
if their is not exit_flag. Otherwise it throws an error.

Signal Handler
--------------

Sends the signal that kills the program.

Watch Directory
---------------

Takes in the directory you want to watch, the string you want to search for,
and the extension (which defaults to .txt if not given) as arguments.

This function is what calls the detect_removed_files(), detect_added_files(), and magic_string() functions. It also changes the path towards the directory you want to watch.

Detect Removed Files
------------------

If a file isn't in the current dictionary it will log that the file was removed and make sure the dictionary is not changing indexes while being iterated over.

Detect Added Files
------------------

Checks if name is added to the dictionary, if not it logs that it's been added.

Magic String
---------------

Runs through the files in the directory and logs the line which it found the string, the name of the string, and which file it was found it. It should only log it once and will log any new ones of files that get added or any text appended to a file already in the directory.