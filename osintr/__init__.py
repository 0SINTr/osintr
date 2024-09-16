'''0SINTr Project'''
import os
import sys

# Get the absolute path to the package's directory
package_dir = os.path.dirname(os.path.realpath(__file__))

# Check if the package's directory is already in sys.path, if not, add it
if package_dir not in sys.path:
    sys.path.append(package_dir)