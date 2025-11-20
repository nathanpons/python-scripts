# Python Scripts Desktop App

A modern desktop application built with Python and CustomTkinter that provides useful utilities including weather information and recipe finding as well as automation tools. The app uses AWS Lambda functions as proxy servers to securely handle API keys.

## Features

- **Weather Dashboard**: Get current weather information for any city
  - Temperature in Celsius and Fahrenheit
  - Humidity levels
  - Weather descriptions and icons
  - Clean, modern UI with real-time data

- **Recipe Finder**: Search for recipes by ingredients
  - Enter ingredients you have on hand
  - Get multiple recipe suggestions
  - View recipe images, preparation time, and servings
  - Scrollable results display

- **Hold Key Script**: Hold or rapidly press keys or mouse clicks
  - Enter key you would like to be held down / rapidly pressed and they key to toggle the script
  - Able to change the rate of presses

- **Secure API Key Management**: API keys are stored server-side in AWS Lambda functions, not exposed in the desktop application

## Prerequisites

- python 3.10 or higher
- pip

## Installation

- There are a few options for installation

 1. Download the official release on the 'Releases' tab on GitHub and running the .EXE file. (Recommended)
 2. Cloning the repository and running the app through local code and creating an AWS cloud environment. You will need your own API keys for **Spoonacular** and **OpenWeatherApi**. You will also need to provide 
 your own AWS credentials. Again, it is recommended to just install the official release as described above.

    ```bash
    git clone https://github.com/PapsBurr/python-scripts.git
    cd python-scripts
    pip install -r requirements
    python lambda/create_lambda_package.py
    cd terraform
    terraform init
    terraform apply
    cd ..
    python src/main.py
    ```

    **If you just wish to use the automation scripts you do not need to run the 'lambda/create_lambda_package.py' or terraform commands.**
