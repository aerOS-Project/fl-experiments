# FL experiments

The following repository contains the setup and obtained results of FL experiments.

## Description of conducted experiments

### Hardware setup

The experiments were carried out on two different infrastructures:
1. **Single Local Virtual Machine (Centralized setup)**: 
    - **CPU**: Intel(R) Xeon(R) CPU E5-2673 v4 @ 2.30GHz (2 cores, 4 processors), 
    - **RAM**: 16 GB
    - **Deomplyment method**: Services deployed as images within AMD64 Linux local Docker containers
2. **aerOS Continuum (Decentralized setup):**
    - **CPU**: x64 Architecture, 4 cores,
    - **RAM**: 15.6 GB
    - **Deployment method**: Containers deployed on Linux-based aerOS continuum

### Dataset Description

The training dataset was generated semi-synthetically using the Extended Green Cloud Simulator (EGCS), a simulation model of CloudFerro green edge infrastructure. It represents resource utilization during computational task execution throughout the entire year and combines:
1. Real weather condition data monitored by Electrum throughout the year 2024
2. Simulated using EGCS resource utilization
3. Simulated resource demands of computational tasks generated based on real tasks processed in CloudFerro infrastructure

The dataset was composed of **10156 observations** in total and was divided into 4 different subsets, each corresponding to an individual season of the year:
1. (Winter) **2539 observations**
2. (Spring) **2750 observations**
3. (Summer) **2727 observations**
4. (Autumn) **2143 observations**

All of the subsets were subsequently randomly divided in half, as such representing the client’s local data used for training.

### Training

The training objective was to learn an effective task migration strategy — specifically, to identify when factors such as CPU usage and weather conditions should trigger task migration. The ultimate aim was to maximize the utilization of servers powered by green energy. 

Training was performed simultaneously on two clients (**FL Local Operations**), with the Federated Averaging (FedAvg) algorithm used to aggregate model updates across the clients. The trained model was a simple neural network with a single hidden layer. The experiments were run for each data subset separately, resulting in running 4 training experiments on each infrastructure. 

## Repository content
The repository is organized into the following directories and files:

### `/energy_reports/`
Contains energy efficiency diagnostics and power consumption data collected during the FL training experiments:
- **`energy-report-training-Q1.html`** to **`energy-report-training-Q4.html`**: Power efficiency diagnostic reports generated using Windows `powercfg /energy` command for each quarterly training session
- **`results_aeros.md`**: Summary of energy utilization measurements across aerOS Continuum nodes during training, showing average energy consumption per quarter and node on which local operation client was deployed
- **`transfer/data_transfer.csv`**: Time-series data capturing data transfer metrics for sending data between VMs (used to justify missing energy consumption saving) 

### `/scripts/`
Utility scripts:
- **`estimate_power_from_report.py`**: Python script that parses HTML energy reports and estimates power consumption based on CPU utilization, device states, and configurable power coefficients
- **`upload_model.py`**: Script for uploading trained FL models to the FL Repository component via REST API

### `/setup/`
Configuration files and resources required for FL experiment setup:

#### `/setup/configs/`
- **`local-operations/`**: Client-side configuration files
  - `setup.json`: Data loader and client library configuration
  - `model.json`, `format.json`: Model architecture and data format specifications
  - `transformation_pipeline_train.json`, `transformation_pipeline_test.json`: Data preprocessing pipeline definitions
- **`orchestrator/`**: Server-side configuration
  - `training_config.json`: FL training parameters 

#### `/setup/data_loaders/`
- **`application.tests.migration_loader.pkl`** and **`.zip`**: Serialized data loader implementations necesary to run the training

#### `/setup/model/`
- **`migration_predictor_v1.zip`**: Packaged FL model used in training

### `/training_results/`
Quantitative results from FL training experiments on both infrastructures:

#### `/training_results/aeros/`
Results from aerOS Continuum (decentralized) infrastructure:
- **`training_results_Q1.json`** to **`training_results_Q4.json`**: Training metrics including final loss, accuracy, number of federated rounds, and model metadata for each dataset

#### `/training_results/local/`
Results from local VM (centralized) infrastructure:
- **`training_results_Q1.json`** to **`training_results_Q4.json`**: Corresponding training metrics from the local Docker-based setup for performance comparison