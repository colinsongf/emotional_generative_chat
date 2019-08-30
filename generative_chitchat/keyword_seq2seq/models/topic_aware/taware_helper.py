#!/usr/bin/env python
# coding: utf-8


import tensorflow as tf

from models.model_helper import TrainModel, EvalModel, InferModel
from models.topic_aware import taware_iterators
from models import vocab_utils as vocab


def create_train_model(
        model_class, hparams, scope=None, num_workers=1, jobid=0,
        extra_args=None):
    """Create train graph, model, and iterator."""
    train_file = hparams.train_data

    graph = tf.Graph()

    with graph.as_default(), tf.container(scope or "train"):
        vocab_table = vocab.create_vocab_table(hparams.vocab_file)

        dataset = tf.data.TextLineDataset(train_file)
        skip_count_placeholder = tf.placeholder(shape=(), dtype=tf.int64)

        iterator = taware_iterators.get_iterator(
            dataset,
            vocab_table,
            batch_size=hparams.batch_size,
            num_buckets=hparams.num_buckets,
            topic_words_per_utterance=hparams.topic_words_per_utterance,
            src_max_len=hparams.src_max_len,
            tgt_max_len=hparams.tgt_max_len,
            skip_count=skip_count_placeholder,
            num_shards=num_workers,
            shard_index=jobid)

        model = model_class(
                mode=tf.contrib.learn.ModeKeys.TRAIN,
                iterator=iterator,
                params=hparams,
                scope=scope)

    return TrainModel(
        graph=graph,
        model=model,
        iterator=iterator,
        skip_count_placeholder=skip_count_placeholder)


def create_eval_model(model_class, hparams, scope=None):
    """Create train graph, model, src/tgt file holders, and iterator."""
    vocab_file = hparams.vocab_file
    graph = tf.Graph()

    with graph.as_default(), tf.container(scope or "eval"):
        vocab_table = vocab.create_vocab_table(vocab_file)
        eval_file_placeholder = tf.placeholder(shape=(), dtype=tf.string)

        eval_dataset = tf.data.TextLineDataset(eval_file_placeholder)
        iterator = taware_iterators.get_iterator(
            eval_dataset,
            vocab_table,
            hparams.batch_size,
            num_buckets=hparams.num_buckets,
            topic_words_per_utterance=hparams.topic_words_per_utterance,
            src_max_len=hparams.src_max_len,
            tgt_max_len=hparams.tgt_max_len)
        model = model_class(
            mode=tf.contrib.learn.ModeKeys.EVAL,
            iterator=iterator,
            params=hparams,
            scope=scope,
            log_trainables=False)
    return EvalModel(
        graph=graph,
        model=model,
        eval_file_placeholder=eval_file_placeholder,
        iterator=iterator)


def create_infer_model(model_class, hparams, scope=None):
    """Create inference model."""
    graph = tf.Graph()
    vocab_file = hparams.vocab_file

    with graph.as_default(), tf.container(scope or "infer"):
        vocab_table = vocab.create_vocab_table(vocab_file)
        reverse_vocab_table = vocab.create_rev_vocab_table(vocab_file)

        src_placeholder = tf.placeholder(shape=[None], dtype=tf.string)
        batch_size_placeholder = tf.placeholder(shape=[], dtype=tf.int64)

        src_dataset = tf.data.Dataset.from_tensor_slices(
            src_placeholder)
        iterator = taware_iterators.get_infer_iterator(
            src_dataset,
            vocab_table,
            batch_size=batch_size_placeholder,
            topic_words_per_utterance=hparams.topic_words_per_utterance,
            src_max_len=hparams.src_max_len)
        model = model_class(
            mode=tf.contrib.learn.ModeKeys.INFER,
            iterator=iterator,
            params=hparams,
            rev_vocab_table=reverse_vocab_table,
            scope=scope,
            log_trainables=False)
    return InferModel(
        graph=graph,
        model=model,
        src_placeholder=src_placeholder,
        batch_size_placeholder=batch_size_placeholder,
        iterator=iterator)

