import time
import sys
import gc
import pandas as pd
import numpy as np
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import AdamW, AutoTokenizer, AutoModel, AutoConfig, RobertaTokenizer, T5ForConditionalGeneration
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import train_test_split

# defining CodeBERT model
model_name = 'microsoft/unixcoder-base'
# uncomment below to use CodeBERT model
# model_name = "microsoft/codebert-base"
model_config = AutoConfig.from_pretrained(model_name, return_dict=False, output_hidden_states=True)
tokenizer = AutoTokenizer.from_pretrained(model_name,use_fast=False)
auto_model =AutoModel.from_pretrained('microsoft/unixcoder-base', config=model_config)

# setting the seed for reproducibility
np.random.seed(0)
torch.manual_seed(0)

# specify GPU
device = torch.device("cuda")

dataset_path=sys.argv[1]
df= pd.read_csv(dataset_path)


# balancing the dataset
def sampling(X_train, y_train, X_valid, y_valid):
    oversampling = RandomOverSampler(
        sampling_strategy='minority', random_state=49)
    x_train = X_train.values.reshape(-1, 1)
    y_train = y_train.values.reshape(-1, 1)
    x_val = X_valid.values.reshape(-1, 1)
    y_val = y_valid.values.reshape(-1, 1)

    x_train, y_train = oversampling.fit_resample(x_train, y_train)
    x_val, y_val = oversampling.fit_resample(x_val, y_val)
    x_train = pd.Series(x_train.ravel())
    y_train = pd.Series(y_train.ravel())
    x_val = pd.Series(x_val.ravel())
    y_val = pd.Series(y_val.ravel())

    return x_train, y_train, x_val, y_val

# converting code into tokens and then vector representation
def tokenize_data(train_text, val_text, test_text):

    tokens_train = tokenizer.batch_encode_plus(
        train_text.tolist(),
        max_length=1022, #set this to 510 while using CodeBERT
        
        pad_to_max_length=True,
        truncation=True)

    tokens_val = tokenizer.batch_encode_plus(
        val_text.tolist(),
        max_length=1022, #set this to 510 while using CodeBERT
        pad_to_max_length=True,
        truncation=True)

    tokens_test = tokenizer.batch_encode_plus(
        test_text.tolist(),
        max_length=1022, #set this to 510 while using CodeBERT
        pad_to_max_length=True,
        truncation=True)
    return tokens_train, tokens_val, tokens_test

# converting vector representation to tensors
def text_to_tensors(tokens_train, tokens_val, tokens_test):
    train_seq = torch.tensor(tokens_train['input_ids'])
    train_mask = torch.tensor(tokens_train['attention_mask'])

    val_seq = torch.tensor(tokens_val['input_ids'])
    val_mask = torch.tensor(tokens_val['attention_mask'])

    test_seq = torch.tensor(tokens_test['input_ids'])
    test_mask = torch.tensor(tokens_test['attention_mask'])

    return train_seq, train_mask, val_seq, val_mask, test_seq, test_mask

# setting seed for data_loaders for output reproducibility
def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    numpy.random.seed(worker_seed)
    random.seed(worker_seed)

g = torch.Generator()
g.manual_seed(0)

def data_loaders(train_seq, train_mask, train_y, val_seq, val_mask, val_y):
    # define a batch size
    batch_size = 2

    # wrap tensors
    train_data = TensorDataset(train_seq, train_mask, train_y)

    # sampler for sampling the data during training
    train_sampler = RandomSampler(train_data)

    # dataLoader for train set
    train_dataloader = DataLoader(
        train_data, sampler=train_sampler, batch_size=batch_size, worker_init_fn=seed_worker)

    # wrap tensors
    val_data = TensorDataset(val_seq, val_mask, val_y)

    # sampler for sampling the data during training
    val_sampler = SequentialSampler(val_data)

    # dataLoader for validation set
    val_dataloader = DataLoader(val_data, sampler=val_sampler, batch_size=batch_size, worker_init_fn=seed_worker)

    return train_dataloader, val_dataloader

