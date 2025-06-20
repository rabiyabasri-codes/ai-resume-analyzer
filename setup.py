from setuptools import setup

setup(
    name="resume-analyzer",
    version="1.0",
    install_requires=[
        "flask==2.0.1",
        "spacy==3.7.2",
        "PyMuPDF==1.21.1",
        "python-dotenv==0.19.0",
        "Werkzeug==2.0.1",
        "thinc==8.1.12",
        "typing-extensions==4.7.1",
        "numpy>=1.19.0",
        "tqdm>=4.38.0",
    ],
    python_requires=">=3.7",
) 