import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = [i.strip() for i in f]

setuptools.setup(
    name="http(s)-http_client",
    version="1.0",
    author="Andrey Ozhigov",
    author_email="andreyozhigoff@yandex.ru",
    description="A simple http(s)-http_client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7"
)
