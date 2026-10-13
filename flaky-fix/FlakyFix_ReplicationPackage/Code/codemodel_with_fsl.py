import time
import sys
import gc
import numpy as np
from pathlib import Path
import pandas as pd
import torch
import torch.nn as nn
import random
import gc
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import AdamW, AutoTokenizer, AutoModel, AutoConfig
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import train_test_split
import statistics
from sklearn.utils.multiclass import type_of_target
from pickle import load
from matplotlib.pylab import plt
from numpy import arange
import re
import string

# defining code model
model_name = 'microsoft/unixcoder-base'
# uncomment below to use CodeBERT model
# model_name = "microsoft/codebert-base"
model_config = AutoConfig.from_pretrained(model_name, return_dict=False, output_hidden_states=True)
tokenizer = AutoTokenizer.from_pretrained(model_name,use_fast=False)
auto_model =AutoModel.from_pretrained(model_name, config=model_config)

# setting the seed for reproducibility
def set_deterministic(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)                    
    torch.cuda.manual_seed(seed)               
    torch.cuda.manual_seed_all(seed)           
    torch.backends.cudnn.deterministic = True

dataset_path=sys.argv[1]
df= pd.read_csv(dataset_path)

# specify GPU
device = torch.device("cuda")

input_data=df[['flaky_code']]

target_data = df['label']

type_of_target(target_data)

# setting seed for data_loaders for output reproducibility
def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    numpy.random.seed(worker_seed)
    random.seed(worker_seed)


g = torch.Generator()
seed = 42 # any number 
set_deterministic(seed)

# converting code into tokens and then vector representation
def tokenize_data(text):

        tokens = tokenizer.batch_encode_plus(
        text.tolist(),
        max_length=1022, #set this to 510 while using CodeBERT
        pad_to_max_length=True,
        truncation=True)
        tokens_ids=tokenizer.convert_tokens_to_ids(tokens)
        return tokens

# converting vector representation to tensors
def text_to_tensors(tokens_train, tokens_val, tokens_test):
    train_seq = torch.tensor(tokens_train['input_ids'])
    train_mask = torch.tensor(tokens_train['attention_mask'])

    val_seq = torch.tensor(tokens_val['input_ids'])
    val_mask = torch.tensor(tokens_val['attention_mask'])

    test_seq = torch.tensor(tokens_test['input_ids'])
    test_mask = torch.tensor(tokens_test['attention_mask'])

    return train_seq, train_mask, val_seq, val_mask, test_seq, test_mask

def create_dataloaders(seq_anchor,mask_anchor,seq_pos,mask_pos,seq_neg,mask_neg,y):
    # define a batch size
    batch_size = 2

    # wrap tensors
    data = TensorDataset(seq_anchor,mask_anchor,seq_pos,mask_pos,seq_neg,mask_neg,y)

    # sampler for sampling the data during training
    train_sampler = RandomSampler(data)

    # dataLoader for dataset
    dataloader = DataLoader(data, sampler=train_sampler, batch_size=batch_size, worker_init_fn=seed_worker)

    return dataloader

#getting the updated dataloader for the test dataset:
def test_dataloaders(test_seq_anchor,test_mask_anchor, test_y):

        batch_size = 1

        # wrap tensors
        data = TensorDataset(test_seq_anchor,test_mask_anchor, test_y)

        # sampler for sampling the data during training
        test_set_sampler = RandomSampler(data)

        # dataLoader for train set
        test_set_dataloader = DataLoader(data, sampler=test_set_sampler, batch_size=batch_size, worker_init_fn=seed_worker)

        return test_set_dataloader


# setting up the neural network for CodeBERT fine-tuning
class BERT_Arch(nn.Module):

    def __init__(self, bert):

        super(BERT_Arch, self).__init__()

        self.bert = auto_model

        # dropout layer
        self.dropout = nn.Dropout(0.1)

        # relu activation function
        self.relu = nn.ReLU()

        # dense layer 1
        self.fc1 = nn.Linear(768, 512)

        
    # define the forward pass
    def forward(self, sent_id, mask):

        # generate the cls tag
        cls_hs = self.bert(sent_id, attention_mask=mask)[1]
        
        fc1_output = self.fc1(cls_hs)

        dropout_output = self.dropout(fc1_output)
        
        normalized = nn.functional.normalize(dropout_output)

        return normalized

