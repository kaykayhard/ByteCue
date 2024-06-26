# ByteCue: One Step Further Than Decompilation: Bytecode Comment Generation

This is the source code and dataset for ByteCue. The dataset is saved in the ```datawash/data``` folder.

## Quick start
If you want to train your own dataset, start with the step1, otherwise skip the step1.
### Step1: data preprocess
> + please place the bytecode, cfg and comment files under data folder with the following names:<br>
>-train_story.txt <br>
>-train_summ.txt <br>
-train_cfg.txt <br>
-train_api_pair.txt <br>
-eval_story.txt <br>
-eval_summ.txt <br>
-eval_cfg.txt <br>
-eval_api_pair.txt <br>
-test_story.txt <br>
-test_summ.txt <br>
-test_cfg.txt <br>
-test_api_pair.txt <br>
> each story and summary must be in a single line (see sample text given.)
>
> + Run the preprocess.py <br>
Command: ```python preprocess.py```<br>
This will creates three tfrecord files under the datawash folder.

### Step2: train the model
> run the main.py <br>
Command: ```python main.py``` <br>
Configurations for the model can be changes from config.py file

### Step3: generate comments and test your trained model
> + Firstly, generate comments for the test set <br>
> run the generateCOMMENT.py <br>
> Command: ```python generateCOMMENT.py```
> + Then, evaluate the generated comments<br>
> run the evaluation.py <br>
> Command: ```python evaluation.py```