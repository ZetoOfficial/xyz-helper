# XYZ-Helper Backend

XYZ-Helper is a backend application designed for working with XYZ files. It provides functionality for elbow plot generation and point segmentation. Additionally, the application offers caching, importing, and exporting features.

## Features

- Elbow plot generation for data analysis.
- Point segmentation to identify distinct clusters.
- Caching to optimize performance and reduce redundant calculations.
- Import and export functions for working with XYZ files.

## Technologies

XYZ-Helper is built using the following technologies:

- Python3.9
- FastAPI
- NumPy
- PyVista
- pandas
- scikit-learn (Gaussian Mixture)

## Getting Started

To get started with XYZ-Helper, follow these steps:

- Clone this repository: `git clone https://github.com/your-username/xyz-helper.git`
- Navigate to the project directory: `cd xyz-helper`

## Usage

- Install the required dependencies using pip: `pip install -r requirements.txt`
- Run the FastAPI server: `uvicorn main:app --host=localhost --port=8080`

The application will be accessible at http://localhost:8080.

## API Endpoints

XYZ-Helper provides the following API endpoints for interacting with the application:

- `POST /upload_file`: Upload an XYZ file for processing. Returns an UploadFileResponse.
- `POST /load_file`: Load data from a previously processed XYZ file. Returns a LoadFileResponse.
- `POST /export`: Export processed data to a file. Returns the exported file using FileResponse.
- `POST /elbow_rule_graphic`: Generate an elbow rule graphic for data analysis. Returns an ElbowRuleGraphicResponse.
- `POST /generate_image`: Generate an image based on the processed data. Returns a GenerateImageResponse.
- `POST /show_image`: Display an image based on the processed data. Returns a ShowImageResponse.

For detailed information about request and response formats, please refer to the [API documentation](http://localhost:8080/api/redoc).