class TripletLoss(nn.Module):
    def __init__(self, margin=1.0):
        super(TripletLoss, self).__init__()
        self.margin = margin
        
    def calc_euclidean(self, x1, x2):
        return (x1 - x2).pow(2).sum(1)
    
    def forward(self, anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor) -> torch.Tensor:
        distance_positive = self.calc_euclidean(anchor, positive)
        distance_negative = self.calc_euclidean(anchor, negative)
        losses = torch.relu(distance_positive - distance_negative + self.margin)

        return losses.mean()

triplet_loss = nn.TripletMarginLoss(margin=0.5, p=2)

class EarlyStopping:
    def __init__(self, tolerance=3, min_delta=0.005):

        self.tolerance = tolerance
        self.min_delta = min_delta
        self.counter = 0
        self.early_stop = False

    def __call__(self, train_loss, validation_loss):
        if (validation_loss - train_loss) > self.min_delta:
            self.counter +=1
            if self.counter >= self.tolerance:  
                self.early_stop = True

# Training the model
def train(train_dataloader):

    model.train()
    b_num=0
    total_loss=0
    
    #for Anchor
    # iterate over batches 
    for step, batch in enumerate(train_dataloader):
        
        # progress update after every 50 batches.
        b_num=int(b_num)+1
        # print("Now in the batch of training:  ",b_num)
        if step % 50 == 0 and not step == 0:

            print('  Batch {:>5,}  of  {:>5,}.'.format(step, len(train_dataloader)))
        
        # push the batch to gpu
        batch = [r.to(device) for r in batch]

        sent_id_a, mask_a, _,_,_,_,labels = batch

        _,_,sent_id_p,mask_id_p,_,_,labels = batch

        _,_,_,_,sent_id_n,sent_mask_n,labels = batch


        # clear previously calculated gradients
        model.zero_grad()

        # get model predictions for the current batch
        anchor_out = model(sent_id_a, mask_a)
        positive_out = model(sent_id_p,mask_id_p)
        negative_out = model(sent_id_n,sent_mask_n)
       
        loss = triplet_loss(anchor_out,  positive_out,negative_out )
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss=total_loss+loss.item()

    avg_loss = total_loss / len(train_dataloader)

    print("train loss final :",avg_loss)   
    return avg_loss

# Evaluating the model

def evaluate_(val_dataloader):

    model.eval()
    b_num=0
    total_loss=0
    
    #for Anchor
    # iterate over batches 
    for step, batch in enumerate(val_dataloader):

        b_num=int(b_num)+1
       
        if step % 50 == 0 and not step == 0:
            print('  Batch {:>5,}  of  {:>5,}.'.format(step, len(val_dataloader)))
        
        # push the batch to gpu
        batch = [r.to(device) for r in batch]

        sent_id_a, mask_a, _,_,_,_,labels = batch

        _,_,sent_id_p,mask_id_p,_,_,labels = batch

        _,_,_,_,sent_id_n,sent_mask_n,labels = batch


        # clear previously calculated gradients
        model.zero_grad()

        # get model predictions for the current batch
        anchor_out = model(sent_id_a, mask_a)
        positive_out = model(sent_id_p,mask_id_p)
        negative_out = model(sent_id_n,sent_mask_n)

        loss = triplet_loss(anchor_out,  positive_out,negative_out )
        total_loss=total_loss+loss.item()

    avg_loss = total_loss / len(val_dataloader)

    print("valid loss final :",avg_loss)   
    return avg_loss

#create the support set for Few-Shot-Learning

def create_support_set(X_train, y_train):
  result = pd.concat([X_train, y_train], axis=1, join='inner')
  flakyresult=result[result['label']==1]
  flakyresult_support_set= flakyresult.sample(n=10)
  non_flakyresult=result[result['label']==0]
  non_flaky_support_set= non_flakyresult.sample(n=10)
  support_set = pd.concat([flakyresult_support_set, non_flaky_support_set], ignore_index=True, sort=False)
  tokens_support_set = tokenizer.batch_encode_plus(
  support_set['Anchor'].tolist(),
  max_length=510,
  pad_to_max_length=True,
  truncation=True)
  support_set_seq = torch.tensor(tokens_support_set['input_ids'])
  support_set_mask = torch.tensor(tokens_support_set['attention_mask'])
  support_set_Y=np.asarray(support_set['label']).astype('float32')
  support_set_y = torch.tensor(support_set_Y)

  batch_size = 1

  # wrap tensors
  data = TensorDataset(support_set_seq,support_set_mask,support_set_y)

  # sampler for sampling the data during training
  support_set_sampler = RandomSampler(data)

  # dataLoader for train set
  support_set_dataloader = DataLoader(data, sampler=support_set_sampler, batch_size=batch_size, worker_init_fn=seed_worker)
  
  return support_set_dataloader