#setting up the neural network for CodeBERT fine-tuning
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

        # dense layer 2 (Output layer)
        self.fc2 = nn.Linear(512, 2)

        # softmax activation function
        self.softmax = nn.LogSoftmax(dim=-1)


    # define the forward pass
    def forward(self, sent_id, mask):

        # pass the inputs to the model
        cls_hs = self.bert(sent_id, attention_mask=mask)[1]

        fc1_output = self.fc1(cls_hs)

        relu_output = self.relu(fc1_output)

        dropout_output = self.dropout(relu_output)

        # output layer
        fc2_output = self.fc2(dropout_output)

        # apply softmax activation
        final_output = self.softmax(fc2_output)

        return final_output

# training the model
def train():

    model.train()

    total_loss, total_accuracy = 0, 0

    # empty list to save model predictions
    total_preds = []

    # iterate over batches
    for step, batch in enumerate(train_dataloader):

        # progress update after every 50 batches.
        if step % 50 == 0 and not step == 0:
            print('  Batch {:>5,}  of  {:>5,}.'.format(step, len(train_dataloader)))

        # push the batch to gpu
        batch = [r.to(device) for r in batch]

        sent_id, mask, labels = batch

        # clear previously calculated gradients
        model.zero_grad()

        # get model predictions for the current batch
        preds = model(sent_id, mask)

        # compute the loss between actual and predicted values
        loss = cross_entropy(preds, labels)

        # add on to the total loss
        total_loss = total_loss + loss.item()

        # backward pass to calculate the gradients
        loss.backward()

        # clip the the gradients to 1.0. It helps in preventing the exploding gradient problem
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        # update parameters
        optimizer.step()

        # model predictions are stored on GPU. So, push it to CPU
        preds = preds.detach().cpu().numpy()

        # append the model predictions
        total_preds.append(preds)

    # compute the training loss of the epoch
    avg_loss = total_loss / len(train_dataloader)

    # reshape the predictions in form of (number of samples, no. of classes)
    total_preds = np.concatenate(total_preds, axis=0)

    # returns the loss and predictions
    return avg_loss, total_preds

def format_time(time=None, format=None, rebase=True):
    return get_i18n().format_time(time, format, rebase)

def evaluate():

    print("\nEvaluating..")

    # deactivate dropout layers
    model.eval()

    total_loss, total_accuracy = 0, 0

    # empty list to save the model predictions
    total_preds = []

    # iterate over batches
    for step, batch in enumerate(val_dataloader):

        # Progress update every 50 batches.
        if step % 50 == 0 and not step == 0:

            # Calculate elapsed time in minutes.
            # elapsed = format_time(time.time() - t0)

            # Report progress.
            print('  Batch {:>5,}  of  {:>5,}.'.format(
                step, len(val_dataloader)))

        # push the batch to gpu
        batch = [t.to(device) for t in batch]

        sent_id, mask, labels = batch

        # deactivate autograd
        with torch.no_grad():

            # model predictions
            preds = model(sent_id, mask)

            # compute the validation loss between actual and predicted values
            loss = cross_entropy(preds, labels)

            total_loss = total_loss + loss.item()

            preds = preds.detach().cpu().numpy()

            total_preds.append(preds)

    # compute the validation loss of the epoch
    avg_loss = total_loss / len(val_dataloader)

    # reshape the predictions in form of (number of samples, no. of classes)
    total_preds = np.concatenate(total_preds, axis=0)

    return avg_loss, total_preds


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

def give_test_data_in_chunks(x_test):
    tokens_test = tokenizer.batch_encode_plus(
        x_test.tolist(), max_length=500, pad_to_max_length=True, truncation=True)
    test_seq = torch.tensor(tokens_test['input_ids'])
    test_mask = torch.tensor(tokens_test['attention_mask'])
    preds_chunk = model(test_seq.to(device), test_mask.to(device))
    preds_chunk = preds_chunk.detach().cpu().numpy()
    preds = np.argmax(preds_chunk, axis=1)

    return preds

class EarlyStopping:
    def __init__(self, tolerance=5, min_delta=0.005):

        self.tolerance = tolerance
        self.min_delta = min_delta
        self.counter = 0
        self.early_stop = False

    def __call__(self, train_loss, validation_loss):
        if (validation_loss - train_loss) > self.min_delta:
            self.counter +=1
            if self.counter >= self.tolerance:  
                self.early_stop = True

