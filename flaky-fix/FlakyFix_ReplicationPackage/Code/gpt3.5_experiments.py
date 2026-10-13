import pandas as pd
import numpy as np
import time
import openai
import nltk
from nltk.translate.bleu_score import corpus_bleu
from nltk.translate.bleu_score import sentence_bleu,SmoothingFunction
smoothing = SmoothingFunction()

openaAI_key='' #add key from openAI account
openai.api_key = openaAI_key

data='../Data/Dataset_for_GPT.csv' #comment this for in-context learning
#uncomment below lines to run the prompts for in-context learning:
#data='../Data/change_assertion_input_FSP.csv'
#data='../Data/change_condition_input_FSP.csv'
#data='../Data/change_dataStructure_input_FSP.csv'
dataset = pd.read_csv(data)

#uncomment below lines to run the prompts for in-context learning:
#prompt_FSP = "Here are some examples of flaky tests and their fixes based on the labels associated with them:\n\n"
#for index, row in change_dataStructure_FSP.iterrows():
    #prompt_FSP += f"Flaky Test: {row['Flaky Code']}\n"
    #prompt_FSP += f"Fixed Test: {row['Fixed Flaky Code']}\n"
    #prompt_FSP += f"Label: {row['Auto_labels']}\n\n"

x=0
gens=[]
for index, row in dataset.iterrows():
                    # print(x)
                    # if x>26:
                                print(x)
                                flakycode=row['Flaky Code']
                                label=row['Auto_labels']
                                prompt='This test case is Flaky: '+ flakycode+ 'This test can be fixed by changing following in the code: '+ label + 'Just Provide the full fixed code of this test case only without any other text description'
                                # prompt='This test case is Flaky: '+ flakycode+ 'Just Provide the fixed code of this test case only to make it non-flaky. Do not provide any any other text description.' #uncomment this line to test the model with prompt without label.
                                #prompt = prompt_FSP+ '     Based on these examples, For this    '+ flakycode+ '   with a specific label:     '+ label+  '   Just Provide the full fixed test code of this test case only to make it non-flaky. Do not provide any any other text description.' #uncomment this line to test the model with prompt with in-context learning.
                                start_time_generation = time.time()
                                #calling GPT API
                                response = openai.ChatCompletion.create(
                                # model="gpt-4-1106-preview",
                                model="gpt-3.5-turbo-1106",  

                                messages=[
                                    {"role": "system", "content": "You are a helpful assistant for fixing flaky tests."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.7,
                                max_tokens=4096)

                                generation=response['choices'][0]['message']['content']

                                gens.append(generation)
                                x=x+1
                    # x=x+1

#post_process the generated codes:
def clean_test_cases(test_cases):
    prefix = '```java\n'
    suffix = '```'
    cleaned_cases = []
    for case in test_cases:
        if case.startswith(prefix):
            case = case[len(prefix):]
        if case.endswith(suffix):
            case = case[:-len(suffix)]
        cleaned_cases.append(case)
    return cleaned_cases

# Clean the test cases list
gens_ = clean_test_cases(gens)
dataset['gens']=gens_

#Evaluate the generated test code using Corpus and Sentence BLEU
groundtruth=dataset['Fixed Flaky Code'].tolist()
generations=dataset['gens'].tolist()

# Split strings of codes into lists of tokens
generated_codes = [code.split() for code in generations]
ground_truth_codes = [code.split() for code in groundtruth]

# Calculate corpus BLEU for each pair and store the scores
corpus_bleu_scores= []
for gen_code, true_code in zip(generated_codes, ground_truth_codes):
    bleu_score = corpus_bleu([[true_code]], [gen_code],smoothing_function=smoothing.method4)*100
    corpus_bleu_scores.append(bleu_score)

# Calculate average corpus BLEU score
average_corpus_bleu = sum(corpus_bleu_scores) / len(corpus_bleu_scores)

# print("Individual Corpus BLEU Scores:", corpus_bleu_scores)
print("Average Corpus BLEU Score:", average_corpus_bleu)

#sentence BLEU Score
smoothing = SmoothingFunction()
sentence_bleu_scores=[]
for i in range(len(groundtruth)):
    candidate_sentence=generations[i]
    label_=groundtruth[i]

    bleu_score = sentence_bleu([candidate_sentence.split()],label_.split(),smoothing_function=smoothing.method4)*100
    # print(bleu_score)
    sentence_bleu_scores.append(bleu_score)

average_sentence_bleu = sum(sentence_bleu_scores) / len(groundtruth)
print('averege sentence BLEU here is: ',average_sentence_bleu)
dataset['corpus_bleu']=corpus_bleu_scores
dataset['sentence_bleu']=sentence_bleu_scores

dataset.to_csv('../Results/gpt3.5_results.csv', index=False)