#create the embeddings for support set required for Few-Shot-Learning
def create_support_set_Embedding(support_set_dataloader):
    
    Supportset_Embeddings=[]
    for step, batch in enumerate(support_set_dataloader):    
        # push the batch to gpu
        batch = [r.to(device) for r in batch]

        sent_id_a, mask_a,labels = batch
        # print(sent_id_a.shape)

        embedding = model(sent_id_a,mask_a)
        Supportset_Embeddings.append([embedding,labels])
        # print(len(embedding))

    return Supportset_Embeddings

#getting the labels and preds from the test dataset

def test_model(Supportset_Embeddings,test_set_dataloader):

    preds=[]

    labels_=[]
     
    for step, batch in enumerate(test_set_dataloader):

        all_similarities_flaky=[]
        
        all_similarities_non_flaky=[]

    # push the batch to gpu
        batch = [r.to(device) for r in batch]

        sent_id,mask,labels = batch

        test_embedding = model(sent_id,mask)
        labels=labels.detach().cpu().numpy()
        labels=labels[0]
        # print('label of this test case',labels)
        
        preds.append(labels)
        for i in Supportset_Embeddings:

            label_ss= i[1].detach().cpu().numpy()
            label_ss=label_ss[0]


            cosi = torch.nn.CosineSimilarity(dim=1)
            
            cosi_sim =  cosi(test_embedding, i[0])

            cosi_sim=cosi_sim.detach().cpu().numpy()

            cosi_sim=cosi_sim[0]

            if label_ss==0.0:
                
                all_similarities_non_flaky.append(cosi_sim)

            else :
                
                all_similarities_flaky.append(cosi_sim)

        non_flaky_mean=statistics.mean(all_similarities_non_flaky)
        flaky_mean=statistics.mean(all_similarities_flaky)


        if flaky_mean>non_flaky_mean:

          labels_.append(1.0)

        else:

          labels_.append(0.0)

    return preds,labels_

def get_evaluation_scores(tn, fp, fn, tp):
    print("get_score method is defined")
    if(tp == 0):
        accuracy = (tp+tn)/(tn+fp+fn+tp)
        Precision = 0
        Recall = 0
        F1 = 0
    else:
        accuracy = (tp+tn)/(tn+fp+fn+tp)
        Precision = tp/(tp+fp)
        Recall = tp/(tp+fn)
        F1 = 2*((Precision*Recall)/(Precision+Recall))
    return accuracy, F1, Precision, Recall

def data_prep(X,Y):
       
      set1=pd.concat([X, Y.to_frame()], axis=1, join='inner')

      #Data prepaeration for Triple Loss Siamese Network: 
      flaky = list(set1[set1['label'] == 1]['flaky_code'])
      non_flaky = list(set1[set1['label'] == 0]['flaky_code'])

      # Creating pairs of data for siamese training => labels for identity loss and class for disaster or non disaster
      dataf = pd.DataFrame(columns=['Anchor', 'Positive', 'Negative', 'label'])

      for data in flaky:
        a = data
        p = random.choice(flaky)
        p=data_augment(p)
        n = random.choice(non_flaky)
        n=data_augment(n)

        dataf.loc[len(dataf)] = [a, p, n, 1]


      for data in non_flaky:
        a = data
        p = random.choice(non_flaky)
        p=data_augment(p)
        n = random.choice(flaky)
        n=data_augment(n)
        
        dataf.loc[len(dataf)] = [a, p, n, 0]

      return dataf[['Anchor', 'Positive', 'Negative']],dataf['label']

#Data Augmentation

def get_test_case_name(code):
    match = re.search(r'public\s+void\s+(\w+)\(', code)
    if match:
        return match.group(1)
    return None