execution_time = time.time()
print("Start time of the experiment", execution_time)
skf = StratifiedKFold(n_splits=4,shuffle=True)
TN = FP = FN = TP = 0
fold_number = 0

for train_index, test_index in skf.split(input_data, target_data):
    auto_model =AutoModel.from_pretrained(model_name, config=model_config) #this is done to avoid data leakage within each fold for model training
    print(" NOW IN FOLD NUMBER", fold_number)
    X_train, X_test = input_data.iloc[list(train_index)], input_data.iloc[list(test_index)]
    y_train, y_test = target_data.iloc[list(train_index)], target_data.iloc[list(test_index)]
    
    X_train, X_valid, y_train, y_valid=train_test_split(X_train, y_train, random_state=49, test_size=0.3, stratify=y_train)
    X_train, y_train, X_valid, y_valid = sampling(
        X_train, y_train, X_valid, y_valid)

    tokens_train, tokens_val, tokens_test = tokenize_data(
        X_train, X_valid, X_test)
    Y_train = pd.DataFrame(y_train)
    y_val = pd.DataFrame(y_valid)
    y_test = pd.DataFrame(y_test)

    Y_train.columns = ['label']
    y_val.columns = ['label']
    y_test.columns = ['label']

    # convert labels of train, validation and test into tensors
    train_y = torch.tensor(Y_train['label'].values)
    val_y = torch.tensor(y_val['label'].values)
    test_y = torch.tensor(y_test['label'].values)

    train_seq, train_mask, val_seq, val_mask, test_seq, test_mask = text_to_tensors(tokens_train, tokens_val, tokens_test)

    # create data_loaders for train and validation dataset
    train_dataloader, val_dataloader = data_loaders(train_seq, train_mask, train_y, val_seq, val_mask, val_y)

    # compute the class weights

    class_weights = compute_class_weight('balanced', classes=np.unique(Y_train.values), y=np.ravel(Y_train.values))
    # convert list of class weights to a tensor
    weights = torch.tensor(class_weights, dtype=torch.float)

    # push to GPU
    weights = weights.to(device)

    # define the loss function
    cross_entropy = nn.NLLLoss(weight=weights)

    epochs =5

    #call the early stopping class

    early_stopping = EarlyStopping(tolerance=3, min_delta=0.005)

    print("Class Weights:", class_weights)

    model = BERT_Arch(auto_model)

    # push the model to GPU
    model = model.to(device)

    # define the optimizer
    optimizer = AdamW(model.parameters(), lr=1e-5)

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

        # train the model
        train_loss, _ = train()
        print('Train Loss',train_loss)
        train_losses.append(train_loss)

        # evaluate the model
        with torch.no_grad(): 
          # evaluate the model and calculate the validation loss
              valid_loss, _ = evaluate()
              print('Valid Loss',valid_loss)
              valid_losses.append(valid_loss)

        early_stopping(train_loss, valid_loss)

        if early_stopping.early_stop or epoch==5:

            print("We are early stopping at epoch:", epoch)
              # save the best model
            torch.save(model.state_dict(), 'Model.pt')
            
            print(f'\nTraining Loss Final : {train_loss:.3f}')
            print(f'Validation Loss Final : {valid_loss:.3f}')

            break
    
    # load weights of best model
    model.load_state_dict(torch.load('Model.pt'))
    
    with torch.no_grad():
        preds = give_test_data_in_chunks(X_test)

    print(classification_report(test_y, preds))
    tn, fp, fn, tp = confusion_matrix(test_y, preds, labels=[0, 1]).ravel()
    TN = TN + tn
    FP = FP + fp
    FN = FN + fn
    TP = TP + tp

    del model
    torch.cuda.empty_cache()

    fold_number = fold_number+1

accuracy, F1, Precision, Recall = get_evaluation_scores(TN, FP, FN, TP)

#print results:
print('accuracy, F1, Precision, Recall,TN, FP, FN, TP',accuracy, F1, Precision, Recall,TN, FP, FN, TP)