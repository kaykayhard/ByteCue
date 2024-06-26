#!/usr/bin/env python
import sys

if not 'texar_repo' in sys.path:
    sys.path += ['texar_repo']

from config import *
from preprocess import file_based_input_fn_builder
import os
import csv
import collections
from texar_repo.examples.bert.utils import data_utils, model_utils, tokenization
import importlib
import tensorflow as tf
import texar as tx
from texar_repo.examples.bert import config_classifier as config_downstream
from texar_repo.texar.utils import transformer_utils
from texar_repo.examples.transformer.utils import data_utils, utils
from texar_repo.examples.transformer.bleu_tool import bleu_wrapper

train_dataset = file_based_input_fn_builder(
    input_file=train_out_file,
    max_seq_length_src=max_seq_length_src,
    max_seq_length_cfg=max_seq_length_cfg,
    max_seq_length_tgt=max_seq_length_tgt,
    max_seq_length_api=max_seq_length_api,
    is_training=True,
    drop_remainder=True,
    is_distributed=is_distributed)({'batch_size': batch_size})

eval_dataset = file_based_input_fn_builder(
    input_file=eval_out_file,
    max_seq_length_src=max_seq_length_src,
    max_seq_length_cfg=max_seq_length_cfg,
    max_seq_length_tgt=max_seq_length_tgt,
    max_seq_length_api=max_seq_length_api,
    is_training=False,
    drop_remainder=True,
    is_distributed=is_distributed)({'batch_size': eval_batch_size})

test_dataset = file_based_input_fn_builder(
    input_file=test_out_file,
    max_seq_length_src=max_seq_length_src,
    max_seq_length_cfg=max_seq_length_cfg,
    max_seq_length_tgt=max_seq_length_tgt,
    max_seq_length_api=max_seq_length_api,
    is_training=False,
    drop_remainder=True,
    is_distributed=is_distributed)({'batch_size': test_batch_size})

bert_config = model_utils.transform_bert_to_texar_config(
    os.path.join(bert_pretrain_dir, 'bert_config.json'))

tokenizer = tokenization.FullTokenizer(
    vocab_file=os.path.join(bert_pretrain_dir, 'vocab.txt'),
    do_lower_case=True)

vocab_size = len(tokenizer.vocab)

src_input_ids = tf.placeholder(tf.int64, shape=(None, None))
src_segment_ids = tf.placeholder(tf.int64, shape=(None, None))

tgt_input_ids = tf.placeholder(tf.int64, shape=(None, None))
tgt_segment_ids = tf.placeholder(tf.int64, shape=(None, None))

cfg_input_ids = tf.placeholder(tf.int64, shape=(None, None))
cfg_segment_ids = tf.placeholder(tf.int64, shape=(None, None))

api_input_ids = tf.placeholder(tf.int64, shape=(None, None))
api_segment_ids = tf.placeholder(tf.int64, shape=(None, None))

batch_size = tf.shape(src_input_ids)[0]

src_input_length = tf.reduce_sum(1 - tf.to_int32(tf.equal(src_input_ids, 0)), axis=1)
tgt_input_length = tf.reduce_sum(1 - tf.to_int32(tf.equal(tgt_input_ids, 0)), axis=1)
cfg_input_length = tf.reduce_sum(1 - tf.to_int32(tf.equal(cfg_input_ids, 0)), axis=1)

api_input_length = tf.reduce_sum(1 - tf.to_int32(tf.equal(api_input_ids, 0)), axis=1)


labels = tf.placeholder(tf.int64, shape=(None, None))
is_target = tf.to_float(tf.not_equal(labels, 0))

global_step = tf.Variable(0, dtype=tf.int64, trainable=False)

learning_rate = tf.placeholder(tf.float64, shape=(), name='lr')

iterator = tx.data.FeedableDataIterator({'train': train_dataset, 'eval': eval_dataset, 'test': test_dataset})

batch = iterator.get_next()

# ##################################################### GRU ######################################################
# flags = tf.flags
# flags.DEFINE_string("config_model", "config_model", "The model config.")
#
# FLAGS = flags.FLAGS
#
# config_model = importlib.import_module(FLAGS.config_model)

print("Intializing the GRU Encoder")
with tf.variable_scope('gru'):
    print("Intializing the CFG Encoder")
    # The word embedding is performed first, and the dimension parameters are consistent with bert's
    embedder = tx.modules.WordEmbedder(
        vocab_size=bert_config.vocab_size,
        hparams=bert_config.embed)
    word_embeds = embedder(cfg_input_ids)

    # Creates segment embeddings for each type of tokens.
    segment_embedder = tx.modules.WordEmbedder(
        vocab_size=bert_config.type_vocab_size,
        hparams=bert_config.segment_embed)
    segment_embeds = segment_embedder(cfg_segment_ids)

    # Finally generate the embedding vector
    input_embeds = word_embeds + segment_embeds
    gru_cells = [tf.nn.rnn_cell.GRUCell(num_units=768) for layer in range(2)]
    multi_cell = tf.nn.rnn_cell.MultiRNNCell(gru_cells)
    CFG_gruoutputs, states = tf.nn.dynamic_rnn(multi_cell, input_embeds, dtype=tf.float32)