def random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def replace_test_case_name(java_test_case_code):
    test_case_name = get_test_case_name(java_test_case_code)
    if not test_case_name:
        return java_test_case_code
    new_test_case_name = test_case_name + '_' + random_string(5)
    return re.sub(test_case_name, new_test_case_name, java_test_case_code)

def extract_boolean_values(source_code):
    return re.findall(r'\b(true|false)\b', source_code)

def replace_boolean_values(source_code):
    boolean_values = extract_boolean_values(source_code)
    for boolean_value in boolean_values:
        if boolean_value == 'true':
            source_code = source_code.replace('true', 'false')
        elif boolean_value == 'false':
            source_code = source_code.replace('false', 'true')
    return source_code

def extract_numbers_and_strings(source_code):
    numbers = re.findall(r'\b(?!Assert\.)\d+\b', source_code)
    strings = re.findall(r'"(?!Assert\.)(.*?)"', source_code)
    return numbers + strings

def replace_numbers_and_strings(source_code):
    values = extract_numbers_and_strings(source_code)
    for value in values:
        if value.isdigit():
            new_value = str(random.randint(1, 100))
        else:
            new_value = '"' + random_string(5) + '"'
        source_code = source_code.replace(value, new_value)
    return source_code

def data_augment(code):

      new_name=replace_test_case_name(code)
      boole=extract_boolean_values(code)
      new_code=replace_boolean_values(new_name)

      final_code=replace_numbers_and_strings(new_code)

      return final_code

# Load the training and validation loss dictionaries
def plot_curve(train_losses,valid_losses,epoch):
  # Generate a sequence of integers to represent the epoch numbers
  epochs = range(0, epoch)
  
  # Plot and label the training and validation loss values
  plt.plot(epochs, train_losses, label='Training Loss')
  plt.plot(epochs, valid_losses, label='Validation Loss')
  
  # Add in a title and axes labels
  plt.title('Training and Validation Loss')
  plt.xlabel('Epochs')
  plt.ylabel('Loss')
  
  
  # Display the plot
  plt.legend(loc='best')
  plt.show()

execution_time = time.time()
print("Start time of the experiment", execution_time)

skf = StratifiedKFold(n_splits=4,shuffle=True, random_state=56)
TN = FP = FN = TP = 0
fold_number = 0

