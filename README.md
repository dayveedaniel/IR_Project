## Project Overview

This is the GitHub project of Team Double Oreo for the Advanced Information Retrieval course, year 2025. The project aims to implement a Retrieval-Augmented Generation (RAG) system that functions as a smart librarian or file explorer for companies and institutions with extensive text-based files. The goal is to enable quick and efficient information retrieval from these files.

### System Workflow

1. **Data Extraction**: Extract text and potentially media information from files.
2. **Text Indexing and Processing**: Implement indexing and processing on the extracted text.
3. **Vector Indexing**: Perform vector indexing on the text to facilitate faster searches and result retrieval.
4. **Integration with LLM**: Pass the search results to a Large Language Model (LLM) for further processing.
5. **User Interface**: Display the processed results to the user through an interactive UI.

### Project Components

#### Data Mining and Processing

Since we lack the volume of files necessary for this project, we will mine data from Wikipedia, specifically from the "Artificial Intelligence" category.

- The Python scripts and Jupyter notebooks for running this process are located in the [data_mining](./data_mining) folder.
- To run the script, execute the following command: `python data_miner.py` (complete with any additional instructions).
- Once the script completes, the mined data is saved to the [data](./data) folder.

#### Data Processing

(Provide details on how the data is processed after mining, including any specific techniques or libraries used.)

#### Indexing and Search with Vector

(Describe the vector indexing process, including any libraries or algorithms used to enable fast search capabilities.)

#### Integration with LLM

(Explain how the system integrates with a Large Language Model to process and refine search results.)

#### User Interface

The project includes a user interface where users can view and interact with the data. It features a search bar and various options for filtering results.

- The UI is developed using Flutter, making it cross-platform.
- To run the UI, follow these steps:
  - Install the [Flutter SDK](https://flutter.dev/docs/get-started/install).
  - Ensure Flutter is added to your system's PATH.
  - Run the command `flutter run` and choose the platform to run on.
