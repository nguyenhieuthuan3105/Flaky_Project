This is the replication package associated with the paper: 'FlakyFix: Using Large Language Models for Predicting Flaky Test Fix Categories and Test for Code Repair'

### Requirements
This is a list of all required python packages:
-imbalanced_learn==0.8.1
-numpy==1.19.5
-pandas==1.3.3
-transformers==4.10.2
-torch==1.5.0
-scikit_learn==0.24.2
-openai==v0.28.1

#Automated tool for labelling dataset with flaky test fix categories

This is a step-by-step guideline for automatically labelling dataset with flaky test fix categories


### Input Files:
This is a an input file that is required to accomplish this step:
* Data/IdoFT_dataset_filtered.csv
https://figshare.com/s/47f0fb6207ac3f9e2351

### Output Files:
* Results/IdoFT_dataset_filtered.csv


### Replicating the experiment

This experiment can be executed using the following commands after navigating to the `Code\` folder:

```console
bash Automated_labelling_tool.sh
```

It will generate the dataset required to run our prediction models to predict the category of the fix, given a flaky test code

---

# Prediction models for fix categories using the test case code

This is the guideline for replicating the experiments we used to evaluate our prediction models i.e. CodeBERT and UniXcoder (fine-tuned with Few Shot Learning and Feed Forward Neural Network independently) for classifying tests with different fix categories. 

### Input Files:
This is a list of input files that are required to perform the binary classification for each fix category:
* Data/change_assertion.csv
*Data/change_condition.csv
*Data/change_data_format.csv
*Data/change_data_structure.csv
*Data/handle_exception.csv
*Data/reorder_data.csv
*Data/reset_variable.csv
*Data/call_static_method.csv
*Data/reorder_parameters.csv
*Data/misc.csv

### Replicating the experiment

To run experiment with our prediction model, navigate to the `Code\` folder and run the following commands:

```console
bash codemodel_with_fnn.sh
bash codemodel_with_fsl.sh
```

# Generate the repaired flaky tests using GPT 3.5 Turbo:

Input Files:
This is a an input file that is required to accomplish this step:

### Experiments on the 181 tests using prompts with and without labels:
* Data/Dataset_for_GPT.csv


### Experiments on the tests using prompts with, without labels and in-context learning:

###For Change Assertion:
* Data/change_assertion_input_FSP.csv
###For Change Condition:
* Data/change_condition_input_FSP.csv
###For Change DataStructure:
* Data/change_dataStructure_input_FSP.csv

To run this experiment, navigate to the `Code\` folder and run the following commands:

```console
bash gpt3.5_experiments.sh
```
# Execute a sample of GPT-reapired flaky tests:

Input Files:
This is a an input file that is required to accomplish this step:
* Data/sampleTests_For_Execution.csv

To execute the 35 GPT-repaired flaky tests:

-First Clone the Github project (From the 'PR Link' column in the sampleTests_For_Execution.csv file)
-Checkout on the the commit of the given PR link (if merged, checkout on the master branch)
-Navigate to the project folder and run command: 
```console
*mvn clean test -Dtest=[Test Class Name]#[Test Method Name] -DfailIfNoTests=false
```



