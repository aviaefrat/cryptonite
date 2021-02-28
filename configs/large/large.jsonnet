local config = import "../shared.jsonnet";

config {
    "dataset_reader"+: {
        "hf_pretrained_tokenizer": "t5-large"
    },
    "model"+: {
        "hf_pretrained_model": "t5-large"
    },
    "data_loader"+: {
        "batch_sampler"+: {
            "max_tokens": 7000
        }
    }
}
