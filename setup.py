from setuptools import setup
import os

def get_scripts():
    
    
    #['hellllow = scripts:hellllow:main']
    scripts = []
    for dirpath, dirnames, filenames in os.walk('scripts'):
        for filename in filenames:
            if filename.endswith('.py'):
                script_name = os.path.splitext(filename)[0]
                scripts.append(f'{script_name} = {dirpath.replace("/", ".")}.{script_name}:main')
    return scripts

if __name__ == "__main__":

    console_scripts = get_scripts()
    
    setup(entry_points=dict(

            console_scripts=console_scripts
    ))
""" from setuptools import setup, find_packages
import glob
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_scripts():
    
    
    #['hellllow = scripts:hellllow:main']
    scripts = []
    for dirpath, dirnames, filenames in os.walk('scripts'):
        for filename in filenames:
            if filename.endswith('.py'):
                script_path = os.path.join(dirpath, filename)
                script_name = os.path.splitext(filename)[0]
                scripts.append(f'{script_name} = {dirpath.replace("/", ".")}.{script_name}:main')
    return scripts




setup(
    name='amplikraken',
    version=version.get(),
    author='Andrea Telatin',
    description='Metabarcoding Analysis using Kraken2',
    packages=find_packages(),
    #scripts=glob.glob('scripts/*.py'),
    # get requirements.txt     
    entry_points={
        'console_scripts': get_scripts(),
    },
    install_requires=[line.strip() for line in open('requirements.txt')],
    license='MIT',
    scripts=['scripts/hellllow.py'],
    classifiers=[
        'Development Status :: 4 - Beta',
		'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    # Python >= 3.6
    python_requires='>=3.6',
)
#
 """