for train_index, test_index in skf.split(input_data,target_data):
    
    auto_model =AutoModel.from_pretrained(model_name, config=model_config) #this is done to avoid data leakage within each fold for model training
    print(" NOW IN FOLD NUMBER", fold_number)

    X_train, X_test = input_data.iloc[list(train_index)], input_data.iloc[list(test_index)]
    y_train, y_test = target_data.iloc[train_index], target_data.iloc[test_index]
    
    X_train, X_valid, y_train, y_valid=train_test_split(X_train, y_train, random_state=56, test_size=0.3, stratify=y_train)
    
    #reansforming data into triplets for Saimese Network

    X_train,y_train=data_prep( X_train,y_train)
    X_valid,y_valid=data_prep(X_valid,y_valid)
    X_test,y_test=data_prep(X_test,y_test)

    #converting test cases into tokens
    #for train
    train_q1_seq = tokenize_data(X_train['Anchor'])
    train_q2_seq = tokenize_data(X_train['Positive'])
    train_q3_seq = tokenize_data(X_train['Negative'])
    #for validation
    val_q1_seq = tokenize_data(X_valid['Anchor'])
    val_q2_seq = tokenize_data(X_valid['Positive'])
    val_q3_seq = tokenize_data(X_valid['Negative'])
    #for test
    test_q1_seq = tokenize_data(X_test['Anchor'])
    test_q2_seq = tokenize_data(X_test['Positive'])
    test_q3_seq = tokenize_data(X_test['Negative'])

    #Set1 for Anchor
    train_seq_anchor, train_mask_anchor, val_seq_anchor, val_mask_anchor, test_seq_anchor, test_mask_anchor=text_to_tensors(train_q1_seq,val_q1_seq,test_q1_seq)
    #Set2 for positive
    train_seq_pos, train_mask_pos, val_seq_pos, val_mask_pos, test_seq_pos, test_mask_pos=text_to_tensors(train_q2_seq,val_q2_seq,test_q2_seq)
    #Set3 for negative
    train_seq_neg, train_mask_neg, val_seq_neg, val_mask_neg, test_seq_neg, test_mask_neg=text_to_tensors(train_q3_seq,val_q3_seq,test_q3_seq)
        
    # converting labels of train, validation and test into tensors
    Y_train=np.asarray(y_train).astype('float32')
    train_y = torch.tensor(Y_train)
    Y_val=np.asarray(y_valid).astype('float32')
    val_y = torch.tensor(Y_val)
    Y_test=np.asarray(y_test).astype('float32')
    test_y = torch.tensor(Y_test)

    #create dataloaders
    train_dataloader=create_dataloaders(train_seq_anchor,train_mask_anchor,train_seq_pos,train_mask_pos, train_seq_neg,train_mask_neg,train_y)
    val_dataloader=create_dataloaders(val_seq_anchor,val_mask_anchor,val_seq_pos,val_mask_pos, val_seq_neg,val_mask_neg,val_y)
    test_set_dataloader=test_dataloaders(test_seq_anchor,test_mask_anchor, test_y)


    # compute the class weights
    from sklearn.utils import class_weight
    class_weights= class_weight.compute_class_weight(class_weight='balanced', classes= np.unique(train_y.values), y=np.ravel(train_y.values))
    # converting list of class weights to a tensor
    weights = torch.tensor(class_weights, dtype=torch.float)

    # push weights to GPU

    weights = weights.to(device)

    print("Class Weights:", class_weights)


    model = BERT_Arch(auto_model)

    # push the model to GPU
    model = model.to(device)


    epochs = 10

    #call the early stopping class

    early_stopping = EarlyStopping(tolerance=3, min_delta=0.02)


    # define the optimizer
    optimizer = AdamW(model.parameters(), lr=1e-5)

    #criterion = torch.jit.script(TripletLoss())
    
    gc.collect()

    torch.cuda.empty_cache()

    # set initial loss to infinite
    best_valid_loss = float('inf')

    # empty lists to store training and validation loss of each epoch
    train_losses = []
    valid_losses = []

      # for each epoch
    for epoch in range(epochs):

          print('\n Epoch {:} / {:}'.format(epoch + 1, epochs))

          # train the model and calculate the train loss
          train_loss = train(train_dataloader)
          train_losses.append(train_loss)

          with torch.no_grad(): 
          # evaluate the model and calculate the validation loss
                  valid_loss = evaluate_(val_dataloader)
                  valid_losses.append(valid_loss)
          
          epoch=epoch + 1   
          early_stopping(train_loss, valid_loss)

          if early_stopping.early_stop or epoch==10:

            print("We are early stopping at epoch:", epoch)
              # save the best model
            torch.save(model.state_dict(), 'Model.pt')
            
            print(f'\nTraining Loss Final : {train_loss:.3f}')
            print(f'Validation Loss Final : {valid_loss:.3f}')
            break


    # load weights of best model
    model.load_state_dict(torch.load('Model.pt'))

    support_set_dataloader=create_support_set(X_train,y_train)

    support_set_Embedding=create_support_set_Embedding(support_set_dataloader)

    with torch.no_grad(): 
      preds,labels= test_model(support_set_Embedding,test_set_dataloader)

     
    print(classification_report(preds, labels))

    tn, fp, fn, tp = confusion_matrix(preds, labels, labels=[0, 1]).ravel()

    TN = TN + tn
    FP = FP + fp
    FN = FN + fn
    TP = TP + tp

    #clearing catche and deleting the model to free the memory

    torch.cuda.empty_cache()
    gc.collect()
    del model
    fold_number=fold_number+1

    print(tn, fp, fn, tp,"tn, fp, fn, tp")
    print("This fold is completed in : (%s) seconds. " % round((time.time() - execution_time), 5))
    plot_curve(train_losses,valid_losses,epoch)

#get final results from all folds:

accuracy, F1, Precision, Recall = get_evaluation_scores(TN,FP,FN,TP)

print('accuracy, F1, Precision, Recall',accuracy, F1, Precision, Recall)
print('TN,FP,FN,TP',TN,FP,FN,TP)
print("This overall experiment is completed in : (%s) seconds. " % round((time.time() - execution_time), 5))