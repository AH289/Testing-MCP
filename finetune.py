import json
import torch
import transformers
seed = 42
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
transformers.logging.set_verbosity_error()
print('before importing')
torch.set_float32_matmul_precision('high')
from transformers import (Trainer, TrainingArguments, AutoTokenizer,
                           Gemma2ForSequenceClassification)


from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
from collections import Counter

def main():
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)

        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')

        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall,
        }

    print('before loading')
    # Load the dataset
    with open('/mnt/share/Hashish/PI_input/data_sets/dataset_3.22_binary.json', 'r', encoding="utf-8") as file:
        data = json.load(file)

    print(data[0])

    # Extract the 'type' field to use for stratification
    types = [item["risk type"] for item in data]

    # Perform a stratified train/test split based on the 'type'
    train_data, val_data = train_test_split(
        data, 
        test_size=0.1,
        random_state=42, 
        shuffle=True, 
        stratify=types  # Stratify based on the 'type' field
    )

    # Count the occurrences of each type in the entire dataset, train, and validation sets
    total_type_count = Counter(types)
    train_type_count = Counter([item["risk type"] for item in train_data])
    val_type_count = Counter([item["risk type"] for item in val_data])

    # Display the counts
    print("Total count of each type in the entire dataset:")
    print(total_type_count)

    print("\nCount of each type in the training set:")
    print(train_type_count)

    print("\nCount of each type in the validation set:")
    print(val_type_count)


    # Define a custom dataset class
    class CustomDataset(torch.utils.data.Dataset):
        def __init__(self, data, tokenizer):
            self.data = data
            self.tokenizer = tokenizer
        def __len__(self):
            return len(self.data)
        def __getitem__(self, idx):
            item = self.data[idx]
            inputs = tokenizer(f"""<start_of_turn>user\n{item['text']}<end_of_turn>\n<start_of_turn>model\n""", return_tensors="pt", return_attention_mask=True, padding='longest', truncation=True, max_length=4096)
            inputs = {key: val.squeeze() for key, val in inputs.items()}
            inputs['labels'] = torch.tensor(item['label'], dtype=torch.long)
            return inputs

    print('before loading')
    model_dir = "/mnt/share/Hashish/PI_input/models_directory"

    model = Gemma2ForSequenceClassification.from_pretrained(
        pretrained_model_name_or_path="/mnt/share/Hashish/PI_input/results/ex_15_cot/final_model_sft_merged",
        trust_remote_code=True,
        attn_implementation="eager",
        torch_dtype=torch.bfloat16,
        num_labels=2,
        cache_dir=model_dir
    )

    tokenizer = AutoTokenizer.from_pretrained("/mnt/share/Hashish/PI_input/results/ex_15_cot/final_model_sft_merged", trust_remote_code=True, cache_dir=model_dir)

    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.eos_token_id
    # tokenizer.padding_side = 'right'
    print(tokenizer.padding_side)

    # Create the custom datasets
    train_dataset = CustomDataset(train_data, tokenizer)
    val_dataset = CustomDataset(val_data, tokenizer)

    # Comment these two blocks for full parameter tuning
    for param in model.parameters():
        param.requires_grad = False  # Initially freeze all parameters

    for l in model.named_modules():
        if 'final' in l[0] or 'score' in l[0]:
            print("a"*200)
            print(l)
            print("a"*200)
            for param in l[1].parameters():
                param.requires_grad = True

    # Verify which parameters are now trainable
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(f"Trainable parameter: {name} and number:", param.size())

    print("r"*200)
    print(model)
    print("r"*200)
    # Define the training arguments, use accuracy for evaluation
    training_args = TrainingArguments(
        output_dir='/mnt/share/Hashish/PI_input/results/ex_15_binary/',
        num_train_epochs=4,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=8,
        warmup_steps=50,
        learning_rate=1e-4,
        logging_dir='./logs',
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
    )

    # Initialize the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # Fine-tune the model
    trainer.train()

    lm_head_state_dict = model.score.state_dict()
    torch.save(lm_head_state_dict, "binary_lm_head_state_dict.pth")

if __name__ == '__main__':
    main()
