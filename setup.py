import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-privacy-policy-tools_updated",
    version="0.2.0",
    author="Abass Conteh",
    author_email="abassconteh@gmail.com",
    description="A highly configurable Django app to manage privacy policies and confirmations with enhanced features.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wachjose88/django-privacy-policy-tools",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'django>=4.2.0',
        'django-ckeditor',
        'django-tinymce',
        'djangorestframework>=3.12.0',
        'bleach',
        'django-modeltranslation'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)