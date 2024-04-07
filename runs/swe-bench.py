import argparse
from tot.methods.bfs import solve
from tot.tasks.swe import SWETask
from datasets import load_dataset
import json
import time

print("Downloading dataset...")
train_dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split = "test", cache_dir='datasets_cache')
preds_path = "preds.jsonl"
try:
    with open(preds_path, "r") as file:
        preds_jsonl = file.read()
except FileNotFoundError:
    preds_jsonl = ""

def update_jsonl(instance_id, model_patch, model_name_or_path, jsonl_object):
    data = [json.loads(line) for line in jsonl_object.splitlines()]

    new_obj = {
        "instance_id": instance_id,
        "model_patch": model_patch,
        "model_name_or_path": model_name_or_path
    }

    data.append(new_obj)
    updated_jsonl = "\n".join([json.dumps(obj) for obj in data])

    return updated_jsonl

def save_jsonl(jsonl_object, file_path="preds.jsonl"):
    with open(file_path, "w") as file:
        file.write(jsonl_object) if jsonl_object.strip() else file.write("")

args = argparse.Namespace(
    backend='mixtral-8x7b-32768',
    temperature=0.2, 
    task='swe', 
    naive_run=False,
    prompt_sample='cot', 
    method_generate='sample', 
    method_evaluate='vote', 
    method_select='greedy', 
    n_generate_sample=1, 
    n_evaluate_sample=3, 
    n_select_sample=5)

print("Solving...")
task = SWETask(train_dataset)

for index in range(110,150):
    ys, infos = solve(args, task, index, to_print=False)
    preds_jsonl = update_jsonl(train_dataset[index]["instance_id"], SWETask.parse_diff_block(ys[0]), args.backend, preds_jsonl)
    save_jsonl(preds_jsonl, preds_path)
    print(f"Solution {index} done.")
    time.sleep(60)