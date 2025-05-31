

# 🚀 ByteCue: enhancing bytecode comment generation with API information

📘 This repository contains the **source code** and **dataset** for **ByteCue**, a tool for automatic bytecode comment generation.

---

## ⚡ Quick Start

If you plan to train the model using your own dataset, begin with **Step 1**. Otherwise, you may skip it.

---

### 🛠️ Step 1: Data Preprocessing

1. 📂 Place the following input files (`bytecode`, `CFG`, `comments`) under the `data/` folder:

```
- train_story.txt
- train_summ.txt
- train_cfg.txt
- train_api_pair.txt
- eval_story.txt
- eval_summ.txt
- eval_cfg.txt
- eval_api_pair.txt
- test_story.txt
- test_summ.txt
- test_cfg.txt
- test_api_pair.txt
```

> 🔸 **Note:** Each line in the `*_story.txt` and `*_summ.txt` files should represent a single example (see provided samples).

2. ▶️ Run the preprocessing script:

```bash
python preprocess.py
```

📁 This will generate `.tfrecord` files under the `datawash/` directory.

---

### 🧠 Step 2: Train the Model

Train the model by running:

```bash
python main.py
```

⚙️ You can modify training configurations in the `config.py` file.

---

### 💬 Step 3: Generate Comments & Evaluate

1. ✍️ Generate comments for the test set:

```bash
python generateCOMMENT.py
```

2. 📊 Evaluate the generated comments:

```bash
python evaluation.py
```

---

## 📦 Dataset Download

Due to LFS limitations, please download the dataset from:

🔗 [Google Drive – ByteCue Dataset](https://drive.google.com/drive/folders/1z0xh0KOFB8V-9LQmE0BTJyXkUU_t3kYD?usp=sharing)

📦 After extracting the `.zip` file, move the following folders to the **ByteCue root directory**:

```
- datawash/
- scripts/
- texar_repos/
- venv/
- pretrained_model/
```

---

## 📁 Project Structure

```
ByteCue/
│
├── scripts/
│   ├── build_data_with_cfg.py
│   ├── drawCFG.py
│   └── prepare_train_data.py
│
├── texar_repos/
├── datawash/
├── pretrained_model/
├── venv/
│
├── Bytecue.py
├── config.py
├── evaluation.py
├── generateCOMMENT.py
├── main.py
└── preprocess.py
```

---