# ########################################## encoder api model ######################################################
    print("Intializing the GRU Encoder api")
    # The word embedding is performed first, and the dimension parameters are consistent with bert's
    api_embedder = tx.modules.WordEmbedder(
        vocab_size=bert_config.vocab_size,
        hparams=bert_config.embed)

    api_word_embeds = api_embedder(api_input_ids)
    # Creates segment embeddings for each type of tokens.
    api_segment_embedder = tx.modules.WordEmbedder(
        vocab_size=bert_config.type_vocab_size,
        hparams=bert_config.segment_embed)

    # The word embedding is performed first, and the dimension parameters are consistent with bert's


    # Creates segment embeddings for each type of tokens.

    api_segment_embeds = api_segment_embedder(api_segment_ids)

    # Finally generate the embedding vector
    api_input_embeds = api_word_embeds + api_segment_embeds
    API_gruoutputs, api_states = tf.nn.dynamic_rnn(multi_cell, api_input_embeds, dtype=tf.float32)




# ########################################## encoder Bert model ######################################################
print("Intializing the Bert Encoder Graph")
with tf.variable_scope('bert'):
    # first word embedding
    embedder = tx.modules.WordEmbedder(
        vocab_size=bert_config.vocab_size,
        hparams=bert_config.embed)
    word_embeds = embedder(src_input_ids)

    # Creates segment embeddings for each type of tokens.
    segment_embedder = tx.modules.WordEmbedder(
        vocab_size=bert_config.type_vocab_size,
        hparams=bert_config.segment_embed)
    segment_embeds = segment_embedder(src_segment_ids)

    # Finally generate the embedding vector
    input_embeds = word_embeds + segment_embeds

    # Build the Bert model (a TransformerEncoder)
    
    encoder = tx.modules.TransformerEncoder(hparams=bert_config.encoder)
    encoder_output = encoder(input_embeds, src_input_length)

    # Build layers for downstream classification
    with tf.variable_scope("pooler"):
        # Uses the projection of the 1st-step hidden vector of BERT output as the representation of the sentence
        bert_sent_hidden = tf.squeeze(encoder_output[:, 0:1, :], axis=1)
        # Add a fully connected layer to adjust the dimension
        bert_sent_output = tf.layers.dense(bert_sent_hidden, config_downstream.hidden_dim, activation=tf.tanh)
        # then dropout
        output = tf.layers.dropout(bert_sent_output, rate=0.1, training=tx.global_mode_train())

# Loads pretrained BERT model parameters
print("loading the bert pretrained weights")
init_checkpoint = os.path.join(bert_pretrain_dir, 'bert_model.ckpt')
model_utils.init_bert_checkpoint(init_checkpoint)
####################################################################################################################


# 输出结果在这里拼接
# encoder_output =  CFG_gruoutputs+encoder_output

# print("API_gruoutputs",tf.shape(API_gruoutputs))
# print("API_gruoutputs",tf.shape(API_gruoutputs))
# print("CFG_gru_outputs",tf.shape(CFG_gruoutputs))
# print("encoder_output",tf.shape(encoder_output))
# encoder_output = API_gruoutputs + CFG_gruoutputs + encoder_output
# print("encoder_output2",tf.shape(encoder_output))
# print(API_gruoutputs.sh)

def add_and_keep_larger_elements(vector1, vector2):
    # 将两个向量相加
    result = tf.add(vector1, vector2)
    
    # 仅保留较大的元素
    result = tf.maximum(vector1, vector2)
    
    return result


print("API_gruoutputs", API_gruoutputs) 
print("API_gruoutputs", API_gruoutputs) 
print("CFG_gru_outputs",CFG_gruoutputs)
print("encoder_output",encoder_output)

# 拼接的做法
# encoder_output = API_gruoutputs + CFG_gruoutputs + encoder_output 

# 保留最大值的做法
# encoder_output =add_and_keep_larger_elements(add_and_keep_larger_elements(API_gruoutputs, CFG_gruoutputs),encoder_output)

# 取平均值的做法
encoder_output = API_gruoutputs + CFG_gruoutputs + encoder_output 
encoder_output = encoder_output / 3

print("encoder_output2",encoder_output)



# ######################################### decoder ############################################################
tgt_embedding = tf.concat([tf.zeros(shape=[1, embedder.dim]), embedder.embedding[1:, :]], axis=0)

decoder = tx.modules.TransformerDecoder(embedding=tgt_embedding, hparams=dcoder_config)
# For training
outputs = decoder(
    memory=encoder_output,
    memory_sequence_length=src_input_length,
    inputs=embedder(tgt_input_ids),
    sequence_length=tgt_input_length,
    decoding_strategy='train_greedy',
    mode=tf.estimator.ModeKeys.TRAIN
)

mle_loss = transformer_utils.smoothing_cross_entropy(outputs.logits, labels, vocab_size, loss_label_confidence)
mle_loss = tf.reduce_sum(mle_loss * is_target) / tf.reduce_sum(is_target)

tvars = tf.trainable_variables()

non_bert_vars = [var for var in tvars if 'bert' not in var.name]

train_op = tx.core.get_train_op(
    mle_loss,
    learning_rate=learning_rate,
    variables=non_bert_vars,
    global_step=global_step,
    hparams=opt)

tf.summary.scalar('lr', learning_rate)
tf.summary.scalar('mle_loss', mle_loss)
summary_merged = tf.summary.merge_all()

saver = tf.train.Saver(max_to_keep=5)
best_results = {'score': 0, 'epoch': -1}

start_tokens = tf.fill([tx.utils.get_batch_size(src_input_ids)],
                       bos_token_id)
predictions = decoder(
    memory=encoder_output,
    memory_sequence_length=src_input_length,
    decoding_strategy='infer_greedy',
    beam_width=beam_width,
    alpha=alpha,
    start_tokens=start_tokens,
    end_token=eos_token_id,
    max_decoding_length=400,
    mode=tf.estimator.ModeKeys.PREDICT
)
if beam_width <= 1:
    inferred_ids = predictions[0].sample_id
else:
    # Uses the best sample by beam search
    inferred_ids = predictions['sample_id'][:, :, 0]
