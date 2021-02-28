{  # todo PyCharm treats libsonnet as plain text, so we're keeping this file as .jsonnet for now
    "train_data_path": error "Must override train_data_path",
    "validation_data_path": error "Must override validation_data_path",
    "dataset_reader": {
        "type": "cryptic-crossword",
        "hf_pretrained_tokenizer": error "Must override dataset_reader.hf_pretrained_tokenizer"
    },
    "model": {
        "type": "cryptic-crossword",
        "hf_pretrained_model": error "Must override model.hf_pretrained_model"
    },
    "data_loader": {
        "batch_sampler": {
            "type": "max_tokens_sampler",
            "max_tokens": error "Must override data_loader.batch_sampler.batch_size"
        }
    },
    "trainer": {
        "num_epochs": 100,
        "optimizer": error "Must override trainer.optimizer",
        "validation_metric": "+t5_tokenizer_em",
        "cuda_device": 0,
        "patience": 10,
        "checkpointer": {
            "num_serialized_models_to_keep": 1
        }
    }
}
