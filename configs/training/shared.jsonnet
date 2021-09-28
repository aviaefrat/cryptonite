{
    "train_data_path": error "Must override train_data_path",
    "validation_data_path": error "Must override validation_data_path",
    "dataset_reader": {
        "type": "cryptic-crossword",
        "hf_pretrained_tokenizer": "t5-large"
    },
    "model": {
        "type": "cryptic-crossword",
        "hf_pretrained_model": "t5-large"
    },
    "data_loader": {
        "batch_sampler": {
            "type": "max_tokens_sampler",
            "max_tokens": 7000
        }
    },
    "trainer": {
        "num_epochs": 100,
        "optimizer": {
            "type": "adafactor",
            "lr": 0.001,               # From https://arxiv.org/pdf/1910.10683.pdf#page=9
            "scale_parameter": false,  #  "We use a constant learning rate of 0.001 when fine-tuning"
            "relative_step": false     #  also see https://github.com/pytorch/fairseq/blob/master/fairseq/optim/adafactor.py#L74
        }
        "validation_metric": "+t5_tokenizer_em",
        "cuda_device": 0,
        "patience": 10,
        "checkpointer": {
            "num_serialized_models_to_keep": 1
        }
    }
}
